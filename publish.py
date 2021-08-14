# #!/usr/bin/env python3
import json
import os
import functools
import concurrent.futures
from datetime import datetime
import re
from pathlib import Path
import time
import yaml
import asyncio
import logging
import aiohttp
import aiofiles
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TEMPLATE = """\
---
{front_matter}
---

{content}
"""


def timing(f):
    """
    decorator to time a function and print it
    :param f: function to wrap
    :return: wrapped function
    """
    def wrap():
        start = time.time()
        f()
        end = time.time()
        logger.info(f"{f.__name__} took {end - start!r}")
    return wrap


def slugify(name):
    """
    Takes a article name and returns a slug appropriate version using hyphens
    :param name: string to be converted
    :return: converted string
    """
    out = re.sub(r'[^\w\d\s]', '', name)
    return re.sub(r'\s', '-', out)


async def write_file(data):
    if data:
        file_name, data_out = '', ''
        data_id = data.get('id')
        data_type = data.get('type')
        if data_type in ('story', 'job'):
            slug = slugify(data.get('title'))
            data['date'] = datetime.fromtimestamp(data.get('time')).isoformat()
            data['linkurl'] = data.get('url')
            data['slug'] = slug
            data['tags'] = []
            data['categories'] = []
            if data.get('time', None):
                del data['time']
            if data.get('url', None):
                del data['url']
            if data.get('type', None):
                data['categories'] = ["{}".format(data.get('type'))]
                del data['type']
            file_name = Path(f'./content/en/post/{slug}.md')
            data_out = TEMPLATE.format(front_matter=yaml.dump(data).strip(), content="")
        elif data_type == 'comment':
            file_name = Path(f'./data/post/{data_id}.yaml')
            data_out = yaml.dump(data)

        # lets write the file if it doesn't exist
        if file_name and not file_name.exists():
            async with aiofiles.open(file_name, 'w') as f:
                await f.write(data_out)


async def fetch(url, session, sem):
    async with sem:
        async with session.get(url, ssl=False) as response:
            return await response.json()


async def worker(queue, session, sem):
    while True:
        json_data = None

        # Get a "work item" out of the queue.
        url = await queue.get()

        # download the json, wait for at most 5 seconds
        try:
            json_data = await asyncio.wait_for(fetch(url, session, sem), timeout=5)
        except asyncio.TimeoutError:
            logger.info(f"Timeout for {url}")
            # add back to queue for retry?
            # await queue.put(queue_item)

        # This data may add more to the queue lets check
        if type(json_data) is list:
            # list of ids e.g [123, 456]
            for article_id in json_data:
                queue.put_nowait(f'https://hacker-news.firebaseio.com/v0/item/{article_id}.json')
        elif type(json_data) is dict:
            # an individiual record lets add child records to the queue
            for comment_id in json_data.get('kids', []):
                queue.put_nowait(f'https://hacker-news.firebaseio.com/v0/item/{comment_id}.json')

            # lets write this record out as a file
            await write_file(json_data)

        # Notify the queue that the "work item" has been processed.
        queue.task_done()


async def start(num_workers):
    # Create a queue that we will use to store our "workload".
    queue = asyncio.Queue()

    # build initial urls
    urls = [f'https://hacker-news.firebaseio.com/v0/{name}.json' for name in
            ('topstories', 'askstories', 'showstories', 'jobstories')]

    # add initial urls to queue
    for url in urls:
        queue.put_nowait(url)

    tasks = []
    conn = aiohttp.TCPConnector(ttl_dns_cache=300, limit=0)
    sem = asyncio.Semaphore(100)
    async with aiohttp.ClientSession(connector=conn) as session:
        # Create worker tasks to process the queue concurrently.
        for i in range(num_workers):
            task = asyncio.create_task(worker(queue, session, sem))
            tasks.append(task)

        # Wait until the queue is fully processed.
        await queue.join()

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()


@timing
def main():
    logger.info("Starting publish...")

    num_workers = int(os.environ.get('num_workers', 100))

    # create dirs
    Path('./content/en/post/').mkdir(exist_ok=True)
    Path('./data/post/').mkdir(exist_ok=True)

    # Download all json and create files
    asyncio.run(start(num_workers))
    # asyncio.get_event_loop().run_until_complete(start(num_workers))

    logger.info("Building site...")
    subprocess.run(["hugo", "--verbose"])


if __name__ == '__main__':
    main()
