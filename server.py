import os
import sys
import socket
import asyncio
import datetime
import platform
import html as h
import http

HOST = 'localhost'
PORT = 8000
# DIRECTORY = '/home/gabriel'  # The directory you want to serve files from


def list_directory(path):
    # Get the list of files and directories in the given path
    files = os.listdir(path)

    # Generate HTML for displaying the directory listing
    html = h.h1('File explorer')
    html += '<ul>'

    for item in files:
        item_path = os.path.join(path, item)
        html += h.li(h.ahref(item + ('/' if os.path.isdir((item_path)) else '')))

    html += '</ul>'
    return html.encode('utf-8')


# Extract the HTTP request header
def get_http_header(request):

    headers = request.split('\r\n')
    http_header = '<h1>HTTP Request Header</h1>'
    http_header += '<ul>'

    for header in headers:
        http_header += f'{header}<br>'

    http_header += '</ul>'
    return http_header.encode('utf-8')


def handle_request(request):

    # Extract the requested file path from the HTTP request
    path = request.split()[1]

    # Build the absolute path to the file or directory
    resource_path = os.path.join(DIRECTORY, path[1:])
    last = os.path.basename(os.path.normpath(resource_path))

    # If the requested path is /HEADER, return the HTTP request header
    if last == 'HEADER':
        res = http.Response(200, 'text/html', get_http_header(request))

    # If the requested path is /Hello, return "Hello"
    elif path == '/Hello':
        res = http.Response(200, 'text/plain', 'Hello'.encode('utf-8'))

    # If the requested path is /Info, return server information
    elif path == '/Info':
        server_info = f'Date: {datetime.datetime.now()}\n'
        server_info += f'Server User: {os.getlogin()}\n'
        server_info += f'Server OS: {platform.platform()}'
        res = http.Response(200, 'text/plain', server_info.encode('utf-8'))

    # If the requested resource is a directory, list its contents
    elif os.path.isdir(resource_path):
        res = http.Response(200, 'text/html', list_directory(resource_path))

    # If the requested resource is a file, open and send its contents
    elif os.path.exists(resource_path):
        with open(resource_path, 'rb') as file:
            file_data = file.read()
        res = bytes(http.Response(200, None, file_data))

    # If the requested resource doesn't exist, return a 404 Not Found response
    else:
        res = http.Response(404)

    # Send the HTTP response
    return bytes(res)


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:

    # Read incoming request
    msg = await reader.read(1024)
    req = msg.decode()    

    # Print client and req info
    # addr, port = writer.get_extra_info('peername')
    # print(f'Client connected: {addr} {port}')
    # print(f'Request received: {req}')

    # Handle request
    res = handle_request(req)

    # Send response to client
    writer.write(res)
    await writer.drain()

    # Close connection
    writer.close()
    await writer.wait_closed()


async def run_server() -> None:
    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    DIRECTORY = sys.argv[1]
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_server())
