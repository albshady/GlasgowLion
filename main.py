import asyncio
import os
from typing import List

from aiohttp import ClientSession, TCPConnector

import bs4


DOMAIN = "https://frontend-ifmo-2019.now.sh"
ROOT_URL = "/js/01-intro/assets/"


async def get_file_links(session: ClientSession, dir_path: str) -> List[str]:
    async with session.get(f"{DOMAIN}{dir_path}") as resp:
        soup = bs4.BeautifulSoup(await resp.text(), features='lxml')

    links = []
    tasks = []

    for a in soup.find_all('a'):
        if a.parent.name == 'li':
            link: str = a.get('href')
            if '.' in link.split('/')[-1]:
                links.append(a.get('href'))
            else:  # consider it's a dir
                tasks.append(get_file_links(session, link))

    flat_list = [item for sublist in await asyncio.gather(*tasks) for item in sublist]
    links.extend(flat_list)
    return links


async def download_file(session: ClientSession, path: str) -> None:
    async with session.get(f"{DOMAIN}{path}") as resp:
        content = await resp.read()

    os.makedirs(f"files/{'/'.join(path.split('/')[:-1])}", exist_ok=True)

    with open(f"files{path}", 'wb') as file:
        file.write(content)


async def main():
    connector = TCPConnector(ssl=False)
    async with ClientSession(connector=connector) as session:
        file_links = await get_file_links(session, ROOT_URL)

        tasks = [download_file(session, file_link) for file_link in file_links]
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
