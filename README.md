# gym-codecraft
An gym-like environment with a docker container sandbox for the agent to learn to code.

# Requirements

I'm using Windows, so `Docker Desktop` is needed. Also the Python library `docker` is needed, which can automatically get client from the environment.

The Python library `gymnasium`, which is the successor of the famous `gym`, is needed.

# Running the demo

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
python demo.py
```

# Still Under Construction

### Todo:

1. write some nice tasks in `curriculum.json`.

2. giving reward

3. step by step reward

4. rendering? monitoring?