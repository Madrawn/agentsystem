"""
This is the script that connects to the model process and sends the JSON data	
"""
from typing import Any
from agentsystem.agents.agents import Model

from agentsystem.models.Response import Response
from agentsystem.models.SocketMessage import SocketMessage
from agentsystem.app.socket.GenericSocket import GenericSocket


class SocketModel(Model):
    def __init__(self, port):
        # This is the script that connects to the model process and sends the
        # JSON data
        self.port = port

    def run(self, *args, **kwargs):
        return self._run(*args, **kwargs)

    def _run(
            self,
            system_message,
            prompt_message,
            prefix_message,
            **extra_args):
        # Create a socket object
        def send():
            with GenericSocket() as s:
                # Connect to the model process on port 1234
                s.connect('localhost', self.port)
                s.sock.settimeout(None)
                # Create a JSON data object
                data = SocketMessage("prompt_request", data={
                    "system_message": system_message,
                    "prompt_message": prompt_message,
                    "prefix_message": prefix_message,
                    "extra_args": extra_args
                }).serialize()
                # Convert the JSON data object to a JSON string

                # Send the JSON string to the socket
                s.mysend(data)

                # Receive the JSON string from the socket
                response: SocketMessage[dict[str, Any]
                                        ] = SocketMessage.from_byte(s.myreceive())

                # Print the response
                print(response.socket_data.data_value)

                # Close the socket
                return response.socket_data.data_value
        return Response(send)

    def interrupt(self) -> None:
        # Create a socket object
        print("Interrupting model")
        with GenericSocket() as interrupt_socket:

            # Connect to the model process on port 1234
            interrupt_socket.connect('localhost', self.port+1)

            # Create a JSON data object
            data = SocketMessage("interrupt", data={}).serialize()
            # Convert the JSON data object to a JSON string

            # Send the JSON string to the socket
            interrupt_socket.mysend(data)