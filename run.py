import logging
import configparser
import asyncio

from aiohttp import web

import filething

# configure logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

if __name__ == '__main__':
    app = web.Application()
    loop = asyncio.get_event_loop()

    config = configparser.ConfigParser()
    config.read('filething.ini')

    filething = filething.Server(loop, app, config)
    filething.run()
