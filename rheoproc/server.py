import os
import socket
import pickle
import bz2


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
            timestamp(f'Preparing result "{cache_path}"')
            with open(cache_path, 'rb') as f:
                data = f.read()

            timestamp('Compressing...')
            self.send_message(conn, m_type='status', status='Compressing...')
            orig_size = len(data)
            data = bz2.compress(data)
            timestamp(f'Compressed {len(data)*100//orig_size}%')

            timestamp('Sending preamble to client')
            self.send_message(conn, m_type='preamble', size=len(data))

            timestamp('Sending result to client')
            conn.sendall(data)

        except Exception as e:
            # if something goes wrong, send exception back to client
            warning('An error occurred: {e}')
            self.send_message(conn, m_type='exception', exception=str(e))

        conn.close()


    def send_message(self, conn, *, m_type, **kwargs):
        data = {
            'type':m_type,
            **kwargs
        }
        data = pickle.dumps(data)
        data = bz2.compress(data)
        data += b'\0'
        conn.sendall(data)


    def stop(self):
        self.running = False

