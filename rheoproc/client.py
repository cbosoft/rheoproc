import socket
import pickle

from rheoproc.port import PORT

def get_from_server(server_addr, *args, **kwargs):
    data = (args, kwargs)
    data_encoded = pickle.dumps(data)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect( (server_addr, PORT) )
        print(f'Sending query to server at {server_addr}:{PORT}')
        s.sendall(data_encoded)

        print(f'Receiving result...')
        data = bytearray()
        BUFFLEN = 4096
        while part := s.recv(BUFFLEN):
            data.extend(part)

    print(f'got {len(data)/1024/1024:.5f} MB back')

    data = pickle.loads(data)
    if isinstance(data, str):
        raise Exception(data)
    return data
