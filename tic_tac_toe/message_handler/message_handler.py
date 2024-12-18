from abc import ABC, abstractmethod
import sys
import selectors
import json
import io
import struct
import logging

class MessageHandler(ABC):
    def __init__(self, selector, sock, addr):
        self.logger = logging.getLogger('app')
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._json_header_len = None
        self.json_header = None

    def process_events(self):
        self.read()
        self.write()

    def read(self):
        self._read()

        if self._json_header_len is None:
            self.process_protoheader()

        if self._json_header_len is not None:
            if self.json_header is None:
                self.process_jsonheader()

        # Reset json header length now that headers have been read
        self._json_header_len = None

    @abstractmethod
    def write(self):
        ...

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            self.logger.info(f'sending {repr(self._send_buffer)} to {self.addr}')
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message


    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._json_header_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._json_header_len
        if len(self._recv_buffer) >= hdrlen:
            self.json_header = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.json_header:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def close(self):
        self.logger.info(f'closing connection to {self.addr}')
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            self.logger.error(f'error: selector.unregister() exception for {self.addr}: {repr(e)}')

        try:
            self.sock.close()
        except OSError as e:
            self.logger.error(f'error: socket.close() exception for {self.addr}: {repr(e)}')
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None
