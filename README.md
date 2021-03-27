# hugo-hn

[![Build Status Badge](https://api.travis-ci.org/davidejones/hugo-hn.svg?branch=master)](https://travis-ci.org/davidejones/hugo-hn)

Hacker News site built with Hugo http://davidejones.github.io/hugo-hn

[![screenshot](https://raw.githubusercontent.com/davidejones/hugo-hn/master/screen.png)](http://davidejones.github.io/hugo-hn)

## Running the site locally

### Running

Download the hugo extended binary at version 0.82 or higher. You can get it from the releases page on this repo https://github.com/gohugoio/hugo
Once you have it follow these steps to run the site locally

```
git clone https://github.com/davidejones/hugo-hn.git
cd hugo-hn
hugo server
```

Then visit http://localhost:1313 to see the site. See posts section below for lack of content

### Posts

You may notice there are no posts while running this locally. This is because they are scraped from the hacker news api during the travis build using a python script called `publish.py`.
If you want some posts to play with locally, you can install python 3 (i'm using python 3.7) and then do something like this

For mac and linux
```
# cd into this project/repo
python -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
python publish.py
```

For windows
```
# cd into this project/repo
python -m venv venv
venv\bin\activate.bat
pip install -r requirements.txt
python publish.py
```

