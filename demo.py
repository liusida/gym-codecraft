import json
import gymnasium
import gym_codecraft

# WARNING: Clean up any existing containers (There's always too many stopped containers on my machine:)
import docker
docker.from_env().containers.prune()

env = gymnasium.make("gym_codecraft/CodeCraft-v0")
obs = env.reset()
print(obs)

actions = [
    {'action':'lol'},
    {'action':'command', 'command':'pwd'},
    {'action':'write_file', 'path':'hello.py', 'content': 'print("Hello, world!")'},
    {'action':'command', 'command':'ls'},
    {'action':'command', 'command':'cat hello.py'},
    {'action':'command', 'command':'python hello.py'},
    {'action':'submit'}
]
for action in actions:
    print(action)
    obs, reward, _, _, _ = env.step(json.dumps(action))
    print(obs)
    if (reward != 0):
        print(f"Reward: {reward}")

env.close()