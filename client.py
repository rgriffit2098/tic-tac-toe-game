from tic_tac_toe.message.register import Register
from tic_tac_toe.application.application_type import ApplicationType
from tic_tac_toe.message_handler.client.client_message_handler import ClientMessageHandler
from threading import Thread
import selectors
import traceback
import socket
import sys

class Client(ApplicationType):
    def __init__(self, server_host, server_port):
        super().__init__()
        self.server_host = server_host
        self.server_port = server_port
        self.client_message_handler = None
        self.client_socket_thread = None

    def start(self):
        print("Starting tic-tac-toe client")
        print("What would you like your player name to be?")
        player_name = input()
        register_event = Register(player_name)
        request = self._create_request(register_event)
        self._start_connection(self.server_host, self.server_port)
        self.client_socket_thread = Thread(target=self._process_socket_traffic)
        self.client_socket_thread.start()

        #send register request
        self.client_message_handler.send_request(request)

        #while client is still connected to the server
        while self.client_message_handler is not None:
            one = 1
        #self.client_message_handler.send_request(request)

        self.client_socket_thread.join()

    def _start_connection(self, host, port):
        addr = (host, port)
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.client_message_handler = ClientMessageHandler(self.sel, sock, addr)
        self.sel.register(sock, events, data=self.client_message_handler)
        print("connection established with the server")

    def _process_socket_traffic(self):
        try:
            while True:
                events = self.sel.select(timeout=1)
                for key, mask in events:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        print(
                            "client: error: exception for",
                            f"{message.addr}:\n{traceback.format_exc()}",
                        )
                        message.close()
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    break

        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()
            self.client_message_handler = None

    def _create_request(self, event):
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=event.event_type.value, data=event.data),
        )

def main():
    if len(sys.argv) < 3:
        sys.exit('Not enough arguments: <server ip> <server port>')

    client = Client(sys.argv[1], int(sys.argv[2]))
    client.start()

if __name__ == '__main__':
    main()