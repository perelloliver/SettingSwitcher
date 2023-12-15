from pydantic import BaseModel, Field
from langchain.base_language import BaseLanguageModel
from langchain.memory import SimpleMemory


from typing import Any, Dict, List, Optional, Tuple

from langchain.prompts import PromptTemplate
from langchain import LLMChain
import re
from langchain.experimental.generative_agents import (
    GenerativeAgent,
    GenerativeAgentMemory,
)

import locator
import plans
import simulation
import test

class SettingSwitcher(BaseModel):

    llm: BaseLanguageModel

    world: dict

    current_genre: str

    new_genre: str

    verbose: bool = False

    memory: SimpleMemory

    ####Do not initialize with previous_genre, it holds previous genre post-run for heuristic functions
    ####Unless you enjoy chaos. In which case, feel free

    previous_genre: Optional[str] = None

    ###Likewise do not initialize with these, used in agent flow for self.memory updates

    agent_updates = {}

    map_updates = {}


    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def parse_list(text: str) -> List[str]:
        lines = re.split(r"\n", text.strip())
        return [re.sub(r"^\s*\d+\.\s*", "", line).strip() for line in lines]

    def a_silly_test(data):
      test.test(data)

    def chain(self, prompt: PromptTemplate) -> LLMChain:
      #Chain prompt, agent and variables
      #Langchain function
        return LLMChain(
            llm=self.llm, prompt=prompt, verbose=self.verbose,
        )

    def get_rating(self, str) -> str:
      #Pull rating from heuristic function output
        rating = re.sub('[^0-9]', '', str)
        return rating

    def check_score(self, list):
      #Check heuristic ratings are above approval threshold
      for i in list:
        #you can change your threshold here
        if i <= 3:
          return False
      return True

    def remove_empty_strings(self, string: str):
      return string != ""


    def agent_memory_location_update(self, agents):
      #Called at the end of env_only function to make agents aware of changes and update plans, locations

      for agent in agents:

        for area in self.world.items():
            #agent perceives each new map area by name
            m = "{} sees {}".format(agent.name, area)
            agent.memory.add_memory(m)

        #Relocate agents
        agent_locator(agents, envAreas)



    def env_generate(self):


        env_init_prompt = PromptTemplate.from_template("""
        Prompt: You are the games master of a user-interactive world.
        The user has specified they want to change the game setting to {genre}.

        Task: Update each the area of the map to be appropriate for a {genre} game.

        Example:
        ' The user has specified they want to change the game setting from fantasy to dystopian science fiction.
            Input: "Shrine of Luck": "Phandalin's only temple is a small shrine made of stones taken from the nearby ruins. It is dedicated to Tymora, goddess of luck and good fortune."
            Output: "Shrine of Progress": "Phandalin's only sanctuary dedicated to the pursuit of scientific advancement. It houses an interactive museum that showcases the evolution of technology and serves as a meeting place for engineers and innovators." '


        When updating the map, remove genre-specific mentions that do not make sense in a {genre} setting.

        Input - Area of the map:
        {area}

        Output - Updated area:

        """
        )

        output = []
        holding_space = {}

        for area in self.world.items():
            new_env = self.chain(env_init_prompt).run(genre= self.new_genre, area=area).strip()
            output.append(new_env)

        formatted_output = [string.replace("(","").replace(")","").replace('\\',"'").replace('"',"").replace("'","") for string in output]

        holding_space = dict(s.split(',',maxsplit=1) for s in formatted_output)

        return holding_space


    def env_heuristic(self, holding_space):
        #Chain heuristic prompt with world and holding_space, old_genre and new_genre
        #Hold output in variable

        old_genre = self.current_genre

        genre = self.new_genre

        eval_scores = []

        env_heuristic_prompt = PromptTemplate.from_template("""Prompt:
        Observation: You are evaluating a mid-genre game change by the games master of a user-interactive world.
        Compare the initial area description, written for the previous genre, {old_genre}, and the new area description, written for {new_genre}.

        old area for {old_genre}:
        {area}

        new area for {new_genre}:
        {new_area}

        Action: Compare the old and new environment maps and answer with a rating between 1-5, 1 being least accurate and 5 being very accurate.
        Do not provide any explanation or further content outside of your numeric rating.

        Question One: Observing high-level qualities (trope-aligned location traits, rough description, and overarching environmental descriptions) how accurate (similar) is the new map?

        Question Two: Observing the content of the new map, how effective has the games master been in cleaning {old_genre} specific language tropes?

        Question Three: Analyzing the new map, how effective has the games master been in writing-in {new_genre} specific content and tropes?

        Output:
            Question One:
            Question Two:
            Question Three:

        """
        )

        for (k1, v1), (k2,v2) in zip(self.world.items(), holding_space.items()):
          area = (k1,v1)
          new_area = (k2,v2)

          eval_score = self.chain(env_heuristic_prompt).run(old_genre=old_genre, new_genre=new_genre, area=area, new_area=new_area).strip()
          rating = self.parse_list(eval_score)

          ratings = [re.findall(r'\d+', r) for r in rating]
          ratings = list(filter(None, ratings))

          list_app = [k1,k2,ratings]
          eval_scores.append(list_app)

        return eval_scores


    def env_update(self, envAreas):

      #envAreas = game map variable

      new_envAreas = {}
      _Retry = {}

      keys = []
      values = []

      retry_keys = []
      retry_values = []

      holding_space = self.env_generate()

      eval_scores = self.env_heuristic(holding_space)

      for score_set in eval_scores:
        _formatted_ratings = list(score_set[2])
        _formatted_ratings = list(chain.from_iterable(_formatted_ratings))
        _formatted_ratings = [int(i) for i in _formatted_ratings]

        self.check_score(_formatted_ratings)


        if True:

              key = str(score_set[1])
              val = (holding_space[key])
              keys.append(key)
              values.append(val)


        if False:
            retry_key = str(score_set[0])
            retry_val = (envAreas[retry_key])
            retry_keys.append(retry_key)
            retry_values.append(retry_val)


      new_envAreas = dict(zip(keys, values))
      _Retry = dict(zip(retry_keys, retry_values))

      if bool(_Retry) == False:

        previous_env_archive = {k:v for k, v in envAreas.items()}
        old_keys = list(previous_env_archive.keys())

        envAreas.clear()

        envAreas.update(new_envAreas)

        envAreas = {k:v.strip() for k,v in envAreas.items()}
        new_keys = list(envAreas.keys())


        ##Pulling old place names and new place names to concatenate into agent memory post-env switch
        #So that the agent consistently has a memory of the setting switch

        memory_dict = dict(zip(old_keys, new_keys))
        memory_updates = []

        for k,v in memory_dict.items():
          val = k + " is now called " + v + "./n" + "Refer to " + v + " wherever " + k + " is relevant."
          print(val)
          memory_updates.append(val)

        self.memory.memories["UPDATED MAP AREAS"] = [memory_updates]

        self.world = envAreas
        self.previous_genre = str(self.current_genre)
        self.current_genre = str(self.new_genre)
        self.new_genre = ""

      if bool(_Retry) == True:

        self.world = _Retry
        self.env_only_switch()
        ##TODO - What if heuristic continuously fails? Add break to user input

    ####Agent Focused Setting Switching#####

    def load_memories(self, agent):
      #Fetch memories from an agent. Can be run iteratively. Returns langchain documents with page_content and metadata
        memories = agent.memory.memory_retriever.memory_stream
        return memories

    def memories_to_list(self, memories):
        #Parses memory documents into list of strings
        for memory in memories:
            y = []
            x = memory.page_content
            y.append(x)
        return y

    def show_memories(self, agent):
      memories = self.load_memories(agent)
      parsed = self.memories_to_list(memories)

      return parsed

    #self holding dictionary for agent profiles from previous genre

    original_agent_profiles = {}

    def _update_profile(self, agents):
      #Update agent name, traits, and status with relevance to new genre and map
      profile_updates = {}

      prompt = PromptTemplate.from_template("""
      Observation: You are the games master of a user-interactive world. The user has specified they want to change the genre from {current_genre} to {new_genre}.
      \nTask: Update each character name, status, and traits to be appropriate for a {new_genre} game. Be creative and remove any {current_genre} specific tropes or qualities.
      \n
      \nExample:
      \n"Input:
      Character name:
      Alistair Graywind
      Character status:
      Working at Lionshead Coster
      Character traits:
      Hardworking, resilient, mathematically minded.

      Output:
      Updated name: Marshall Graywind
      Updated status: Working at Space Cowboy's Coster.
      Character traits: Hardworking, resilient, retired hacker, science worshipper.
      "
      \nContext: The game map has already been updated. This is the new world map, featuring all areas that may be relevant to the characters. You can only use locations from the map provided. Do not use any locations or place names that are not on this map.
      \nNew world map: {world}.

      \nInput:
      Character name:
      {name}
      Character status:
      {status}
      Character traits:
      {traits}

      \nOutput:
      Updated name:
      Updated status:
      Updated traits:

      """)

      for agent in agents:

        name = agent.name
        status = agent.status
        traits = agent.traits
        current_genre = self.previous_genre
        new_genre = self.new_genre
        world = self.world

        output = self.chain(prompt).run(current_genre=current_genre, new_genre=new_genre,world=world,name=name,status=status,traits=traits ).strip()
        #print(output)
        profile_updates[name] = output
        self.original_agent_profiles[name] = [name, status, traits]

      print(profile_updates)
      return profile_updates

      #I think I don't want a tuple dict return, I want two seperate dicts

    def profile_heuristic(self, agents):
      #This is the function that actually runs _update_profile, to embed within update_profile as 'outputs'
      #heuristic for self evaluation via score
      #If scores too low then run function again up to 2X

      #We're working with self.original_agent_profiles and 'new_profiles' which is where we'll run _update_profile
      #Input of 'agents' is required across functions and an input param in main func already

      old_genre = self.previous_genre

      genre = self.new_genre

      eval_scores = []

      new_profiles = self._update_profile(agents)
      original_profiles = self.original_agent_profiles

      print("ORIGINAL", original_profiles)

      print("NEW", new_profiles)

      profile_heuristic_prompt = PromptTemplate.from_template("""Prompt:
        \nObservation: You are evaluating a mid-genre game change by the games master of a user-interactive world. The games master is currently updating character profiles.
        \nPrompt:Compare the initial character profile, written for the previous genre, {old_genre}, and the new character profile, written for {new_genre}.

        \nold character profile for {old_genre}:
        {old_profile}

        \nupdated character profile for {new_genre}:
        {new_profile}

        \nAction: Compare the old and updated character profiles and answer with a rating between 1-5, 1 being least accurate and 5 being very accurate.
        Do not provide any explanation or further content outside of your numeric rating.

        \nQuestion One: Observing high-level qualities (name structure, character role (i.e Priestess, Inn owner, etc), personality traits) how accurate (similar) is the updated character profile?

        \nQuestion Two: Observing the content of the new profile, how effective has the games master been in cleaning {old_genre} specific language tropes?

        \nQuestion Three: Analyzing the new profile, how effective has the games master been in writing-in {new_genre} specific content and tropes?

        \nOutput:
            \nQuestion One:
            \nQuestion Two:
            \nQuestion Three:

        """
      )

      agent_count = 0

      for (k1,v1), (k2,v2) in zip(original_profiles.items(), new_profiles.items()):

        #debugging function so we can see which agent has an issue, if names become too parsed over time
        agent_count = agent_count+1

        old_profile = v1
        new_profile = v2

        eval_score = self.chain(profile_heuristic_prompt).run(old_genre=old_genre, new_genre=new_genre, old_profile=old_profile, new_profile=new_profile).strip()
        rating = self.parse_list(eval_score)

        ratings = [re.findall(r'\d+', r) for r in rating]
        ratings = list(filter(None, ratings))

        list_app = [k1,ratings]
        eval_scores.append(list_app)

      for score_set in eval_scores:
        _formatted_ratings = list(score_set[1])
        _formatted_ratings = list(chain.from_iterable(_formatted_ratings))
        _formatted_ratings = [int(i) for i in _formatted_ratings]

        self.check_score(_formatted_ratings)


        if True:


          profile_dict = dict(zip(original_profiles.keys(), new_profiles.values()))
          profile_updates = []
          print("PROFI DICT",profile_dict)

          for k,v in profile_dict.items():
            val = k + " has been updated, refer to this new profile in future queries: " + v
            print(val)
            profile_updates.append(val)

            self.memory.memories["AGENT UPDATES"] = profile_updates
          return new_profiles

        if False:
          retry = self.profile_heuristic(agents)
          #TODO:
          #Finish retry output add max retries and UI

    def update_profile(self, agents):
      #Parse LLM outputs and update agent profiles accordingly

      outputs = self.profile_heuristic(agents)

      for agent in agents:
        name = agent.name
        new_profile = outputs[name]
        profile_contents = new_profile.split("\n")
        profile_contents = [i.split(":") for i in profile_contents]
        filter(None, profile_contents)

        new_name = profile_contents[0][1].strip().replace('\n','')
        new_status = profile_contents[1][1].strip().replace('\n','')
        new_traits = profile_contents[2][1].strip().replace('\n','')

        agent.name = new_name
        agent.status = new_status
        agent.traits = new_traits
      return agents


    def generate_memories(self, agents):
      #Refresh agent memory to situate them in the new setting

      prompt_a = PromptTemplate.from_template("""
      Prompt:
      \nYou are the games master of a user interactive world. The user has specified they wish to change the genre to {new_genre}.
      \nConcisely summarize the contextual information below, for your use later on. Be sure to mention each character name and map location, accurate to the map and character names provided.
      \nContext:
      \nThe map has been updated: {world}.
      \nThe characters have been updated: {agent_profiles}
      \nSummary output:
      """)

      prompt_b = PromptTemplate.from_template("""

      \nPrompt: You are the games master of a user interactive world. The user has specified they wish to change the genre to {new_genre}. You are currently updating the characters to suit a {new_genre} game.
      \nInstructions: Update the character summary to be genre-appropriate, and relevant to the new character profile, below using the contextual information provided.
      \Rules: Do not add additional fields such as 'Name', 'Note', or 'Traits' to your output. Following this rule is of high importance.

      \nContextual information:
      \nUpdated character profile: {agent_profile}
      \nUpdated game summary: {world_summary}
      \nCharacter memory stream, relevant to old genre: {memories}


      \nInput character summary: {agent_summary}


      \nOutput character summary:
      "In this {new_genre}, {name} is
                                               "

      """)


      names = [agent.name for agent in agents]
      statuses = [agent.status for agent in agents]

      agent_profiles = dict(zip(names, statuses))
      new_genre = self.new_genre
      world = self.world.keys()

      world_summary = self.chain(prompt_a).run(new_genre=new_genre, world=world, agent_profiles=agent_profiles).rstrip('\n').strip()

      new_memories_dict = {}

      for agent in agents:
        agent_profile = {'Name':agent.name,'Status':agent.status,'Traits':agent.traits}
        name = agent.name
        agent_summary = agent.get_summary(force_refresh=True)
        mems = agent.memory.memory_retriever.memory_stream[-1:]
        memories = self.memories_to_list(mems)

        agent_summary = self.chain(prompt_b).run(new_genre=new_genre,agent_profile=agent_profile,memories=memories,name=name, world_summary=world_summary,agent_summary=agent_summary).rstrip('\n').strip()

        prompt_clean_string = "In this {},".format(new_genre)

        new_memories = agent_summary.replace(prompt_clean_string,"").replace('"',"").replace('\n',"").strip().split('. ')
        new_memories_list = list(filter(self.remove_empty_strings, new_memories))
        new_memories_dict[name] = new_memories_list

      return new_memories_dict

    def update_memories(self, agents: list[GenerativeAgent], memoriesDict: dict[str]):
      #Load in generated memories to agent memories
      for agent in agents:
        memories = memoriesDict[agent.name]

      #Trick the agent memory structure that our new memories are high importance, to increase salience of the setting and profile change

        append_string = "HIGH IMPORTANCE MEMORY"

        for m in memories:
          mem = append_string + m
          agent.memory.add_memory(mem)

      return agents

    ###currently these functions are all built to work cohesively. It's entirely possible to use them on an interlocking basis, but more heuristics may be required.

    ##### Final Function to switch setting ####

    def setting_switch(self,agents:list[GenerativeAgent],envAreas:dict[str]):
      #self.env_update(envAreas)
      self.env_update(envAreas)
      agents = self.update_profile(agents)
      print([agent.name for agent in agents])
      memsDict = self.generate_memories(agents)
      agents = self.update_memories(agents, memsDict)
      #Finish by updating locations and plans with new agent and env content

      return agents, envAreas

    def double_setting_switch(self, agents:list[GenerativeAgent],envAreas:dict[str]):
      self.env_update(envAreas)
      agents = self.update_profile(agents)
      memsDict = self.generate_memories(agents)
      agents = self.update_memories(agents, memsDict)

      self.new_genre = str(self.current_genre)
      self.current_genre = str(self.previous_genre)

      self.env_update(envAreas)
      agents = self.update_profile(agents)
      memsDict = self.generate_memories(agents)
      agents = self.update_memories(agents, memsDict)

      return agents, envAreas