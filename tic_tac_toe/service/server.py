from tic_tac_toe.service.application_type import ApplicationType
from tic_tac_toe.message_handler.server_message_handler import ServerMessageHandler
from tic_tac_toe.message_handler.server_request_handler import ServerRequestHandler
import socket
import selectors
import traceback

class Server(ApplicationType):
    def __init__(self, listening_port):
        super().__init__()
        self.listening_port = listening_port
        #singleton server request handler to keep all states in sync
        self.server_request_handler = ServerRequestHandler()

    def start(self):
        print("Starting tic-tac-toe server")
        host = ''
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((host, self.listening_port))
        lsock.listen()
        print("listening on", (host, self.listening_port))
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    #only ran when a new socket is created with a new client
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except ConnectionResetError:
                            print(
                                "server: error, client", f"{message.addr}", "has unexpectedly closed its connection"
                            )

                            self.server_request_handler.remove_new_connected_client(message.addr)
                            message.close()

                        except Exception:
                            print(
                                "server: error: exception for",
                                f"{message.addr}:\n{traceback.format_exc()}",
                            )
                            message.close()


        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("accepted connection from", addr)
        conn.setblocking(False)
        server_message_handler = ServerMessageHandler(self.sel, conn, addr, self.server_request_handler)
        self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=server_message_handler)
        self.server_request_handler.add_new_connected_client(addr, server_message_handler)