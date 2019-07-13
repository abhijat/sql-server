import logging
import socketserver
import sys

from query_parser.operators import configuration, InvalidStateException
from query_parser.parser import QueryParser


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        logging.info(f'incoming connection from {self.request.getpeername()}')
        self.data = self.request.recv(4096).strip()
        logging.info(f'serving query {self.data}')

        try:
            queries = QueryParser().parse(self.data.decode('ascii'))
            for query in queries:
                for row in query.execute():
                    self.request.sendall(row.encode('ascii'))
                    self.request.sendall(b'\r\n')
        except Exception as e:
            self.request.sendall(str(e).encode('ascii'))

        self.request.sendall(b'\r\n')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <PORT>')
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print(f'invalid port {sys.argv[1]}')
        sys.exit(1)

    if len(sys.argv) == 3:
        configuration['data_path'] = sys.argv[2]
    else:
        configuration['data_path'] = '..'

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(name)s %(message)s')

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('localhost', port), RequestHandler) as server:
        logging.info(f'listening on port {port}')
        server.serve_forever()
