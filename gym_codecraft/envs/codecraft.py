import gymnasium as gym
from gymnasium import spaces


class CodeCraftEnv(gym.Env):
    def __init__(self):
        self.observation_space = spaces.Dict({"obs": spaces.Text(1024)})
        self.action_space = spaces.Text(10)

    def _get_obs(self):
        return {"obs": "\n"}
    
    def _get_info(self):
        return {"info": "\n"}
    
    def reset(self):
        pass

    def step(self, action):
        # An episode is done iff the agent has reached the target
        terminated = False
        reward = 1 if terminated else 0  # Binary sparse rewards
        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, terminated, False, info
    
    def render(self):
        pass

    def close(self):
        pass