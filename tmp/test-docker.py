import docker
client = docker.from_env()

# delete all stopped containers
client.containers.prune()
# from docker.models.volumes import Volume
volume = client.volumes.create()

# volume = client.volumes.create(name='workspace', driver='local')
# start a container
container = client.containers.run("python:alpine3.18", volumes={volume.name: {'bind': "/workspace", 'mode': 'rw'}}, working_dir="/workspace", tty=True, detach=True, remove=True) # type: ignore

# execute commands
commands = ['cd /tmp', 'ls', 'whoami', 'pwd', 'mkdir tmp', 'tree', 'cat test.txt']
for command in commands:
    exec_result = container.exec_run(['/bin/sh', '-c', command]) # type: ignore
    print(exec_result.output.decode('utf-8'))

# stop the container
container.stop() # type: ignore
