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


def create_story(item):
    slug = slugify(item.get('title'))
    makedirs('./content/posts/', exist_ok=True)
    file_name = './content/posts/{}.md'.format(slug)
    with open(file=file_name, mode='w', encoding='utf-8') as f:
        print('{}...'.format(slug))
        item['date'] = datetime.fromtimestamp(item.get('time')).isoformat()
        item['linkurl'] = item.get('url')
        item['slug'] = slug
        item['tags'] = []
        if item.get('time', None):
            del item['time']
        if item.get('url', None):
            del item['url']
        f.write(TEMPLATE.format(front_matter=yaml.dump(item).strip(), content=""))


def hugo_build():
    completed = subprocess.run(
        ['./bin/hugo-linux64'],
        stdout=subprocess.PIPE,
    )
    print('{}'.format(completed.stdout.decode('utf-8')))


def main():
    print("Generating latest 30 hacker news posts...")
    stories_request = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json')
    for id in stories_request.json()[:30]:
        item_request = requests.get('https://hacker-news.firebaseio.com/v0/item/{}.json'.format(id))
        item = item_request.json()
        create_story(item)
    hugo_build()

if __name__ == '__main__':
    main()
