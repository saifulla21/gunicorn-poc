import base64
import errno
import re
from gunicorn.workers.async import ALREADY_HANDLED
from hashlib import sha1
import socket
import logging
from lib.websocket import WebSocket


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] [%(levelname)-7s] - %(process)d:%(threadName)s:%(name)s:%(funcName)s - %(message)s')
WS_KEY = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
class WebSocketWSGI(object):
    def __init__(self, handler):
        self.handler = handler

    def verify_client(self, ws):
        pass

    def _get_key_value(self, key_value):
        if not key_value:
            return
        key_number = int(re.sub("\\D", "", key_value))
        spaces = re.subn(" ", "", key_value)[1]
        if key_number % spaces != 0:
            return
        part = key_number / spaces
        return part

    def __call__(self, environ, start_response):
        if not (environ.get('HTTP_CONNECTION').find('Upgrade') != -1 and
            environ['HTTP_UPGRADE'].lower() == 'websocket'):
            # need to check a few more things here for true compliance
            start_response('400 Bad Request', [('Connection','close')])
            return []

        sock = environ['gunicorn.sock']

        version = environ.get('HTTP_SEC_WEBSOCKET_VERSION')

        ws = WebSocket(sock, environ, version)

        handshake_reply = ("HTTP/1.1 101 Switching Protocols\r\n"
                   "Upgrade: websocket\r\n"
                   "Connection: Upgrade\r\n")

        key = environ.get('HTTP_SEC_WEBSOCKET_KEY')
        if key:
            ws_key = base64.b64decode(key)
            if len(ws_key) != 16:
                start_response('400 Bad Request', [('Connection','close')])
                return []

            protocols = []
            subprotocols = environ.get('HTTP_SEC_WEBSOCKET_PROTOCOL')
            ws_protocols = []
            if subprotocols:
                for s in subprotocols.split(','):
                    s = s.strip()
                    if s in protocols:
                        ws_protocols.append(s)
            if ws_protocols:
                handshake_reply += 'Sec-WebSocket-Protocol: %s\r\n' % ', '.join(ws_protocols)

            exts = []
            extensions = environ.get('HTTP_SEC_WEBSOCKET_EXTENSIONS')
            ws_extensions = []
            if extensions:
                for ext in extensions.split(','):
                    ext = ext.strip()
                    if ext in exts:
                        ws_extensions.append(ext)
            if ws_extensions:
                handshake_reply += 'Sec-WebSocket-Extensions: %s\r\n' % ', '.join(ws_extensions)

            handshake_reply +=  (
                "Sec-WebSocket-Origin: %s\r\n"
                "Sec-WebSocket-Location: ws://%s%s\r\n"
                "Sec-WebSocket-Version: %s\r\n"
                "Sec-WebSocket-Accept: %s\r\n\r\n"
                 % (
                    environ.get('HTTP_ORIGIN'),
                    environ.get('HTTP_HOST'),
                    ws.path,
                    version,
                    base64.b64encode(sha1(key + WS_KEY).digest())
                ))

        else:

            handshake_reply += (
                       "WebSocket-Origin: %s\r\n"
                       "WebSocket-Location: ws://%s%s\r\n\r\n" % (
                            environ.get('HTTP_ORIGIN'),
                            environ.get('HTTP_HOST'),
                            ws.path))

        sock.sendall(handshake_reply)

        try:
            self.handler(ws)
        except socket.error as e:
            if e[0] != errno.EPIPE:
                raise
        # use this undocumented feature of grainbows to ensure that it
        # doesn't barf on the fact that we didn't call start_response
        return ALREADY_HANDLED