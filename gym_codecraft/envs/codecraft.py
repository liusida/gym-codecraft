import gymnasium as gym
from gymnasium import spaces
import string
import json
import docker

class CodeCraftEnv(gym.Env):
    def __init__(self):
        self.observation_space = spaces.Dict({"obs": spaces.Text(1024, charset=string.printable)})
        self.action_space = spaces.Text(10, charset=string.printable)
        self.client = docker.from_env()
        self.container = None

    def reset(self, task_id="1", seed=None, options=None):
        # TODO: read curriculum.json to get the task
        with open('curriculum.json', 'r') as file:
            curriculum_data = json.load(file)
        if task_id in curriculum_data['tasks']:
            task = curriculum_data['tasks'][task_id]
            docker_image = task['docker']
            shell = task['shell']
            working_dir = task['working_dir']
            self.container = self.client.containers.run(docker_image, command=shell, working_dir=working_dir, detach=True, tty=True, remove=True)
            return {"obs": f"Task {task_id}:\n {task}\n"}, {}

        else:
            return {"obs": f"Task {task_id} not found.\n"}, {}

    def step(self, action):
        exec_result = self.container.exec_run(action) # type: ignore

        terminated = False
        reward = 1 if terminated else 0  # Binary sparse rewards
        observation = {"obs": exec_result.output.decode('utf-8')}
        info = {"info": ""}

        return observation, reward, terminated, False, info
    
    def render(self):
        pass

    def close(self):
        if (self.container):
            self.container.stop() # type: ignore