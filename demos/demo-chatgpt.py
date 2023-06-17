# Manually use ChatGPT to be the agent, try the environment out.
import gymnasium
import gym_codecraft
from gym_codecraft.wrappers.envlogger import EnvLogger

# WARNING: Clean up any existing containers (There's always too many stopped containers on my machine:)
import docker
docker.from_env().containers.prune()

# Trick: Make project root the current working directory
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)

env = gymnasium.make("gym_codecraft/CodeCraft-v0")
env = EnvLogger(env)

obs, _ = env.reset()
print(obs['obs'])

while True:
    action = input("Action: ")
    obs, reward, terminated, _, _ = env.step(action)
    print(obs)
    if (reward != 0):
        print(f"Reward: {reward}")
    if (terminated):
        break
    print("What's your next action (in one-line JSON format)?")
    print()