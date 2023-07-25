# UWebServer for <img src="https://www.raspberrypi.com/app/uploads/2021/10/cropped-Raspberry-Pi-Favicon-100x100-1-300x300.png" alt="drawing" width="35"/> Pico W

The `UWebServer` is a minimalistic web server for handling basic HTTP requests, implemented in MicroPython. Currently it handles GET, HEAD, OPTIONS and POST requests. This project was made to work with Raspberry Pi Pico W but should work with any similar device that supports MicroPython.

## Getting Started

Before you start, save the uwebserver.py in `lib` directory on your Pico. Then, import the necessary modules and the `UWebServer` class.

```python
import network
import socket
import gc
import ujson
import os
from uwebserver import UWebServer
```

### Initialize the server
To start, you'll need to create an instance of UWebServer. You can specify the port, the request size limit, and the static directory.

```python
server = UWebServer(port=80, static_dir='static')
```

### Define routes
Define routes using the route decorator, providing the path and the method as arguments. The function decorated will handle requests to that path.

```python
@server.route('/', 'GET')
def handle_root():
    return 'Welcome to my web server!', 'text/html', "200 OK"

@server.route("/api/read", "GET")
def api_read():
    response = readings
    return ujson.dumps(response), "application/json", "200 OK"

@server.route("/api/write", "POST")
def api_write(data):
    response = {"data_received": data}
    return ujson.dumps(response), "application/json", "200 OK"
```

### Start the server
Start the server using the start method. This will keep the server running indefinitely.

```
server.start()
```

### Handling static files
If the static_dir attribute is set when initializing UWebServer, GET requests to paths that match a file in the directory will respond with that file's contents.

For example, if static_dir is set to 'static' and there is a file 'static/index.html', a GET request to /index.html or / will respond with the contents of the file.

## Example code (RPi Pico)
See `example.py` that allows you to control the internal LED via browser.

## Links
* https://projects.raspberrypi.org/en/projects/get-started-pico-w
