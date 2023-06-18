import gymnasium as gym
from gymnasium import spaces
import string
import json
import docker
import tarfile
import io
import pkg_resources

class CodeCraftEnv(gym.Env):
    def __init__(self):
        self.observation_space = spaces.Dict({"obs": spaces.Text(4096, charset=string.printable)})
        self.action_space = spaces.Text(4096, charset=string.printable)
        self.client = docker.from_env()     # High-level client
        self.api_client = docker.APIClient() # Low-level client
        self.container = None
        self.working_dir = "/workspace"
        self.shell = "/bin/sh"

        self.current_task_id = None # the id of the task that the agent is currently working on, None means no task is started

    def step(self, action:str):
        """
        avaiable actions: command(command), write_file(path, content), reset(), submit(), start(task_id), close(), exit()
            - self.current_task_id needed:
                - command(command): execute a shell command
                - write_file(path, content): write a file to the container
                - reset(): reset the container
                - submit(): submit the answer to the task and close the container
            - self.current_task_id not needed:
                - start(task_id): start a new container for a new task
                - close(): close the container
                - exit(): exit the environment
        """
        terminated = False
        info = {"info": ""}
        observation = {"obs": ""}
        reward = 0
        action_obj = None

        try:
            action_obj = json.loads(action)
            action = action_obj['action']
            if action in ['command', 'write_file', 'reset', 'submit'] and self.current_task_id is None:
                observation = {"obs": "No task started. Please use start action to start a task."}
                reward = -1

            else:
                if action == 'command':
                    exec_result = self.container.exec_run([self.shell, '-c', action_obj['command']]) # type: ignore
                    observation = {"obs": exec_result.output.decode('utf-8')}

                elif action == 'write_file':
                    container_dest_path = action_obj['path']
                    file_content = action_obj['content']
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

                elif action == 'reset':
                    observation, info = self.reset()

                elif action == 'submit':
                    # TODO: check the submission, give reward = 1 if correct
                    reward = 1
                    observation = {"obs": "Code submitted. Task closed. Please start a new task."}
                    self.close()

                elif action == 'start':
                    observation, info = self.start(action_obj['task_id'])

                elif action == 'close':
                    self.close()
                    observation = {"obs": "Task closed."}

                elif action == 'exit':
                    self.close()
                    terminated = 1
                    observation = {"obs": "Exited."}

                else:
                    observation = {"obs": f"Unknown action: {action}"}
                    reward = -1

        except Exception as e:
            reward = -1
            observation = {"obs": f"Invalid action error: {e}"}
            action_obj = None

        return observation, reward, terminated, False, info
    
    def render(self):
        pass

    def reset(self, seed=None, options=None):
        return self.start(self.current_task_id, seed=seed, options=options)

    def start(self, task_id=None, seed=None, options=None):
        self.current_task_id = task_id

        if self.container:
            self.container.stop() # type: ignore
            self.container = None

        if task_id is None:
            welcome_path = pkg_resources.resource_filename('gym_codecraft', 'data/welcome.txt')
            with open(welcome_path, 'r') as file:
                welcome = file.read()
            return {"obs": welcome}, {}
        
        # read curriculum.json to get the task
        curriculum_path = pkg_resources.resource_filename('gym_codecraft', 'data/curriculum.json')
        with open(curriculum_path, 'r') as file:
            curriculum_data = json.load(file)

        if task_id in curriculum_data['tasks']:
            task = curriculum_data['tasks'][task_id]
            docker_image = task['docker']
            self.shell = task['shell']
            new_volume = self.client.volumes.create()
            
            self.pull_image(docker_image) # explicitly pull the image to show the progress updates

            self.container = self.client.containers.run(docker_image, volumes={new_volume.name: {'bind': self.working_dir, 'mode': 'rw'}}, working_dir=self.working_dir,  # type: ignore
                                                        detach=True, tty=True, remove=True)
            return {"obs": f"Task {task_id}:\n {task}\n"}, {}

        else:
            return {"obs": f"Task {task_id} not found.\n"}, {}


    def close(self):
        if (self.container):
            self.container.stop() # type: ignore
        self.current_task_id = None
    
    def pull_image(self, docker_image, verbose=True):
        # Pull the image with progress updates
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