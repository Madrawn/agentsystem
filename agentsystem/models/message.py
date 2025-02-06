""" 
Provides classes for handling the transformation of prompts/completions strings into message objects and vice versa.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class Message():
    """A class that represents a message object represents a single message in a chat conversation.
    Every message object has a text attribute that contains the message text.
    A role attribute that contains the role of the speaker (e.g., user, system or agent).
    """
    text: str
    role: str

@dataclass
class Conversation():
    """A class that represents a conversation object represents a conversation between two or more speakers.
    Every conversation object has a list of messages attribute that contains the messages in the conversation.
    """
    messages: List[Message]

class MessageTransformer():
    """A class that provides methods for transforming messages into strings and vice versa.
    There are three possible roles for a speaker: user, system, and agent.
    Each role has a corresponding prefix that is added to the message text.
    When converting a message the base template looks like this:
    f"{role_prefix}{message_text}{role_suffix}"
    A MessageTransformer has to be initialized with a dictionary that maps roles to their corresponding prefixes.
    The prefix and suffix should contain any separators like spaces, colons, newlines, etc such that the message text only contains 
    the actual message.
    """
    def __init__(self, role_pre_and_suffixes: dict[str, tuple[str, str]] = {"user": ("USER: ", "\n\n"), "system": ("<<SYS>>", "<</SYS>>\n"), "agent": ("ASSISTENT: ", "\n\n")}):
        """Initializes a MessageTransformer with a dictionary that maps roles to their corresponding prefixes.
        """
        self.role_pre_and_suffixes = role_pre_and_suffixes

    def message_to_string(self, message: Message) -> str:
        """Converts a message object into a string.
        """
        (role_prefix, role_suffix) = self.role_pre_and_suffixes.get(message.role, "")
        return f"{role_prefix}{message.text}{role_suffix}"

    def string_to_message(self, string: str) -> Message:
        """Converts a string into a message object.
        """
        role = None
        message_text = string

        for role_key, (role_prefix, role_suffix) in self.role_pre_and_suffixes.items():
            if string.startswith(role_prefix) and string.endswith(role_suffix):
                role = role_key
                message_text = string[len(role_prefix):-len(role_suffix)]
                break

        return Message(text=message_text, role=role)

class ConversationTransformer():
    """A class that provides methods for transforming conversations into strings and vice versa using a MessageTransformer.
    """
    def __init__(self, message_transformer: MessageTransformer, message_seperator: str = ""):
        """Initializes a ConversationTransformer with a MessageTransformer.
        """
        self.message_transformer = message_transformer
        self.message_seperator = message_seperator

    def conversation_to_string(self, conversation: Conversation) -> str:
        """Converts a conversation object into a string.
        """
        message_strings = []
        for message in conversation.messages:
            message_string = self.message_transformer.message_to_string(message)
            message_strings.append(message_string)
        return self.message_seperator.join(message_strings)

    def string_to_conversation(self, string: str) -> Conversation:
        """Converts a string into a conversation object.
        """
        messages = []
        while string:
            # Strip the message separator from the start of the string
            string = string.lstrip(self.message_seperator)
            for role, (prefix, suffix) in self.message_transformer.role_pre_and_suffixes.items():
                if string.startswith(prefix):
                    suffix_index = string.find(suffix)
                    if suffix_index == -1:
                        raise ValueError(f"Missing suffix for role '{role}'")
                    message_text = string[len(prefix):suffix_index]
                    messages.append(Message(text=message_text, role=role))
                    string = string[suffix_index + len(suffix):]
                    break
            else:
                raise ValueError("Input string is not in the expected format")
        return Conversation(messages=messages)