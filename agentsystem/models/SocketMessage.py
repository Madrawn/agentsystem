from typing import TypeVar, Generic, Optional
import jsonpickle

T = TypeVar('T')


class SocketMessage(Generic[T]):
    """A class that represents a message to be sent over socket"""

    class SocketData(Generic[T]):
        """A class that holds the data and its type for a socket message"""

        def __init__(self, data: Optional[T]) -> None:
            """Initializes the socket data with the given data"""
            self.data_type: type[T] = type(data) # the type of the data
            self.data_value: Optional[T] = data # the value of the data

    def __init__(self, msg_type: str, data: Optional[T]) -> None:
        """Initializes the socket message with the given type and data"""
        self.msg_type = msg_type # the type or action key of the message
        self.socket_data = self.SocketData[T](data) # the socket data object

    def serialize(self) -> bytes:
        """Serializes the socket message to bytes using jsonpickle"""
        return jsonpickle.dumps(self).encode()

    @classmethod
    def from_byte(cls, bytes: bytes) -> "SocketMessage":
        """Deserializes the socket message from bytes using jsonpickle"""
        return cls.from_json(bytes.decode())

    @classmethod
    def from_json(cls, json: str) -> "SocketMessage":
        """Deserializes the socket message from json using jsonpickle"""
        return jsonpickle.loads(json, classes=cls)
