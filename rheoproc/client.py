import socket
import pickle

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
        size_enc = s.recv(BUFFLEN)
        size = pickle.loads(size_enc)
        if isinstance(size, str):
            raise Exception(size)

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

    data = pickle.loads(data)
    if isinstance(data, str):
        raise Exception(data)
    return data
