"""
An implementation of the Model class that uses the llama_cpp library to 
generate responses based on the given prompt and other parameters.
"""

import threading
from agentsystem.models.Model import ChatModel
from tqdm import tqdm
from agentsystem.agents.agents import Model
from llama_cpp import Llama, StoppingCriteriaList


class LlamaModel(Model):
    """
    An implementation of the Model class that uses the llama\\_cpp library to generate responses based on the given prompt and other parameters.

    Attributes:
        model (Llama): The llama\\_cpp model used for generating responses.

    Methods:
        format(system\\_message, prompt\\_message, prefix\\_message) -> str: Formats the given messages into a string that can be passed to the llama model.
        from\\_model(model: Llama) -> LlamaModel: Initializes the class with an existing llama\\_cpp model.
    """

    model: Llama
    interrupted: bool = False

    def format(self, system_message, prompt_message, prefix_message):
        """Formats the given messages into a string that can be passed to the llama model.

        Args:
            system_message (str): The system message to include in the formatted string.
            prompt_message (str): The prompt message to include in the formatted string.
            prefix_message (str): The prefix message to include in the formatted string.

        Returns:
            str: The formatted string.
        """
        system = "" if system_message == "" else f"<<SYS>>\n{system_message}\n<</SYS>>\n\n"
        instructions = "" if system == "" == prompt_message else f"[INST] {system}{prompt_message} [/INST]\n"
        prompt = f"{instructions}{prefix_message}"
        return prompt

    @classmethod
    def from_model(cls, model: Llama):
        """
        docstring
        """
        return cls(model)

    def _run(self, prompt, **extra_args):
        """
        Generates a response using the llama model and returns it as a string. If stream is set to true, it generates tokens one by one in real time, otherwise, it generates the whole response at once.

        Args:
            prompt (str): The prompt message to pass to the model.
            **extra\\_args: Additional arguments that will be passed directly to the llama model's generate method.

        Returns:
            str: The generated response from the model.
        """

        self.interrupted = False
        print(prompt)
        if "stream" in extra_args and extra_args["stream"]:
            prompt_message = ""
            for token in tqdm(
                self._generate_response(prompt, extra_args),
                total=extra_args["max_tokens"],
            ):
                prompt_message += self._extract_prompt_message(token)
                if self.pure_callback:
                    token["extras"] = extra_args
                    if "grammar" in token["extras"]:
                        token["extras"].pop("grammar")
                    t = threading.Thread(target=self.pure_callback, args=(token,))
                    # start the thread
                    t.start()

                print(prompt_message)
            return prompt_message
        else:
            tokens = self._generate_response(prompt, extra_args)
            prompt_message = self._extract_prompt_message(tokens)
            if self.pure_callback:
                tokens["extras"] = extra_args
                threading.Thread(target=self.pure_callback, args=(tokens,)).start()
            print(prompt_message)
            return prompt_message
        
    @staticmethod
    def _extract_prompt_message(tokens):
        tokens['text'] = tokens["choices"][0]["text"]
        tokens['is_fin'] = tokens["choices"][0]["finish_reason"] is not None
        return tokens["choices"][0]["text"]

    def _generate_response(self, prompt, extra_args):
        extra_args = {k: v for k, v in extra_args.items() if k in self.model.create_completion.__code__.co_varnames}
        return self.model.create_completion(prompt=prompt, stopping_criteria=self.stopping_criteria, **extra_args)

    def stopping_criteria(self, *args, **kwargs):
        return self.interrupted

    def interrupt(self) -> None:
        self.interrupted = True


class ChatLlamaModel(ChatModel, LlamaModel):
    """
    An implementation of the ChatModel class that uses the llama\\_cpp library to generate responses based on the given prompt and other parameters.

    Attributes:
        model (Llama): The llama\\_cpp model used for generating responses.

    Methods:
        _run(messages, **extra\\_args) -> str: Generates a response using the llama model and the llama.cpp create_chat_completion method and returns it as a string.

    """

    def _run(self, messages, **extra_args):
        """
        Generates a response using the llama model and the llama.cpp create_chat_completion method and returns it as a string.

        Args:
            messages (List[str]): The list of messages to pass to the model.
            **extra\\_args: Additional arguments that will be passed directly to the llama model's create_chat_completion method.

        Returns:
            str: The generated response from the model.
        """
        extra_args = {
            k: v for k, v in extra_args.items() if k in self.model.create_chat_completion.__code__.co_varnames
        }
        self.interrupted = False
        print(messages)
        completion = self.model.create_chat_completion(
            messages=messages, stopping_criteria=self.stopping_criteria, **extra_args
        )
        if extra_args["stream"]:
            prompt_message = ""
            for chunk in completion:
                prompt_message += chunk["choices"][0]["delta"]["content"]
                if self.pure_callback:
                    chunk["extras"] = extra_args
                    threading.Thread(target=self.pure_callback, args=(chunk,)).start()
                print(prompt_message)
            return prompt_message
        else:
            prompt_message = completion["choices"][0]["message"]["content"]
            if self.pure_callback:
                completion["extras"] = extra_args
                threading.Thread(target=self.pure_callback, args=(completion,)).start()
            print(prompt_message)
            return prompt_message
