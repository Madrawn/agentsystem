import os
from agentsystem.models.LlamaModel import LlamaModel
from agentsystem.models.Model import Model
import ollama


# https://github.com/ollama/ollama/blob/main/docs/api.md
class OllamaModel(LlamaModel):

    model: str  # Name of the model
    options: ollama.Options = ollama.Options()

    @classmethod
    def from_model(cls, model: str):
        """
        docstring
        """
        # This is the model file that will be used to create the model
        modelfile = f"""
FROM {model}
"""
        model_name = os.path.basename(model)
        try:
            print(ollama.show(model=model_name))
        except ollama.ResponseError:
            print(modelfile)
            resp = ollama.create(model=model_name, modelfile=modelfile, stream=True)
            for chunk in resp:
                print(chunk, flush=True)

        return cls(model_name)

    def _generate_response(self, prompt, extra_args):
        self.options = {**self.options, **extra_args}
        for key in list(self.options.keys()):
            if key not in ollama.Options.__annotations__.keys() and key not in [
                "ignore_eos",
                "logit_bias",
            ]:
                self.options.pop(key)

        token = ollama.generate(
            prompt=prompt, model=self.model, raw=True, stream=True, options=self.options
        )
        return token

    @staticmethod
    def _extract_prompt_message(token):
        token["text"] = token["response"]
        token["is_fin"] = token["done"]
        return token["response"]
