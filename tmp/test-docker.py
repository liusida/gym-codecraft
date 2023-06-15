import docker
client = docker.from_env()

# delete all stopped containers
client.containers.prune()

# start a container
container = client.containers.run("python:alpine3.18", command="/bin/sh", working_dir="/root", detach=True, tty=True, remove=True)

# execute commands
commands = ['ls', 'whoami', 'pwd', 'mkdir tmp', 'tree']
for command in commands:
    exec_result = container.exec_run(command)
    print(exec_result.output.decode('utf-8'))

# stop the container
container.stop()
