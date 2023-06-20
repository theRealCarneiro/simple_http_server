RES_TYPES = {200: 'OK', 404: 'NOT FOUND'}


class Response:
    def __init__(self, status, content_type=None, data=None):
        self.status = status
        self.content_type = content_type
        self.data = data

    def __bytes__(self):
        res = []
        res.append(f'HTTP/1.1 {self.status} {RES_TYPES[self.status]}'.encode())
        if self.content_type is not None:
            res.append(f'Content-Type: {self.content_type}'.encode())
        res.append(b'')

        if self.data is not None:
            res.append(self.data)

        return b'\r\n'.join(res)
