from os import makedirs
from datetime import datetime
import requests
import yaml
import re
import subprocess


TEMPLATE = """\
---
{front_matter}
---

{content}
"""


def slugify(name):
    out = re.sub(r'[^\w\d\s]', '', name)
    return re.sub(r'\s', '-', out)


def create_item(item):
    slug = slugify(item.get('title'))
    makedirs('./content/post/', exist_ok=True)
    file_name = './content/post/{}.md'.format(slug)
    with open(file=file_name, mode='w', encoding='utf-8') as f:
        print('{}...'.format(slug))
        item['date'] = datetime.fromtimestamp(item.get('time')).isoformat()
        item['linkurl'] = item.get('url')
        item['slug'] = slug
        item['tags'] = []
        item['categories'] = []
        if item.get('time', None):
            del item['time']
        if item.get('url', None):
            del item['url']
        if item.get('type', None):
            item['categories'] = [ item.get('type') ]
            del item['type']
        f.write(TEMPLATE.format(front_matter=yaml.dump(item).strip(), content=""))


def hugo_build():
    completed = subprocess.run(
        ['./bin/hugo-linux64', '--baseURL=https://davidejones.github.io/hugo-hn/'],
        stdout=subprocess.PIPE,
    )
    print('{}'.format(completed.stdout.decode('utf-8')))


def main():
    print("Generating hacker news content...")
    end_points = ['topstories', 'askstories', 'showstories', 'jobstories']
    for point in end_points:
        items_request = requests.get('https://hacker-news.firebaseio.com/v0/{}.json'.format(point))
        for id in items_request.json():
            item_request = requests.get('https://hacker-news.firebaseio.com/v0/item/{}.json'.format(id))
            item = item_request.json()
            create_item(item)
    hugo_build()

if __name__ == '__main__':
    main()
