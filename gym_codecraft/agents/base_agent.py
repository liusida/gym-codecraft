class BaseAgent(object):
    def __init__(self):
        pass

    def get_action(self, observation):
        """Given observation, return the action that should be taken."""
        raise NotImplementedError