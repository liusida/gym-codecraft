import json
import gymnasium
import gym_codecraft
from gym_codecraft.wrappers import EnvLogger

# WARNING: Clean up any existing containers (There's always too many stopped containers on my machine:)
import docker
docker.from_env().containers.prune()

env = gymnasium.make("gym_codecraft/CodeCraft-v0")
env = EnvLogger(env)

obs, _ = env.reset()
print(obs)

actions = [
    {'action':'command', 'command': 'ls'}, # intentional error: no task yet.

    {'action':'start', 'task_id':'1'},
    {'action':'lol'}, # intentional error: unknow action
    {'action':'command', 'command':'pwd'},
    {'action':'write_file', 'path':'hello.py', 'content': 'print("Hello, world!")'},
    {'action':'reset'},
    {'action':'command', 'command':'ls'},
    {'action':'command', 'command':'cat hello.py'},
    {'action':'command', 'command':'python hello.py'},
    {'action':'submit'},

    {'action':'start', 'task_id':'2'},
    {'action':'command', 'command':'apk update; apk add git'},
    {'action':'command', 'command': 'git --help'},
    {'action':'command', 'command':'git clone https://github.com/liusida/gym-codecraft.git .'},
    {'action':'submit'},
    
    {'action':'start', 'task_id':'3'},
    {'action':'command', 'command': 'apk update; apk add curl'},
    {'action':'command', 'command': 'curl -o input.txt https://raw.githubusercontent.com/liusida/gym-codecraft/main/assets/3/input.txt'},
    {'action':'command', 'command': 'cat input.txt'},
    {'action':'command', 'command': 'pip install requests'},
    {'action':'write_file', 'path':'main.py', 'content': """
import urllib.request
url = "https://raw.githubusercontent.com/liusida/gym-codecraft/main/assets/3/input.txt"
urllib.request.urlretrieve(url, "input.txt")
# Read the file contents
file_path = "input.txt"
with open(file_path, 'r') as file:
    file_contents = file.read()
# Create a list of numbers
numbers = [int(num) for num in file_contents.strip().split(' ')]
# Sort the numbers in ascending order
numbers.sort()
# Save the sorted numbers to output.txt
output_file = "output.txt"
with open(output_file, 'w') as f:
    for num in numbers:
        f.write(str(num) + ' ')
print("Numbers sorted and saved to output.txt.")
    """},
    {'action':'command', 'command':'python main.py'},
    {'action':'command', 'command':'tree'},
    {'action':'command', 'command':'cat output.txt'},
    {'action':'submit'},
    {'action':'exit'},
    {'action':'submit'},
]
for action in actions:
    print(action)
    obs, reward, terminated, _, _ = env.step(json.dumps(action))
    print(obs)
    if (reward != 0):
        print(f"Reward: {reward}")
    if (terminated):
        break
    print()

env.close()