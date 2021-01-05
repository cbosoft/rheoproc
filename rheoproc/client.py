# rheoproc.client
# This file contains functions relevant to connecting to a remote processing server (see rheoproc.server)

import socket
import pickle
import json
from zlib import decompress
import time

from rheoproc.port import PORT
from rheoproc.progress import ProgressBar
from rheoproc.error import timestamp

def read_message(sock):
    data = b''
    while b := sock.recv(1):
        data += b
        s = b.decode()
        if s == '}':
            break
    return json.loads(data.decode())

class DownloadSpeedo:

    def __init__(self):
        self.start_time = time.time()


    def info(self, tot, current):
        dt = time.time() - self.start_time
        speed = current / dt
        unit = 'b'
        if speed > 1024:
            speed /= 1024
            unit = 'kb'
        if speed > 1024:
            speed /= 1024
            unit = 'Mb'
        return f'{speed:.1f} {unit}/s'


def get_from_server(server_addr, *args, timeout=10, **kwargs):
    data = (args, kwargs)
    data_encoded = pickle.dumps(data)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.connect( (server_addr, PORT) )
        timestamp(f'Querying rheoproc server at {server_addr}:{PORT}')
        s.sendall(data_encoded)

        BUFFLEN = 4096
        size = -1
        while True:
            msg = read_message(s)
            if msg['type'] == 'exception':
                raise Exception(msg['exception'])
            elif msg['type'] == 'status':
                timestamp('remote:', msg['status'])
            elif msg['type'] == 'preamble':
                size = msg['size']
                break

        unit = 'b'
        div = 1
        size_b = int(size)
        if size > 1024:
            size /= 1024
            div *= 1024
            unit = 'kb'
        if size > 1024:
            size /= 1024
            div *= 1024
            unit = 'Mb'
        if size > 1024:
            size /= 1024
            div *= 1024
            unit = 'Gb'

        timestamp(f'Downloading {size:.1f} {unit}')

        data = bytearray()
        ds = DownloadSpeedo()
        pb = ProgressBar(size_b + 1, info_func=ds.info)
        i = 0
        while part := s.recv(BUFFLEN):
            data.extend(part)
            i += 1
            if i > 1000:
                i = 0
                npos = len(data)
                if npos != pb.pos:
                    pb.update(npos)
        pb.update(pb.length)

    try:
        timestamp('Decompressing data')
        data = decompress(data)
    except Exception as e:
        timestamp(f'Error while decompressing: {e}')
        pass
    data = pickle.loads(data)
    if isinstance(data, str):
        raise Exception(data)
    return data
