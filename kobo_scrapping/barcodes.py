import barcode
import requests
import os
import tqdm
from glob import glob
from natsort import natsorted


# These are the non-light-novel books in my kobo, which I may want to filter out or specifically take these.
_not_light_novel_books = [
        'At The Existentialist Café',
        'Buddha\'s Little Finger',
        'I Am Dynamite!',
        'One Hundred Years of Solitude',
        'Red Sister (Book of the Ancestor, Book 1)',
        'The Brothers Karamazov',
        ]


def get_webpage_list_from_overview_html(html_path):
    assert (os.path.isfile(html_path)), 'html_path must be a path on the local computer. A url does not work as the kobo webpage needs authentication and I cba with that.'

    url_list = []
    title_list = []
    with open(html_path, 'r') as filer:
        desired_url_next_line = False
        for line_num, line in enumerate(filer):
            if '\"title product-field' in line:
                desired_url_next_line = True
                continue

            if desired_url_next_line is True:
                desired_url_next_line = False
                url = line.split('href=\"')[-1].split('\">')[0]
                title = line.split('\">')[-1].split('</a>')[0]
                if title in _not_light_novel_books:
                    continue
                url_list.append(url)
                title_list.append(title)

    return url_list, title_list


def get_isbn_list_from_kobo_list(webpage_list):
    isbn_list = []
    for url in tqdm.tqdm(webpage_list):
        headers = {"User-Agent": "User agent for pulling isbn numbers."}
        resp = requests.get(url, headers=headers)

        if not resp:
            raise RuntimeError(f'An error has occured in the request of {url}')

        valid_lines = []
        for line in resp.text.split('\n'):
            if 'ISBN:' in line:
                valid_lines.append(line)

        assert (len(valid_lines) == 1), f'More than one line containing \'ISBN:\' found for {url}.'

        isbn_try1 = int(valid_lines[0].split('<span translate="no">')[-1].split('</span>')[0])
        isbn_try2 = int(''.join(digit for digit in valid_lines[0] if digit.isdigit()))

        assert (isbn_try1 == isbn_try2), f'Somehow got 2 different isbns from 2 different string manipulation: {isbn_try1} vs {isbn_try2}'

        isbn_list.append(isbn_try1)

    return isbn_list


def make_isbn_barcode(number):
    barcode_maker = barcode.get_barcode_class('isbn')
    this_barcode = barcode_maker(number)
    this_barcode.save(f'./barcodes/{number}_barcode')


if __name__ == '__main__':
    html_list = natsorted(glob('./kobo_overview_htmls/*'))
    url_list = []
    title_list = []
    for html in html_list:
        html_read_res = get_webpage_list_from_overview_html(html)
        url_list += html_read_res[0]
        title_list += html_read_res[1]

    # start = 45
    # end = 48
    # url_list = url_list[start:end]
    # title_list = title_list[start:end]

    isbn_list = get_isbn_list_from_kobo_list(url_list)

    for isbn, title in zip(isbn_list, title_list):
        print(f'{isbn}::{title}')

    print()

    # assert (len(isbn_list) == len(title_list)), f'Somehow the lengths of isbn_list ({len(isbn_list)}) and title_list ({len(title_list)}) are not the same'
    for isbn, title in zip(isbn_list, title_list):
        print(f'{isbn}::{title}')
        make_isbn_barcode(str(isbn))
