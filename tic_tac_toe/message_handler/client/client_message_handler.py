from queue import Queue
from tic_tac_toe.message_handler.message_handler import MessageHandler
from tic_tac_toe.message_handler.client.client_synchronizer import ClientSynchronizer

class ClientMessageHandler(MessageHandler):
    def __init__(self, selector, sock, addr):
        super().__init__(selector, sock, addr)
        self.request_queue = Queue()
        self.client_synchronizer = ClientSynchronizer()

    #sends requests to the server
    def send_request(self, request):
        self.request_queue.put(request)

    #checks to see if the player has successfully registered
    def is_registered(self):
        return self.client_synchronizer.is_registered()

    def register_response_received(self):
        return self.client_synchronizer.register_response_received()

    #gets a list of valid commands that can be output to the player
    def get_valid_commands(self):
        return self.client_synchronizer.get_valid_commands()

    #reads from server response queue and returns any responses that need to be
    #print out to the player
    def get_server_output(self):
        return self.client_synchronizer.get_server_output()

    #determines the possible moves that a player can make on the board
    def get_possible_moves_list(self):
        return self.client_synchronizer.get_possible_moves_list()

    def new_state_detected(self):
        return self.client_synchronizer.new_state_detected()

    #formats board with data provided
    def format_board(self, possible_moves_list):
        return self.client_synchronizer.format_board(possible_moves_list)

    # retrieves if the player has exited the game or not
    def player_has_exit_game(self):
        return self.client_synchronizer.player_has_exit_game()

    def write(self):
        if not self.request_queue.empty():
            #write request to buffer
            self._dequeue_request()

    def read(self):
        super().read()

        #process server response
        if self.json_header:
            self._process_response()

    #reads from request queue and sends it to server
    def _dequeue_request(self):
        request = self.request_queue.get()
        self.logger.info(f"Sending request to server: {request}")
        content = request["content"]
        content_type = request["type"]
        content_encoding = request["encoding"]

        req = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": content_type,
            "content_encoding": content_encoding,
        }

        message = self._create_message(**req)
        self._send_buffer += message
        self._write()

    #processes messages received from the server
    def _process_response(self):
        content_len = self.json_header["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return

        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]

        # process json response
        encoding = self.json_header["content-encoding"]
        response = self._json_decode(data, encoding)
        self.logger.info(f'received response {repr(response)} from {self.addr}')
        self._process_response_json_content(response)

        self.json_header = None

    def _process_response_json_content(self, response):
        self.client_synchronizer.process_server_message(response)