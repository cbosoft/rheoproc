import os
import socket
import pickle


from rheoproc.port import PORT
from rheoproc.query import query_db
from rheoproc.error import timestamp, warning


class Server:


    def __init__(self):
        self.running = False
        timestamp('Procserver started')


    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', PORT))
            s.listen()
            timestamp(f'Listening on {PORT}')
            self.running = True
            while self.running:
                conn, addr = s.accept()
                self.handle_connection(conn, addr)


    def handle_connection(self, conn, addr):
        # Get query information
        data = conn.recv(4096)
        args, kwargs = pickle.loads(data)

        timestamp(f'Querying database ({args}, {kwargs}) for {addr[0]}')

        kwargs['returns'] = 'cache_path'
        try:
            cache_path = query_db(*args, **kwargs)
            timestamp(f'Sending result "{cache_path}"')
            nbytes = os.path.getsize(cache_path)
            nbytes_encoded = pickle.dumps(nbytes)
            while len(nbytes_encoded) < 4096:
                nbytes_encoded += b'\0'
            conn.send(nbytes_encoded)

            with open(cache_path, 'rb') as f:
                conn.sendfile(f)

        except Exception as e:
            # if something goes wrong, send exception back to client
            se_enc = pickle.dumps(str(e))
            conn.sendall(se_enc)

        conn.close()


    def stop(self):
        self.running = False

