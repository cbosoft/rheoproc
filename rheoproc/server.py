# rheoproc.server
# remote processing server - class is created and run when rheoproc module is called as a program: 'python -m rheoproc'

import os
import socket
import pickle
import json
from zlib import compress, decompress
import time


from rheoproc.port import PORT
from rheoproc.query import query_db
from rheoproc.error import timestamp, warning

def fmt_time(t : int):
    if t > 60:
        return f'{t//60}m {t%60}s'
    return f'{t}s'



class Server:


    def __init__(self):
        self.running = False
        timestamp('Procserver started')
        self.conn = None
        self.addr = None


    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', PORT))
            s.listen()
            timestamp(f'Listening on {PORT}')
            self.running = True
            while self.running:
                try:
                    self.conn, self.addr = s.accept()
                    self.handle_connection()
                    self.conn.close()
                    self.conn = None
                except KeyboardInterrupt:
                    break
                except Exception:
                    pass



    def handle_connection(self):
        # Get query information
        data = self.conn.recv(4096)
        args, kwargs = pickle.loads(data)

        self.status('Querying database.')

        kwargs['returns'] = 'cache_path'
        try:
            cache_path = query_db(*args, **kwargs)
            self.status('Preparing result.')
            with open(cache_path, 'rb') as f:
                data = f.read()

            self.status('Compressing...')
            orig_size = len(data)
            before = time.time()
            data = compress(data, 1)
            after = time.time()
            dt = int(after - before)
            self.status(f'Compressed to {len(data)*100//orig_size}% in {fmt_time(dt)}')

            self.status('Sending result')
            self.send_message(m_type='preamble', size=len(data))
            self.conn.sendall(data)

        except Exception as e:
            # if something goes wrong, send exception back to client
            warning(f'An error occurred: {e}')
            self.send_message(m_type='exception', exception=str(e))


    def send_message(self, *, m_type, **kwargs):
        data = {
            'type':m_type,
            **kwargs
        }
        data = json.dumps(data).encode()
        self.conn.sendall(data)


    def status(self, status_msg):
        timestamp(status_msg)
        self.send_message(m_type='status', status=status_msg)


    def stop(self):
        self.running = False

