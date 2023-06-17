import json
import gymnasium
import gym_codecraft
from gym_codecraft.agents.naive_agent import NaiveAgent
from gym_codecraft.wrappers.envlogger import EnvLogger

# WARNING: Clean up any existing containers (There's always too many stopped containers on my machine:)
import docker
docker.from_env().containers.prune()

env = gymnasium.make("gym_codecraft/CodeCraft-v0")
env = EnvLogger(env)

agent = NaiveAgent()

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
