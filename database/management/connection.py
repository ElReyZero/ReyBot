from mongoengine import connect, disconnect
from config import database
from datetime import datetime
from discord.ext.tasks import loop

class Connections:
    def __init__(self):
        self.connections = {
            "genshin": {
                "connected": False,
                "last_used": None,
                "connection_name": None
            }
        }
        self.used_connections = list()

    @loop(minutes=1)
    async def disconnect_all(self):
        for connection in self.connections.keys():
            if self.connections[connection]["connected"] and (datetime.now() - self.connections[connection]["last_used"]).total_seconds() > 300:
                self.disconnect(connection)

    def connect(self, name):
        try:
            if not self.connections[name]["connected"]:
                self.connections[name]["connected"] = True
                self.connections[name]["last_used"] = datetime.now()
                if not "default" in self.used_connections:
                    self.used_connections.append("default")
                    self.connections[name]["connection_name"] = "default"
                else:
                    self.connections[name]["connection_name"] = name
                connect(db=name, host=database['host'], alias=self.connections[name]["connection_name"])
        except KeyError:
            raise Exception(f"Connection {name} not found.") 

    def disconnect(self, name):
        try:
            if self.connections[name]["connected"]:
                self.connections[name]["connected"] = False
                disconnect(alias=self.connections[name]["connection_name"])
        except KeyError:
            raise Exception(f"Connection {name} not found.") 

def set_connections():
    connections = Connections()
    return connections