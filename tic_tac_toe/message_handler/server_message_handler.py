from tic_tac_toe.message_handler.message_handler import MessageHandler

class ServerMessageHandler(MessageHandler):
    def __init__(self, selector, sock, addr):
        super().__init__(selector, sock, addr)
        self.request = None
        self.response_created = False

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()

        self._write()

        #reset response created now that it was written to the buffer
        self.response_created = False
        # Set selector to listen for read events, we're done writing.
        self._set_selector_events_mask("r")

    def read(self):
        super().read()

        if self.json_header:
            if self.request is None:
                self.process_request()

    def process_request(self):
        content_len = self.json_header["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return

        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]

        encoding = self.json_header["content-encoding"]
        self.request = self._json_decode(data, encoding)
        print("received request", repr(self.request), "from", self.addr)

        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        response = self._create_response_json_content()
        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message

        #clear request contents now that response has been created
        self.json_header = None
        self.request = None

    def _create_response_json_content(self):
        action = self.request.get("action")
        if action == "register":
            query = self.request.get("value")
            content = f'"{query}" has been registered.'
        else:
            content = f'Error: invalid action "{action}".'

        return self._create_response_body(content)

    def _create_response_body(self, content):
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode({"result": content}, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response