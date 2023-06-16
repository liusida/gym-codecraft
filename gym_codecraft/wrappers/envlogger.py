import gymnasium as gym
import logging
from pathlib import Path

class EnvLogger(gym.Wrapper):
    def __init__(self, env):
        logs_directory = Path('logs')
        if not logs_directory.exists():
            logs_directory.mkdir()
            
        self.logging = logging.getLogger('envlogger')
        self.logging.setLevel(logging.DEBUG)
        file_handler_a = logging.FileHandler('logs/env.log')
        file_handler_a.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logging.addHandler(file_handler_a)
        
        super().__init__(env)

    def step(self, action:str):
        self.logging.info(f"Action: {action}")
        observation, reward, terminated, truncated, info = self.env.step(action)
        self.logging.info(f"Observation: {observation}")
        if reward!=0:
            self.logging.info(f"Reward: {reward}")
        return observation, reward, terminated, truncated, info