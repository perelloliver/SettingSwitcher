##This has since been significantly improved
##TODO: Update accordingly

import langchain
from langchain import PromptTemplate

morning_plan = """
/nPrompt: Good morning! It's the start of a new day. Let's make a plan for the next 24 hours in broad strokes.

/nInstruction: Make a timed hourly plan for the next 24 hours, relevant to the contextual information provided.

/nRules: Do not explain or discuss the plan in any way after completing it. Do not add any additional information or notes outside of the plan.

Agents must sleep between 7-10 hours for every 24, anytime from 21:00-10:00.

Tasks can last longer than one hour, but you must specify each hour. For example:  '[From 10:00 to 11:00]: Tend to the garden. [From 11:00 to 12:00]: Tend to the garden. [From 12:00 to 13:00] Tend to the garden.'

/nVery important rule: Agents MUST sleep between 7-10 hours for every 24, anytime from 21:00 to 10:00.

/nAbout you: {name}, {status}, {summary}

/nLocations you may include in your plan: {areas}

/nEntities you can include in your plan: {names}

/nYou may not interact with any entity outside of this list, or visit any place not present in the locations map.

/n/n Example: Plan Example - here is Oliver's timed hourly plan for the next 24 hours: [From 7:00 to 8:00]: Morning routine,  [From 8:00 to 9:00]: Commute to university, [From 9:00 to 10:00]: Code at their desk, [From 10:00 to 11:00]: Code at their desk, [From 11:00 to 12:00] Code at their desk, [From 12:00 to 13:00] Code at their desk, [From 13:00 to 14:00]: Take a lunch break, [From 14:00 to 15:00]: Go to the office, [From 15:00 to 16:00]: Join the work meeting, [From 16:00 to 17:00] Work on AI design project, [From 17:00 to 18:00] Work on AI design project, [From 18:00 to 19:00]: Meet up with Alex for drinks and dinner at Joe's Bar, [From 19:00 to 20:00] Spend time with Alex having drinks and dinner at Joe's bar, [From 20:00 to 21:00] Spend time with Alex having drinks and dinner at Joe's bar,  [From 21:00 to 22:00]: Head home and get ready for bed, [From 23:00 to 0:00] Sleep, [From 00:00 to 1:00] Sleep,[From 1:00 to 2:00] Sleep,[From 2:00 to 3:00] Sleep,[From 3:00 to 4:00] Sleep,[From 4:00 to 5:00] Sleep,[From 5:00 to 6:00] Sleep,[From 7:00 to 8:00] Wake up, [From 8:00 to 9:00] Get ready for the day and do morning routine"
"

"""

def make_new_plan(GenerativeAgent, locations, envAreas, agents):
  name = GenerativeAgent.name
  summary = GenerativeAgent.summary
  status = GenerativeAgent.status
  areas = envAreas
  names = [agent.name for agent in agents]


  prompt = PromptTemplate(input_variables=["areas","names","status","summary","name"], template=morning_plan)

  plan = GenerativeAgent.chain(prompt).run(areas=areas, names=names,status=status,summary=summary,name=name)
  #plan = plan.replace('\n',"").strip()
  plan = plan.splitlines()
  GenerativeAgent.memory.current_plan =  plan
  return plan

def all_agents_plan(agents, locations, envAreas):
  plans = {}
  for agent in agents:
    plan = make_new_plan(agent,locations,envAreas, agents)

#remove plan_element input if using outside of simulation loop

def make_interval_plan(agent, agents, envAreas,locations, plan_element):

  #TODO:
  #work on perception - already improved, update

  name = agent.name
  summary = agent.summary
  traits = agent.traits
  status = agent.status
  location = locations[name]

  interval_prompt = """

    ### EXAMPLE ###

    Prompt: Describe subtasks in 15 min increments.
    \n---\n
    Name: Toblen Stonehill
    Summary: A hardworking and responsible innkeeper in the town of Phandalin. He values the safety and well-being of his barmaid, as evidenced by his search for a dagger for her protection. Toblen is curious and imaginative, shown by his contemplation of flying when he sees birds. He has strong social connections within the town, knowing and respecting individuals like Linene Graywind, Daran Edermath, and Qelline Alderleaf. Toblen holds deep respect for Sister Garaele and her spiritual work. He is often found in Phandalin Town Square, where he is well-known and familiar with the town's surroundings. Toblen starts his day early to serve breakfast to patrons at the Stonehill Inn and waits for the barmaid to arrive. He harbors dislike towards Harbin Wester and considers him a foolish politician.
    Traits: Kind, hardworking, sensible, strong, simple minded
    Currently: Running Stonehill Inn
    Location: 'Phandalin Town Square', "Opening hours: 0:00 - 23:59. Centre of the town of Phandalin, a modest and hardworking town built upon ancient ruins. There is a townmaster's hall, a single story building hosting political offices and jail cells. Outside of the hall is a noticeboard with information for newcomers and residents of the town announcing events and offering rewards for certain tasks."

    Current plan:
    [From 9:00 to 10:00]: Open Stonehill Inn and prepare for the day.',
  \n---\n

  Action: In 15 min increments, list the subtasks Toblen Stonehill does during his plan.
  \nOutput:

  1. Toblen Stonehill is going to the cellar to check the ale casks for freshness.
  2. Toblen Stonehill is coming back upstairs to wipe down all the tables with a wet cloth.
  3. Toblen Stonehill is sweeping the floor and checking for any dead rats or litter.
  4. Toblen Stonehill is opening all the windows to let fresh air in, and unlocking the door to his customers.

  ### END OF EXAMPLE ###

  Prompt: Describe subtasks in 15 min increments.
  \n---\n
  Name: {name}
  Summary: {summary}
  Traits: {traits}
  Currently: {status}
  Location: {location}

  Current plan:
  {plan_element}

  \n---\n

  Action: In 15 min increments, list the subtasks {name} does during their plan.
  \nOutput:
  1.
  2.
  3.
  4.

  """

  interval_template = PromptTemplate(input_variables=["name","traits","summary","plan_element","location","status"], template=interval_prompt)

  interval_plan = agent.chain(interval_template).run(name=name,traits=traits,summary=summary,plan_element=plan_element,location=location,status=status)

  interval_plan = interval_plan.splitlines()
  interval_plan = [i[2:].strip() for i in interval_plan]

  if len(interval_plan) > 4:
    interval_plan = [i for i in interval_plan[:4]]

  return interval_plan
