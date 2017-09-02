import logging
import sys
import configparser
import asyncio

from aiohttp import web

import filething

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

async def hello(request):
    return web.Response(text="Welcome to a filething server. https://github.com/lnmds/filething")

if __name__ == '__main__':
    app = web.Application()
    loop = asyncio.get_event_loop()

    config = configparser.ConfigParser()
    config.read('filething.ini')

    filething = filething.Server(loop, app, config)

    app.router.add_get('/', hello)

    filething.run()

