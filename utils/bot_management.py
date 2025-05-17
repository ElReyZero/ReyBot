import asyncio
import os
import sys
import time
from typing import Callable


async def restart_program(exit_callback: Callable):
    def restart():
        time.sleep(5)
        os.execv(sys.executable, ['python3'] + sys.argv)

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, restart)
    await exit_callback()
