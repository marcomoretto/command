from channels.routing import route

from command.consumers import *

channel_routing = [
    route("websocket.connect", ws_connect, path=r"^/ws/$"),
    route("websocket.receive", ws_receive, path=r"^/ws/$"),
    route("websocket.disconnect", ws_disconnect, path=r"^/ws/$"),
]
