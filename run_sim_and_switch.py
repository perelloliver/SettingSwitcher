
##I'm taking out additional imports. If this causes bugs, OG import list still in OG colab notebook.

#Import modules

import logging
import json
import base64
import datetime
import threading
import openai
import os
import keyword
from itertools import chain
from datetime import datetime
from datetime import timedelta
from langchain.chat_models import ChatOpenAI

from langchain.experimental import GenerativeAgent, GenerativeAgentMemory
from langchain import PromptTemplate

#Import all elements
import misc
import locator
import plans
import simulation
import switcher

###Add filepath to any chosen env data
###Update this for GIT
with open ('environment.json') as f:
  data = json.load(f)

##REMOVE MY API KEY AFTER TESTING!
os.environ["OPENAI_API_KEY"] = "YOUR API KEY HERE"

#Set our LLM
LLM = ChatOpenAI(model_name = "gpt-3.5-turbo-16k-0613",max_tokens=1500)

#Some quick functions to autoload agents into a list, and their memories into a dictionary for uploading
#Make sure agents are stored in a list for any custom runs, even if manually defined, we need a list of agents = [a1, a2, etc]

#Initialize memories
def start_memories(data):
  agent_data = data['agents']
  agents = []
  memories = {}

  for key, value in agent_data.items():
    memory_name = key
    memories[memory_name] = GenerativeAgentMemory(
    llm=LLM,
    memory_retriever=misc.create_new_memory_retriever(),
    verbose=False,
    reflection_threshold=10
    )

  return agents, memories, agent_data

#Initialize agents
def load_agents(agent_data, memories, agents):
  for k, v in agent_data.items():
    new_agent = GenerativeAgent(
        name=v['Name'],
        traits=v['Traits'],
        status=v['Status'],
        memory_retriever=misc.create_new_memory_retriever(),
        llm=LLM,
        memory=memories[k]  # Using the corresponding memory for each agent
    )
    agents.append(new_agent)

  return agents

#Batch load blank agents
def instantiate_agents(data):
  agents, memories, agent_data = start_memories(data)
  load_agents(agent_data, memories, agents)

  return agents, memories

#Instantiate agents and load in memories
agents, memories = instantiate_agents(data)

###Add line to upload memories to agent memory here
#####################

#Load map

envAreas = data['locations']

#Set the start genre
current_genre = "Modern sandbox"

#Set the new genre - should prompt user input
# new_genre = str(input("Choose a new genre:"))
new_genre = str(input("Choose a genre, any genre:"))

#Spawn agents on map
locations = locator.random_spawn_in_location(agents, envAreas)

#Run our simulation for X period - this is low fidelity and cost should match
#Since this work was completed, low-fidelity agent simulations have improved
#Will update in future

simulation.start_lofi_sim(agents, envAreas, locations)

#mark the end of that cycle and check in with our agents
print("END OF START SIMULATION")
print("AGENT CHECKIN")
for agent in agents:
  print(agent.get_summary(force_refresh=True))

print("SETTING SWITCHER INITIALIZING")

#Initiate our genre-switching agent
SettingSwitcher = SettingSwitcher(
    world = envAreas,
    agents = agents,
    current_genre = current_genre,
    new_genre = new_genre,
    llm = LLM,
    memory = SimpleMemory(
      memories = {
    "SURROUNDINGS (game world)": envAreas,
    "YOUR ROLE": "You are the games master of a user-interactive game world.",
    "CONTEXT": f"The user has specified they want to change the game setting to {new_genre}.",
    "PROMPT": "You are working to update every element of this user-interactive game world to be relevant within the new game setting.",
    "YOUR GOALS": f"""
        1. Respond accurately to user input
        2. Update all areas and elements of the game world convincingly, and in line with previous game mechanics.
        3. Do not change object-agent relationships, or agent-agent relationships, which are integral to the simulation dynamics.
        4. Respect and work within genre frameworks and tropes for the chosen setting.
    """,
}
)
)

print(f"FROM {current_genre} to {new_genre}, LET'S GO!")

SettingSwitcher.setting_switch(agents, envAreas, locations)

print("NEW MAP")
print(envAreas)

print("STARTING NEW SIMULATION CYCLE")
simulation.start_lofi_sim(agents, envAreas)

print("AGENT CHECKIN")
for agent in agents:
  print(agent.get_summary(force_refresh=True))
