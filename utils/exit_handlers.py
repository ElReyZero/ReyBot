import sys
from signal import signal, SIGINT, SIGTERM
from atexit import register
from database.management.connection import db_exit_handler

def main_exit_handler(connections: dict):
    register(db_exit_handler, connections)
    signal(SIGTERM, lambda x,y: sys.exit(0))
    signal(SIGINT, lambda x,y: sys.exit(0))