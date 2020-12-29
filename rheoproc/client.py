import socket
import pickle

from rheoproc.port import PORT

def get_from_server(server_addr, *args, **kwargs):
    data = (args, kwargs)
    data_encoded = pickle.dumps(data)
    print(f'sending data ({len(data_encoded)} bytes) to server at {server_addr}:{PORT}')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect( (server_addr, PORT) )
        s.sendall(data_encoded)

        data = bytearray()
        BUFFLEN = 1024
        while part := s.recv(BUFFLEN):
            data.extend(part)
            if len(part) < BUFFLEN:
                break

        print(f'got {len(data)/1024/1024:.5f} MB back')

    data = pickle.loads(data)
    return data
