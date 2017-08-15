# -*- coding: utf-8 -*-

import requests, codecs

# cell_lac_file = 'cell-lac.txt.backup'
cell_lac_file = 'cell-lac.txt'
address_file = 'address.md'
appcode = '1e121b538b914e6387966b17537c8b28'

def read_file_to_list(filename):
    """ Read cell/lac info from file.

    return: [[cell, lac], ...]
    [
        ['42248', '04311'],
        ['24662', '04309'],
        ['60736', '04309'],
        ['60736', '04309'],
        ...
    ]
    """
    cell_lac_list = []
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            data = line.strip('\n').split(', ')
            cell_lac_list.append(data)

    return cell_lac_list

def generate_cell_lac_key(cell, lac):
    return cell + ',' + lac

def sort_cell_lac(cell_lac_list):
    """ Count and sorf cell/lac info.

    return: [('cell,lac', times), ...]
    [
        ('42248,04311', 60),
        ('60286,04311', 14),
        ('60736,04309', 13),
        ('11528,04309', 11),
        ...
    ]
    """
    statistics = {}
    for data in cell_lac_list:
        cell, lac = data[0], data[1]
        key = generate_cell_lac_key(cell, lac)
        if statistics.has_key(key):
            statistics[key] += 1
        else:
            statistics[key] = 1

    items = [(v, k) for k, v in statistics.items()]
    items.sort()
    items.reverse()             # so largest is first
    items = [(k, v) for v, k in items]

    return items

def request_address(cell, lac):
    url = 'http://basecell-ali.juheapi.com/cell/get?dtype=json&cell=%s&lac=%s&mnc=1' % (cell, lac)
    headers = {'Authorization': 'APPCODE ' + appcode}
    resp = requests.get(url, headers=headers)
    result = resp.json()['result']

    LNG = result['data'][0]['LNG']
    LAT = result['data'][0]['LAT']
    O_LNG = result['data'][0]['O_LNG']
    O_LAT = result['data'][0]['O_LAT']
    ADDRESS = result['data'][0]['ADDRESS']

    return [cell, lac, LNG, LAT, O_LNG, O_LAT, ADDRESS]

def main():

    # get cell/lac info list
    cell_lac_list = read_file_to_list(cell_lac_file)
    sorted_cell_lac = sort_cell_lac(cell_lac_list)

    # prepare table header for markdown
    table_head = ['times', 'cell', 'lac', 'LNG', 'LAT', 'O_LNG', 'O_LAT', 'ADDRESS']
    table_head_str = "|".join(table_head)
    table_head_extra_str = "|".join(['-' for item in table_head])

    with codecs.open(address_file, 'a', "utf-8") as f:

        f.write("|" + table_head_str + "|\n")
        f.write("|" + table_head_extra_str + "|\n")

        done = []
        for data in sorted_cell_lac:
            if data in done:
                continue

            cell_lac_str, times = data[0], data[1]
            single_cell_lac_list = cell_lac_str.split(',')
            cell, lac = single_cell_lac_list[0], single_cell_lac_list[1]

            address_info = request_address(cell, lac)
            address_info_str = "|".join(address_info)

            table_data_str = "|".join((str(times), address_info_str))
            f.write("|" + table_data_str + "|\n")

            done.append(data)

if __name__ == '__main__':
    main()
