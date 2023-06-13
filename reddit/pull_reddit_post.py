import requests
from os import path
import configparser


def request_reddit_json(url):
    json_url = url + '.json'

    headers = {"User-Agent": "User agent for pulling posts and wiki pages locally."}
    resp = requests.get(json_url, headers=headers)

    if not resp:
        raise RuntimeError(f'An error has occured in the request of {url}')

    return resp.json()


def get_reddit_post_body(url, outpath='./reddit_pages/', title=None, overwrite=True):
    assert('comment/' not in url), 'Provided url appears to be for a comment rather than a post or wiki page.'
    is_wiki = '/wiki/' in url

    if is_wiki:
        if title is None:
            title = url.replace('https://www.reddit.com/r/', '').replace('/', ' ').strip()
    else:
        if title is None:
            if url[-1] == '/':
                title = url.split('/')[-2].replace('_', ' ')
            else:
                raise RuntimeError('The url should end in a \'/\'')

    file_title = ''
    for char in title.replace(' ', '_'):
        if char.isalnum() or char == '_':
            file_title += char

    dest_path = f'{outpath}/{file_title}.md'

    if path.isfile(dest_path) and overwrite is False:
        print(f'A file with title matching below url already exists, skipping.\n{url}\n')

        return None

    data = request_reddit_json(url)
    if is_wiki:
        body = data['data']['content_md']
    else:
        body = data[0]['data']['children'][0]['data']['selftext']

    if body.isspace() or body == '':
        print(f'Body is nothing but whitespace, skipping below url.\n{url}\n')

        return None

    with open(dest_path, 'w') as filer:
        filer.write(f'# {title}\n\n')
        filer.write(body)

    return dest_path


def loop_over_ini(ini_path):
    config = configparser.ConfigParser()
    config.read(ini_path)

    default_section = config['DEFAULT']
    overwrite = default_section.getboolean('overwrite', True)
    outpath = default_section.get('outpath', './reddit_pages/')

    for url in config.sections():
        print(url)
        title = config[url].get('title', None)
        get_reddit_post_body(url, outpath=outpath, title=title, overwrite=overwrite)


def print_pretty_json(json_url):
    with request_reddit_json(json_url) as json_handle:
        data = json.load(json_handle)

    pretty = json.dumps(data, indent=2)

    with open('./pretty.json', 'w') as filer:
        filer.write(pretty)


if __name__ == '__main__':
    loop_over_ini('./reddit_post.ini')
