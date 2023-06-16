import gymnasium as gym
from gymnasium import spaces
import string
import json
import docker
import tarfile
import io

class CodeCraftEnv(gym.Env):
    def __init__(self):
        self.observation_space = spaces.Dict({"obs": spaces.Text(1024, charset=string.printable)})
        self.action_space = spaces.Text(10, charset=string.printable)
        self.client = docker.from_env()     # High-level client
        self.api_client = docker.APIClient() # Low-level client
        self.container = None
        self.working_dir = "/"
        self.shell = "/bin/sh"

    def reset(self, task_id=None, seed=None, options=None):
        if self.container:
            self.container.stop()
            self.container = None

        if task_id is None:
            with open('welcome.txt', 'r') as file:
                welcome = file.read()
            return {"obs": welcome}, {}
        
        # read curriculum.json to get the task
        with open('curriculum.json', 'r') as file:
            curriculum_data = json.load(file)
        if task_id in curriculum_data['tasks']:
            task = curriculum_data['tasks'][task_id]
            docker_image = task['docker']
            self.shell = task['shell']
            self.working_dir = task['working_dir']
            self.pull_image(docker_image)
            self.container = self.client.containers.run(docker_image, command=self.shell, working_dir=self.working_dir, 
                                                        detach=True, tty=True, remove=True)
            return {"obs": f"Task {task_id}:\n {task}\n"}, {}

        else:
            return {"obs": f"Task {task_id} not found.\n"}, {}

    def step(self, action : str):
        terminated = False
        info = {"info": ""}
        observation = {"obs": ""}
        reward = 0
        act = None
        try:
            act = json.loads(action)
            act['action']
        except Exception as e:
            reward = -1
            observation = {"obs": f"Invalid action: {e}"}

        if act:
            if act['action'] == 'reset':
                observation, info = self.reset(act['task_id'])

            elif self.container:
                # 1. Shell Command
                if act['action'] == 'command':
                    exec_result = self.container.exec_run([self.shell, '-c', act['command']]) # type: ignore
                    observation = {"obs": exec_result.output.decode('utf-8')}
                
                # 2. Write a File
                elif act['action'] == 'write_file':
                    container_dest_path = act['path']
                    file_content = act['content']
                    tar_buffer = io.BytesIO()
                    tar = tarfile.open(fileobj=tar_buffer, mode='w')
                    tarinfo = tarfile.TarInfo(name=container_dest_path)
                    tarinfo.size = len(file_content)
                    tar.addfile(tarinfo, io.BytesIO(file_content.encode('utf-8')))
                    tar.close()
                    tar_bytes = tar_buffer.getvalue()
                    # Copy the tarball to the container
                    self.container.put_archive(path=self.working_dir, data=tar_bytes) # type: ignore
                    observation = {"obs": f"File {container_dest_path} written."}

                # 3. Submit the code
                elif act['action'] == 'submit':
                    # TODO: check the submission, give reward = 1 if correct
                    reward = 1
                    observation = {"obs": "Code submitted."}
                
                elif act['action'] == 'exit':
                    self.close()
                    terminated = 1
                    observation = {"obs": "Exited."}

                # 999. Unknown action
                else:
                    reward = -1
                    observation = {"obs": f"Unknown action: {act['action']}"}

            else:
                reward = -1
                observation = {"obs": 'No running container: please use `{"action":"reset", "task_id":"?"}` to choose a task.'}
            


        return observation, reward, terminated, False, info
    
    def render(self):
        pass

    def close(self):
        if (self.container):
            self.container.stop() # type: ignore
    
    def pull_image(self, docker_image, verbose=True):
        # Pull the Alpine image and get the response
        response = self.api_client.pull(docker_image, stream=True)
        self.last_status = ""
        self.last_progress = ""

        # Print out status updates as they come in
        for chunk in response:
            # Split the chunk into lines
            lines = chunk.decode('utf-8').splitlines()

            for line in lines:
                # Parse the JSON response
                update = json.loads(line)
                
                if verbose:
                    # Check if 'progress' field is in the response
                    if ('progress' in update):
                        print(f"{update['status']}: {update['progress']}", end='\r')
                        self.last_progress = update['progress']
                    elif update['status'] != self.last_status:
                        if self.last_progress != "":
                            print()
                            self.last_progress = ""
                        print(update['status'])
                        self.last_status = update['status']