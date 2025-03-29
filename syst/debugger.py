# logger_server.py
import logging
import logging.handlers
import socketserver
import struct
import pickle

class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk += self.connection.recv(slen - len(chunk))
            obj = pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            self.process_record(record)

    def process_record(self, record):
        logger = logging.getLogger(record.name)
        logger.handle(record)

class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    def __init__(self, host='localhost', port=9020, handler=LogRecordStreamHandler):
        super().__init__((host, port), handler)

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('log.txt'),
            logging.StreamHandler()
        ]
    )
    server = LogRecordSocketReceiver()
    print("Logging server started on port 9020")
    server.serve_forever()

if __name__ == "__main__":
    main()