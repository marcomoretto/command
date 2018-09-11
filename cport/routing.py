from channels.routing import include

from command.routing import channel_routing

channel_routing = [
    include(channel_routing)
]