from message import MessageTransformer, Message
from message import Conversation, ConversationTransformer


def test_message_to_string():
    transformer = MessageTransformer()
    message = Message(text="Hello, world!", role="user")
    expected_string = "USER: Hello, world!\n\n"
    assert transformer.message_to_string(message) == expected_string


def test_string_to_message():
    transformer = MessageTransformer()
    string = "USER: Hello, world!\n\n"
    expected_message = Message(text="Hello, world!", role="user")
    assert transformer.string_to_message(string) == expected_message


def test_conversation_to_string():
    transformer = MessageTransformer()
    conversation_transformer = ConversationTransformer(transformer)
    message1 = Message(text="Hello", role="user")
    message2 = Message(text="Hi", role="agent")
    conversation = Conversation(messages=[message1, message2])
    expected_string = "USER: Hello\n\nASSISTENT: Hi\n\n"
    assert conversation_transformer.conversation_to_string(conversation) == expected_string


def test_string_to_conversation():
    transformer = MessageTransformer()
    conversation_transformer = ConversationTransformer(transformer)
    string = "USER: Hello\n\nASSISTENT: Hi\n\n"
    expected_message1 = Message(text="Hello", role="user")
    expected_message2 = Message(text="Hi", role="agent")
    expected_conversation = Conversation(messages=[expected_message1, expected_message2])
    assert conversation_transformer.string_to_conversation(string) == expected_conversation
