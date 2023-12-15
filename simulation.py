### NOTE:
## This code has since been significantly improved.
## This is a demo of what was used in our tests.

import locator
from locator import random_spawn_in_location, _agent_locator
from locator import *

import plans
from plans import all_agents_plan, make_interval_plan
from plans import *

import langchain
from langchain import PromptTemplate
def start_lofi_sim(agents, envAreas, locations):
  #TODO - should locations be a global variable?
  intervals={}
  plan_element={}
  num_agents = len(agents)

  #TODO - fix locations plan to ensure agents wake up in accurate places

  #locations = locator.random_spawn_in_location(agents, envAreas)

  #TODO - update locator function to incorporate plans
  plans.all_agents_plan(agents, locations, envAreas)

  for x in range(5):

    hour = str(800 + (x * 100))
    intervals = {}

    locator._agent_locator(agents, envAreas,hour, locations)

    for agent in agents:
      plan_element[agent.name] = agent.memory.current_plan[x]
      intervals[agent.name] = plans.make_interval_plan(agent, agents, envAreas,locations, plan_element[agent.name])

    vals = list(intervals.values())

    for r in range(4):
      for i in range(num_agents):
        items = vals[i]
        action = items[r]
        print(action)
        a = agents[i]
        a.memory.add_memory(action)

if __name__ == "__main__":
  print(locator.random_spawn_in_location)

