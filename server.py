from tic_tac_toe.application.application_type import ApplicationType
from tic_tac_toe.message_handler.server.server_message_handler import ServerMessageHandler
from tic_tac_toe.message_handler.server.server_synchronizer import ServerSynchronizer
import socket
import selectors
import traceback
import sys
import logging
import datetime

class Server(ApplicationType):
    def __init__(self, listening_port):
        super().__init__()
        self.listening_port = listening_port
        #singleton server request handler to keep all states in sync
        self.server_request_handler = ServerSynchronizer()

    def start(self):
        self.logger.info("Starting tic-tac-toe server")
        host = ''
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((host, self.listening_port))
        lsock.listen()
        self.logger.info(f'listening on {(host, self.listening_port)}')
        print("Server has started")
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    #only ran when a new socket is created with a new client
                    if key.data is None:
                        self._accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events()
                        except ConnectionResetError:
                            self.logger.error(f'server: error, client {message.addr} has unexpectedly closed its connection')
                            self.server_request_handler.remove_connected_client(message.addr)
                            message.close()

                        except Exception:
                            self.logger.error(f'server: error: exception for {message.addr}:\n{traceback.format_exc()}')
                            message.close()


        except KeyboardInterrupt:
            self.logger.error("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

    def _accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        self.logger.info(f'accepted connection from {addr}')
        conn.setblocking(False)
        server_message_handler = ServerMessageHandler(self.sel, conn, addr, self.server_request_handler)
        self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=server_message_handler)
        self.server_request_handler.add_new_connected_client(addr, server_message_handler)


def main():
    if len(sys.argv) < 2:
        sys.exit('Not enough arguments: <listening port>')

    #create app logger
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)
    log_name = datetime.datetime.now().strftime('server_%d_%m_%Y_%H_%M_%S.log')
    fh = logging.FileHandler(log_name)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    server = Server(int(sys.argv[1]))
    server.start()

if __name__ == '__main__':
    main()