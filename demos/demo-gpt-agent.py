import json
import gymnasium
import gym_codecraft
from gym_codecraft.wrappers.envlogger import EnvLogger
from gym_codecraft.agents.gpt_agent import GPTAgent

# WARNING: Clean up any existing containers (There's always too many stopped containers on my machine:)
import docker
docker.from_env().containers.prune()

# Trick: Make project root the current working directory
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)

# Env
env = gymnasium.make("gym_codecraft/CodeCraft-v0")
env = EnvLogger(env)
# Agent
agent = GPTAgent(model="gpt-3.5-turbo-0613", using_function_call=False)

# Start
obs, _ = env.reset()
first_message = True

while True:
    if first_message:
        agent.append_system_message(obs['obs'])
        first_message = False
        action = agent.get_action("")
    else:
        action = agent.get_action(obs['obs'])
    print(action)
    obs, reward, terminated, _, _ = env.step(action)
    print(obs)
    if (reward != 0):
        print(f"Reward: {reward}")
    if (terminated):
        break
    input("Press Enter to continue...")
    print()
