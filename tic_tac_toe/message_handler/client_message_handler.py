from tic_tac_toe.message_handler.message_handler import MessageHandler
import struct

class ClientMessageHandler(MessageHandler):
    def __init__(self, selector, sock, addr):
        super().__init__(selector, sock, addr)
        self.request = None
        self.response = None
        self.waiting_for_response = False

    def write_request(self, request):
        self.request = request

    def write(self):
        if self.request and not self.waiting_for_response:
            # Set selector to listen for write events, we're done reading.
            self.queue_request()

        self._write()

        if self.waiting_for_response:
            if not self._send_buffer:
                # Set selector to listen for read events, we're done writing.
                self._set_selector_events_mask("r")

    def read(self):
        super().read()

        if self.json_header:
            if self.response is None:
                self.process_response()

        if not self.waiting_for_response and self.response is None:
            self._set_selector_events_mask("w")

    def queue_request(self):
        content = self.request["content"]
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]
        req = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": content_type,
            "content_encoding": content_encoding,
        }
        message = self._create_message(**req)
        self._send_buffer += message

        self.request = None
        self.waiting_for_response = True

    def process_response(self):
        content_len = self.json_header["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]

        # process json response
        encoding = self.json_header["content-encoding"]
        self.response = self._json_decode(data, encoding)
        print("received response", repr(self.response), "from", self.addr)
        self._process_response_json_content()

        self.json_header = None
        self.waiting_for_response = False
        self.response = None

        # Close when response has been processed
        #self.close()

    def _process_response_json_content(self):
        content = self.response
        result = content.get("result")
        print(f"got result: {result}")