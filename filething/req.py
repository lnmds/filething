
def auth(func):
    async def new_handler(request):
        user = await parse_request(request)
        if not user:
            return web.Response(status=401, text='Unauthorized')

        return await func(request, user)

    return new_handler

