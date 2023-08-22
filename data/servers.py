import json
import os

import aiofiles


async def get_server_list():
    file_path = os.path.join(os.getcwd(), 'servers.json')

    async with aiofiles.open(file_path, mode='r') as f:
        content = await f.read()

    servers = json.loads(content)
    return servers
