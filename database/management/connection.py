from mongoengine import connect, disconnect
from config import database

class Connections:
    def __init__(self):
        self.connections = {
            "genshin": {
                "connected": False,
                "connection_name": None
            }
        }
        self.used_connections = list()

    def disconnect_all(self):
        for connection in self.connections.keys():
            if self.connections[connection]["connected"]:
                self.disconnect(connection)

    def connect(self, name):
        try:
            if not self.connections[name]["connected"]:
                self.connections[name]["connected"] = True
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

def exit_handler(connections):
    connections.disconnect_all()
