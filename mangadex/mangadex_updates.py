import requests
import argparse
import datetime

_base_url = "https://api.mangadex.org"


def read_ini(ini_path):
    """
    Read in desired language and manga list.
    """
    with open(ini_path, 'r') as ini:
        ini_contents = ini.readlines()

    language = ini_contents[0].replace('\n', '')

    manga_ids = []
    for line in ini_contents[1:]:
        if line.startswith('#') or line.startswith(';'):
            continue
        manga_ids.append(line.split(' '))
        manga_ids[-1][1] = manga_ids[-1][1].replace('\n', '')

    return language, manga_ids


def get_json(language, timestamp, manga_ids):
    """
    Pull json data from mangadex API.
    """
    request_params = {"createdAtSince": timestamp}

    requested_jsons = []
    for manga_id, manga_title in manga_ids:
        url = f"{_base_url}/manga/{manga_id}/feed"
        request_result = requests.get(url, params=request_params).json()
        assert(request_result['result'] == 'ok'), f'Failed to retrieve json for {manga_id} {manga_title}.'

        reduced_data = []
        for datum in request_result['data']:
            # print(datum['attributes']['translatedLanguage'] == language)
            if datum['attributes']['translatedLanguage'] == language:
                reduced_data.append(datum)

        requested_jsons.append(reduced_data)

    return requested_jsons


def sort_data_list(data_list, attribute_field):
    values_to_sort_on = []
    for datum in data_list:
        values_to_sort_on.append(datum['attributes'][attribute_field])

    sorted_indices = sorted(range(len(values_to_sort_on)), key=lambda k: values_to_sort_on[k])

    sorted_list = []
    for index in sorted_indices:
        sorted_list.append(data_list[index])

    return sorted_list


def get_updates(ini_path, number_of_days):
    language, manga_ids = read_ini(ini_path)

    timestamp = str(datetime.date.today() - datetime.timedelta(days=number_of_days)) + 'T00:00:00'

    requested_jsons = get_json(language, timestamp, manga_ids)

    for jj, json_data in enumerate(requested_jsons):
        manga_id = manga_ids[jj][0]
        title = manga_ids[jj][1].replace('-', ' ')

        sorted_data = sort_data_list(json_data, 'publishAt')

        print(f'{title}: {manga_id}')
        for datum in sorted_data:
            chapter_id = str(datum['id'])
            attr = datum['attributes']
            info_string = attr['publishAt'].split('T')[0] + ' ' + str(attr['volume']) + ' ' +  str(attr['chapter']) + ' ' + str(attr['title'])
            if attr['title'] is None:
                info_string += ' ' + chapter_id
            print(info_string)
        print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('number_of_days', type=int, default=7, help = 'Number of days in the past to search for new releases.')
    args = parser.parse_args()

    get_updates('./mangadex_list.ini', args.number_of_days)
