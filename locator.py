## Spawn agent in specific location
### This function needs to be called at the agent instantiation point, before base observations are written in

import random
from random import choice

from typing import List, Dict
from langchain.experimental.generative_agents import (
    GenerativeAgent,
    GenerativeAgentMemory,
)

from langchain import PromptTemplate

def random_spawn_in_location(agents:list, envAreas:dict):
  print("This is working a lil bit")
  locations = {}
  for agent in agents:
    print("LOCATED")
    spawn_area = random.choice(list(envAreas.items()))
    _observation = "{} is in {}".format(agent.name, spawn_area)
    agent.memory.add_memory(_observation)
    locations[agent.name] = spawn_area
  return locations

  #TODO - sync up game time

def _agent_locator(agents:List[GenerativeAgent], envAreas, hour, locations):
  place_ratings = {}

  for agent in agents:
    place_ratings[agent.name] = []
    name = agent.name
    location = locations[name]
    plan = agent.memory.current_plan
    summary = agent.get_summary(force_refresh=True)

    for area in envAreas.items():
      prompt = PromptTemplate(input_variables=["area","plan", "location", "name", "hour"], template= """
      \nContext: Your daily plan is {plan}. Your current location is {location}. The time is {hour}
      \nObservation: You are planning where you will be in the next hour.
      \nAction: Rate each the following area with a number between 1-5, indicating how likely {name} is to be there in the next hour based on your plan for today.
      \nRules: Do not explain or embellish your response in any way.
      \nExample: \n"Area - "Sleep Inn":"A quaint pub and inn. It has a bar on ground level and four bedrooms on the second floor, which can be rented at a nightly rate by asking the receptionist. Serving beer, wine, soft drinks and pub-style food all day." Your rating: 4"
      \nArea - {area} Your rating: """)

      r = agent.chain(prompt).run(area=area, location=location,plan=plan, summary=summary,name=name,hour=hour).strip()
      place_ratings[agent.name].append((area, r))

      place_ratings_sorted = sorted(place_ratings[agent.name],
                                      key=lambda x: x[1]) [::-1]
      chosen_location = place_ratings_sorted[0][0]

      if chosen_location != locations[agent.name]:
          observation = "{} moved to {}".format(agent.name, chosen_location)
          agent.memory.add_memory(observation)
          locations[agent.name] = chosen_location
