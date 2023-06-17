from gym_codecraft.agents.base_agent import BaseAgent
import openai
import json
import os
from dotenv import load_dotenv
load_dotenv()
import logging
from pathlib import Path

class GPTAgent(BaseAgent):
    def __init__(self):
        # connect to openai api
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.messages_system = []
        # self.messages_system.append({"role": "system", "content": "You are a programer."})
        self.messages_task = []
        # TODO: should we pin this system message and keep user/assistant messages rolling?

        # logging
        logs_directory = Path('logs')
        if not logs_directory.exists():
            logs_directory.mkdir()
        self.logging = logging.getLogger('gpt_agent')
        self.logging.setLevel(logging.DEBUG)
        file_handler_a = logging.FileHandler('logs/gpt.log', encoding='utf-8')
        file_handler_a.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logging.addHandler(file_handler_a)

        # function call (New Feature from 0613)
        self.functions = [
                            {
                                "name": "command",
                                "description": "Execute a command in the Virtual Linux environment",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "command": {
                                            "type": "string",
                                            "description": "The command to execute",
                                        },
                                    },
                                    "required": ["command"],
                                },
                            },
                            {
                                "name": "write_file",
                                "description": "Write a file to the Virtual Linux environment",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "content": {
                                            "type": "string",
                                            "description": "The content of the file to write",
                                        },
                                    },
                                    "required": ["content"],
                                },
                            },
                            {
                                "name": "reset",
                                "description": "Reset the Virtual Linux environment, start another task",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "task_id": {
                                            "type": "string",
                                            "description": "The ID of the task to start",
                                        },
                                    },
                                    "required": ["task_id"],
                                },
                            },
                            {
                                "name": "exit",
                                "description": "Stop the Virtual Linux environment, end the conversation",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        
                                    },
                                    "required": [],
                                },
                            },
                            {
                                "name": "submit",
                                "description": "Submit the answer to the task",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        
                                    },
                                    "required": [],
                                },
                            },
                        ]


    def append_system_message(self, message):
        self.messages_system.append({"role": "system", "content": message})
        self.logging.info(f"System Messages: {self.messages_system}")
        
    def get_action(self, observation):
        try:
            self.messages_task.append({"role": "user", "content": f"{observation}\nWhat's your next action? (respond with a function call)"})
            self.logging.info(f"Task Messages: {self.messages_task}")
            chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613",
                                                           messages=(self.messages_system+self.messages_task),
                                                           functions=self.functions,
                                                           function_call="auto",  # auto is default, but we'll be explicit
                                                           )
            self.logging.info(f"Chat completion: {chat_completion}")
            response_message = chat_completion["choices"][0]["message"] # type: ignore
            if response_message.get("function_call"):
                function_name = response_message["function_call"]["name"]
                action_obj = {"action": function_name}
                action_obj.update(json.loads(response_message["function_call"]["arguments"]))
                action = json.dumps(action_obj)
                if action_obj["action"] == "reset":
                    self.messages_task = []
                self.messages_task.append({"role": "assistant", "content": action})
            else:
                self.logging.error(f"Error: function_call not found. {response_message}. Exit.")
                action = '{"action": "exit"}'
        except Exception as e:
            self.logging.error(f"Error: Exception {e}. Exit.")
            action = '{"action": "exit"}'
        return action