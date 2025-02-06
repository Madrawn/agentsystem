import json
import os
import logging
from pathlib import Path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage,
    set_global_handler,
)
from llama_index.llms.azure_inference import AzureAICompletionsModel
from llama_index.embeddings.azure_inference.base import AzureAIEmbeddingsModel
from llama_index.core.callbacks.simple_llm_handler import SimpleLLMHandler
from llama_index.core.chat_engine.types import ChatMode
from regex import P

from agentsystem.agents.agents import Agent
from agentsystem.models.Response import Response
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()


# Constants
API_VERSION = "2024-05-01-preview"
LOG_FILE = "llama_index.log"
data_directory = os.getenv("DATA_DIRECTORY")
if not data_directory:
    raise ValueError("DATA_DIRECTORY environment variable is not set")
DATA_DIRECTORY = Path(data_directory)
PERSIST_DIR = Path(os.getenv("PERSIST_DIR")).absolute()
API_KEY = os.getenv("AZURE_INFERENCE_CREDENTIAL")
AZURE_INFERENCE_ENDPOINT = os.getenv("AZURE_INFERENCE_ENDPOINT")
os.environ["OPEN_AI_KEY"] = API_KEY if API_KEY else ""
# Environment setup

from llama_index.core.memory import ChatMemoryBuffer

memory = ChatMemoryBuffer.from_defaults(token_limit=1500)

class IndexAgent(Agent):

    # Logging setup
    def setup_logging(self):
        logger = logging.getLogger("llama_index_logger")
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    # LLM and Embedding Model setup
    def setup_models(self):
        if API_KEY is None:
            raise ValueError("API_KEY environment variable is not set")

        try:
            Settings.llm = AzureAICompletionsModel(
                endpoint=f"{AZURE_INFERENCE_ENDPOINT}/openai/deployments/gpt-4o",
                credential=API_KEY,
                client_kwargs={"headers": {"api-key": API_KEY}},
                model_name="gpt-4o",
            )
            Settings.embed_model = AzureAIEmbeddingsModel(
                endpoint=f"{AZURE_INFERENCE_ENDPOINT}/openai/deployments/text-embedding-3-large",
                credential=API_KEY,
                model_name="text-embedding-3-large",
                api_version="2023-05-15",
            )
        except Exception as e:
            self.logger.error(f"Error setting up models: {e}")
            raise

    def load_documents(self):
        return SimpleDirectoryReader(
            recursive=True, required_exts=[".py"], input_dir=DATA_DIRECTORY
        ).load_data(show_progress=True)

    def setup_index(self):

        storage_context = StorageContext.from_defaults(
            persist_dir=PERSIST_DIR.as_posix()
        )
        index = VectorStoreIndex.from_documents(
            self.documents, storage_context=storage_context, show_progress=True
        )

        index.storage_context.persist()
        return index

    # Initialize the base Agent class with model set to None because the IndexAgent
    # uses a custom query engine and does not require a separate model.
    def __init__(self, **kwargs):
        super().__init__(model=None, **kwargs)
        self.setup_models()
        self.logger = self.setup_logging()
        set_global_handler("simple", logger=self.logger)
        self.documents = self.load_documents()
        self.SourceIndex = self.setup_index()
        self.SourceQuery = self.SourceIndex.as_query_engine()
        self.SourceChat = self.SourceIndex.as_chat_engine(chat_mode=ChatMode.REACT, memory=memory)

    def execute(
        self,
        system_message: str = "",
        prompt_message: str = "",
        prefix_message: str = "",
    ):
        def execute_query():
            try:
                response = self.SourceChat.chat(prompt_message)
                return response.response if response and response.response else "None"
            except Exception as e:
                self.logger.error(f"Error querying SourceQuery: {e}")
                response = "None"
            # Use the SourceQuery to get a response

        return Response(lambda: execute_query())


indexAgent = IndexAgent()
