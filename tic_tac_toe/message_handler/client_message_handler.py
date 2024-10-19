from queue import Queue
from tic_tac_toe.message_handler.message_handler import MessageHandler

class ClientMessageHandler(MessageHandler):
    def __init__(self, selector, sock, addr):
        super().__init__(selector, sock, addr)
        self.request_queue = Queue()

    def write_request(self, request):
        self.request_queue.put(request)

    def write(self):
        if not self.request_queue.empty():
            #write request to buffer
            self.queue_request()
            self._write()


    def read(self):
        super().read()

        #process server response
        if self.json_header:
            self.process_response()

    def queue_request(self):
        request = self.request_queue.get()
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

    def process_response(self):
        content_len = self.json_header["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return

        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]

        # process json response
        encoding = self.json_header["content-encoding"]
        response = self._json_decode(data, encoding)
        print("received response", repr(response), "from", self.addr)
        self._process_response_json_content(response)

        self.json_header = None

    def _process_response_json_content(self, response):
        result = response.get("success")
        data = response.get("data")
        print(f"got result: {response}")