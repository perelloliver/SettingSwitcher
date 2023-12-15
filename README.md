# SettingSwitcher
Project page for Setting Switcher: Changing genre-settings in text-based game environments populated by generative agents as presented at NeurIPS 2023 Workshop on Machine Learning for Creativity and Design.

## [Test it out on colab!](https://colab.research.google.com/drive/1VF6xJ-ovp9oimnjylr46_zhwojDeRA-b?usp=sharing)

## [Read our paper!](https://neuripscreativityworkshop.github.io/2023/papers/ml4cd2023_paper17.pdf)


This work is still ongoing. If you'd like to work together on further developing this to deploy in-game, please be in touch - let's make it happen.

Contents:

- Testing environment
- Example notebook
- Agent (switcher.py)
- All relevant modules for agent (locator, plans, etc)

Points for future work:

Big TODO:
- This work, particularly simulation.py, has since been significantly improved with added capability for perception and interaction. Updates to be made soon.

Dreams of further development and ideas for future work:

- Update since-improved simulation functions with perception and agent interaction.

- Implement higher quality generative agents, such as Concordia agents.

- Permit user interactions within the game environment

- Improve quality and accuracy of output further, testing more genres and tuning heuristic prompts.

- Connect to the visual using a pipeline of GPT-4-Vision, stable diffusion/midjourney/any text-to-image and SettingSwitcher agent.

    - Build in additional functions for generating prompts tailored to X model based on setting i.e art style.

    - Work this into a rudimentary visual game environment.

- Connect to the creation of location trees through prompting
    - Using the description of locations on our map, generate sub-locations and items.

