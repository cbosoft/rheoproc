import socket
import pickle
import time


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
        data = conn.recv(1024)
        args, kwargs = pickle.loads(data)
        timestamp(f'Querying database ({args}, {kwargs}) for {addr[0]}')
        kwargs['returns'] = 'cache_path'
        cache_path = query_db(*args, **kwargs)
        timestamp(f'Sending result "{cache_path}"')
        with open(cache_path, 'rb') as f:
            conn.sendfile(f)
        time.sleep(10)
        conn.close()


    def stop(self):
        self.running = False

