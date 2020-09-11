import os
from typing import List

import requests

import bs4


DOMAIN = "https://frontend-ifmo-2019.now.sh"


def get_file_links(dir_path: str) -> List[str]:
    r = requests.get(f"{DOMAIN}{dir_path}")
    soup = bs4.BeautifulSoup(r.text, features='lxml')

    links = []

    for a in soup.find_all('a'):
        if a.parent.name == 'li':
            link: str = a.get('href')
            if '.' in link.split('/')[-1]:
                links.append(a.get('href'))
            else:  # consider it's a dir
                links.extend(get_file_links(link))

    return links


def download_file(path: str) -> None:
    r = requests.get(f"{DOMAIN}{path}")

    path = f'files/{path.lstrip("/")}'

    folder = "/".join(path.split('/')[:-1])
    os.makedirs(folder, exist_ok=True)

    with open(path, 'w') as file:
        file.write(r.text)


if __name__ == '__main__':
    root_url = "/js/01-intro/assets/"
    file_links = get_file_links(root_url)

    for file_link in file_links:
        download_file(file_link)
