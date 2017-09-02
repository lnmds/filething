import logging

import motor.motor_asyncio

log = logging.getLogger(__name__)

class Server:
    """Main Filething server class.
    
    This class holds all the server state to continue operating

    Attributes
    ----------
    ready: bool
        If the server is in a ready state for startup.

    db: `mongo database object`
    """
    def __init__(self, loop, app, config):
        self.loop = loop
        self.app = app
        self.config = config['filething']

        self.ready = False

        self.mongo = motor.motor_asyncio.AsyncIOMotorClient()
        self.db = self.mongo['filething']

    async def initialize(self):
        """Gather necessary server state."""
        log.info('Initializing')
        self.ready = True
        log.info('Ready!')

    def run(self):
        """Start the HTTP server.

        Raises
        ------
        RuntimeError
            If the server is not ready for startup.
        """
        handler = self.app.make_handler()
        f = self.loop.create_server(handler, \
            self.config['host'], self.config['port'])

        srv = None

        try:
            log.info('Running loop')
            self.loop.run_until_complete(self.initialize())

            srv = self.loop.run_until_complete(f)
            self.loop.run_forever()
        except:
            log.info('Shutting down.')
            srv.close()
            self.loop.run_until_complete(srv.wait_closed())
            self.loop.run_until_complete(self.app.shutdown())
            self.loop.run_until_complete(handler.shutdown(60.0))
            self.loop.run_until_complete(self.app.cleanup())

        self.loop.close()

