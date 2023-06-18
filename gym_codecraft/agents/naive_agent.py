from gym_codecraft.agents.base_agent import BaseAgent
import random
import json

class NaiveAgent(BaseAgent):
    def __init__(self):
        self.action_space = [
            {"action": "command", "command": "ls"},
            {"action": "start", "task_id": "1"},
            {"action": "exit"},
        ]
    
    def get_action(self, observation):
        """Randomly choose one of the available actions."""
        random_action = random.choice(self.action_space)
        
        return json.dumps(random_action)