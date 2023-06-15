import gymnasium
import gym_codecraft

# WARNING: Clean up any existing containers
import docker
docker.from_env().containers.prune()

env = gymnasium.make("gym_codecraft/CodeCraft-v0")
obs = env.reset()
print(obs)

commands = ['pwd', 'echo \'print("Hello, world!")\' > hello.py', 'cat hello.py', 'python hello.py']
for command in commands:
    obs, reward, _, _, _ = env.step(['/bin/sh', '-c', command])
    print(obs)

env.close()