from queue import Queue
from tic_tac_toe.message_handler.message_handler import MessageHandler

#handles messages to/from client
class ServerMessageHandler(MessageHandler):
    def __init__(self, selector, sock, addr, server_request_handler):
        super().__init__(selector, sock, addr)
        #queue for internal server alerts that need to be sent to the client
        self.request_queue = Queue()
        self.server_request_handler = server_request_handler

    def add_internal_request(self, request):
        self.request_queue.put(request)

    def write(self):
        #process requests and send responses back to client
        if not self.request_queue.empty():
            self._create_response(self.request_queue.get())

        self._write()

    def read(self):
        super().read()

        #process client request
        if self.json_header:
            self._process_request()

    def _process_request(self):
        content_len = self.json_header["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return

        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]

        encoding = self.json_header["content-encoding"]
        request = self._json_decode(data, encoding)
        self.logger.info("received request", repr(request), "from", self.addr)
        self.request_queue.put(request)

        #clear request contents now that request has been read and queued
        self.json_header = None

    def _create_response(self, request):
        response = self._create_response_json_content(request)
        message = self._create_message(**response)
        self._send_buffer += message

    #process request in server request singleton and respond
    def _create_response_json_content(self, request):
        content = self.server_request_handler.process_client_request(self.addr, request)
        return self._create_response_body(content)

    def _create_response_body(self, content):
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response