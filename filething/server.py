import logging
import random
import string

from aiohttp import web

log = logging.getLogger(__name__)

class Server:
    """Main Filething server class.

    This class holds all the server state to continue operating

    Attributes
    ----------
    ready: bool
        If the server is in a ready state for startup.
    """
    def __init__(self, loop, app, config):
        self.loop = loop
        self.app = app
        self.config = config['filething']

        self.ready = False

    async def initialize(self):
        """Gather necessary server state."""
        log.info('Initializing')
        self.ready = True
        log.info('Ready!')

    async def request_file(request):
        """This is really insecure, you can
        request other stuff from the server
        because I do not fucking check the data
        given in it aAAA.

        """
        imagepath = request.match_info['image']

        try:
            return web.FileResponse(f'./filething-images/{imagepath}')
        except FileNotFoundError:
            return web.Response(status=404, text='Not Found')

    async def generate_fileid(self):
        return ''.join((f'{random.choice(string.ascii_letters + string.digits)}' for i in range(6)))

    async def upload(request):
        reader = await request.multipart()

        sentfile = await reader.next()

        extension = sentfile.filename.split('.')[-1]
        filename = f'{self.generate_fileid()}.{extension}'

        size = 0
        with open(f'./filething-images/{filename}', 'wb') as f:
            while True:
                chunk = await sentfile.read_chunk()
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)

        return web.json_response({
            'bytes': size,
            'id': filename,
            'url': f'{self.config["url"]}/i/{filename}',
        })

    def run(self):
        """Start the HTTP server.

        Raises
        ------
        RuntimeError
            If the server is not ready for startup.
        """
        r = self.app.router

        r.add_get('/i/{image}', self.request_file)
        r.add_post('/upload', self.upload)

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

