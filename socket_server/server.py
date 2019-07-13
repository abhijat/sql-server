import logging
import socketserver
import sys

from query_parser.parser import QueryParser


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        logging.info(f'incoming connection from {self.request.getpeername()}')
        self.data = self.request.recv(4096).strip()
        logging.info(f'serving query {self.data}')

        queries = QueryParser().parse(self.data.decode('ascii'))
        for query in queries:
            response = '\n'.join(query.execute())
            self.request.sendall(response.encode('ascii'))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <PORT>')
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print(f'invalid port {sys.argv[1]}')
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(name)s %(message)s')

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('localhost', port), RequestHandler) as server:
        logging.info(f'listening on port {port}')
        server.serve_forever()
