#!/usr/bin/env python

import time

from circuits import Component
from circuits.web.servers import Server
from circuits.net.sockets import Connect, Write
from circuits.web.controllers import Controller
from circuits.web.websockets import WebSocketClient, WebSocketsDispatcher


class Echo(Component):

    channel = "ws"

    def read(self, sock, data):
        self.fire(Write(sock, "Received: " + data))


class Root(Controller):

    def index(self):
        return "Hello World!"


class WSClient(Component):

    response = None

    def read(self, data):
        self.response = data


def test1(webapp):
    server = Server(("localhost", 8123))
    Echo().register(server)
    Root().register(server)
    WebSocketsDispatcher("/websocket").register(server)
    server.start()

    client = WebSocketClient("ws://localhost:8123/websocket")
    wsclient = WSClient().register(client)
    client.start()
    client.fire(Connect())
    client.fire(Write("Hello!"), "ws")
    for i in range(100):
        if wsclient.response is not None:
            break
        time.sleep(0.010)
    assert wsclient.response is not None
    client.stop()

    server.stop()
