import time

from tic_tac_toe.service.application_type import ApplicationType
from tic_tac_toe.message_handler.client_message_handler import ClientMessageHandler
from threading import Thread
import selectors
import traceback
import socket

class Client(ApplicationType):
    def __init__(self, server_host, server_port):
        super().__init__()
        self.server_host = server_host
        self.server_port = server_port
        self.client_message_handler = None
        self.client_socket_thread = None

    def start(self):
        print("Starting tic-tac-toe client")
        request = self.create_request("register", "player")
        self.start_connection(self.server_host, self.server_port)
        self.client_socket_thread = Thread(target=self.process_socket_traffic)
        self.client_socket_thread.start()

        #while client is still connected to the server
        while self.client_message_handler is not None:
            # TODO: get player name for register and then get player input before sending messages
            self.client_message_handler.write_request(request)
            #time.sleep(5)

        self.client_socket_thread.join()

    def start_connection(self, host, port):
        addr = (host, port)
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.client_message_handler = ClientMessageHandler(self.sel, sock, addr)
        self.sel.register(sock, events, data=self.client_message_handler)

    def process_socket_traffic(self):
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

    def create_request(self, action, value):
        if action == "register":
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, value=value),
            )