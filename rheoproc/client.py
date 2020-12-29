import socket
import pickle
import bz2

from rheoproc.port import PORT
from rheoproc.progress import ProgressBar
from rheoproc.error import timestamp

def get_from_server(server_addr, *args, **kwargs):
    data = (args, kwargs)
    data_encoded = pickle.dumps(data)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect( (server_addr, PORT) )
        timestamp(f'Querying rheoproc server at {server_addr}:{PORT}')
        s.sendall(data_encoded)

        BUFFLEN = 4096
        size = -1
        while msg_data := s.recv(BUFFLEN):
            msg = pickle.loads(bz2.decompress(msg_data))
            if msg['type'] == 'exception':
                raise Exception(msg['exception'])
            elif msg['type'] == 'status':
                timestamp('remote:', msg['status'])
            elif msg['type'] == 'preamble':
                size = msg['size']
                break

        timestamp(f'Downloading {size/1024/1024:.3f} MB')

        data = bytearray()
        div = 1
        if size > 1024:
            if size > 1024*1024:
                div = 1024*1024
            else:
                div = 1024
        pb = ProgressBar(size//div)
        i = 0
        while part := s.recv(BUFFLEN):
            data.extend(part)
            i += 1
            if i > 1000:
                i = 0
                npos = len(data)//div
                if npos != pb.pos:
                    pb.update(npos)
        pb.update(pb.length)

    try:
        timestamp('Decompressing data')
        data = bz2.decompress(data)
    except Exception as e:
        timestamp(f'Error while decompressing: {e}')
        pass
    data = pickle.loads(data)
    if isinstance(data, str):
        raise Exception(data)
    return data
