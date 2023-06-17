import json
import gymnasium
import gym_codecraft
from gym_codecraft.wrappers.envlogger import EnvLogger
from gym_codecraft.agents.naive_agent import NaiveAgent

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
agent = NaiveAgent()

# Start
obs, _ = env.reset()

while True:
    action = agent.get_action(obs['obs'])
    print(action)
    obs, reward, terminated, _, _ = env.step(action)
    print(obs)
    if (reward != 0):
        print(f"Reward: {reward}")
    if (terminated):
        break
    print()
