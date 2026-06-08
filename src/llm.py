import os
import yaml
from dotenv import load_dotenv

from src.openrouter_client import chat_completion, get_openrouter_model

load_dotenv()  # Loads variables from .env into environment

class LLM:
    def __init__(self, config_file: str):
        self.config_file = config_file

        print(f"Loading config from: {config_file}")
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        print("Full loaded config:", config)

        self.model = (
            config.get("openrouter", {}).get("model") or
            config.get("openai", {}).get("model") or
            config.get("model") or
            get_openrouter_model()
        )

        print(f"Model selected: {self.model}")

    def get_prompt(self, prompt_name: str):
        with open(self.config_file, 'r') as file:
            prompts = yaml.safe_load(file)
            if prompt_name not in prompts:
                raise ValueError(f"Prompt '{prompt_name}' not found in the configuration file.")
            return prompts[prompt_name]

    def generate_response(self, prompt_name, response_format, text):
        prompt_config = self.get_prompt(prompt_name)
        messages = [
            {"role": "system", "content": prompt_config["system_message"]},
            {"role": "user", "content": prompt_config["template"].replace("{text}", text)},
        ]

        params = {
            "model": self.model,
            "messages": messages,
        }

        if response_format:
            params["response_format"] = response_format

        return chat_completion(**params)
    
    
class PromptGenerator:
    def __init__(self, prompt_name, config_file, api_key=None):
        """
        Initializes the PromptGenerator with prompt configuration.
        
        Args:
            prompt_name (str): The name of the prompt as defined in the YAML file.
            config_file (str): The path to the user-defined YAML file containing prompt definitions.
            api_key (str, optional): Deprecated. OpenRouter uses OPENROUTER_API_KEY from the environment.
        """
        self.prompt_data = self.load_prompt_data(prompt_name, config_file)
        self.system_message = self.prompt_data['system_message']
        self.template = self.prompt_data['template']
        
        self.token_usage = {
            'prompt_tokens': 0,
            'completion_tokens': 0
        }

    def load_prompt_data(self, prompt_name, config_file):
        """
        Loads prompt data from the specified YAML file.

        Args:
            prompt_name (str): The name of the prompt as defined in the YAML file.
            config_file (str): The path to the YAML file.

        Returns:
            dict: The prompt data containing the system message and template.
        """
        absolute_path = os.path.abspath(config_file)
        print("Resolved config file path:", absolute_path)
        
        if not os.path.isfile(absolute_path):
            raise FileNotFoundError(f"The YAML file '{absolute_path}' does not exist.")
        
        with open(absolute_path, 'r') as file:
            prompts = yaml.safe_load(file)
            if prompt_name not in prompts:
                raise ValueError(f"Prompt '{prompt_name}' not found in the configuration file.")
            return prompts[prompt_name]

        with open(config_file, 'r') as file:
            prompts = yaml.safe_load(file)
            if prompt_name not in prompts:
                raise ValueError(f"Prompt '{prompt_name}' not found in the configuration file.")
            return prompts[prompt_name]

    def get_messages(self, **prompt_kwargs):
        """
        Formats the messages to be sent to the OpenRouter chat API.

        Args:
            **prompt_kwargs: Keyword arguments to replace placeholders in the prompt template.

        Returns:
            list: A list of messages for the chat completion.
        """
        user_message = self.template.format(**prompt_kwargs)
        return [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_message}
        ]

    def generate_response(self, model, temperature=0, response_format=None, **prompt_kwargs):
        """
        Generates a response using the configured OpenRouter model.

        Args:
            model (str): OpenRouter model ID to use for generating the response.
            temperature (float): Controls the randomness of the response.
            response_format (str, optional): The format of the response.
            **prompt_kwargs: Keyword arguments for replacing placeholders in the prompt template.

        Returns:
            str: The generated response from the model.
        """
        messages = self.get_messages(**prompt_kwargs)

        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        if response_format is not None:
            params["response_format"] = response_format

        return chat_completion(**params)

    def update_usage(self, response):
        """
        Updates the token usage statistics based on the response from the chat model.

        Args:
            response (object): The response object from the chat API.
        """
        self.token_usage['prompt_tokens'] = response.usage.prompt_tokens
        self.token_usage['completion_tokens'] = response.usage.completion_tokens
