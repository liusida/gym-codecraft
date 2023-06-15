import gymnasium
import gym_codecraft

env = gymnasium.make("gym_codecraft/CodeCraft-v0")
env.reset()
print(env.action_space.sample())
obs, reward, _, _, _ = env.step(env.action_space.sample())
print(obs)