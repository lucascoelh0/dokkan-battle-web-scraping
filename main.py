import json

import requests
from bs4 import BeautifulSoup

from Rarity import Rarity


def get_card_title(full_name: str):
    name_list = full_name.split('] ')
    return name_list[0].replace('[', '')


def get_card_name(full_name: str):
    try:
        if 'The Ultimate Android Super #17' in full_name:
            return full_name.split('The Ultimate Android ')[1]
        elif '[Catastrophic Rage Frieza (Final Form)' in full_name:
            return full_name.split('[Catastrophic Rage ')[1]
        else:
            return full_name.split('] ')[1]
    except:
        print(full_name)


def rarity_to_enum(rarity_name: str):
    if ':N' in rarity_name:
        return Rarity.N.value
    elif ':R' in rarity_name:
        return Rarity.R.value
    elif ':SR' in rarity_name:
        return Rarity.SR.value
    elif ':SSR' in rarity_name:
        return Rarity.SSR.value
    elif ':UR' in rarity_name:
        return Rarity.UR.value
    else:
        return Rarity.LR.value


def get_character_page_soup(char_link):
    char_result = requests.get(f'{root}/{char_link}')
    char_content = char_result.text
    return BeautifulSoup(char_content, 'lxml')


def get_portrait_link(character_soup, is_lr: bool):
    character_container = character_soup.find('div', class_='mw-parser-output')
    character_portrait_table = character_container.table

    for char_index, character_row in enumerate(character_portrait_table.tbody.find_all('tr')):
        if char_index == 0:
            character_columns = character_row.find_all('td')
            try:
                if is_lr:
                    return character_columns[0].find('img')['src']
                else:
                    return character_columns[0].find('a', class_='image')['href']
            except:
                print(character_columns)


def get_art_link(character_soup, is_lr: bool):
    art_container = character_soup.find('div', class_='lefttablecard')
    try:
        art_table = art_container.table
        art_link_container = art_table.tbody.find('span', class_='advanced-tooltip')
        if is_lr:
            return art_link_container.find('img')['src']
        else:
            return art_link_container.find('a', class_='image')['href']
    except:
        print(character_soup)


def get_char_data(char_table):
    for index, row in enumerate(char_table.tbody.find_all('tr')):
        if index > 0:
            columns = row.find_all('td')

            if columns:
                card_server = columns[6].text.strip()
                if 'Unreleased' not in card_server and 'Inactive' not in card_server:
                    card_full_name = columns[3].text.strip()
                    card_id = columns[0].text.strip().replace('(', '').replace(')', '')
                    card_title = get_card_title(card_full_name)
                    card_name = get_card_name(card_full_name)
                    rarity_info = columns[4].find('a')['title']
                    rarity = rarity_to_enum(rarity_info)
                    character_link = columns[3].find('a')['href']

                    char_soup = get_character_page_soup(character_link)
                    portrait_link = get_portrait_link(char_soup, rarity == 5)
                    art_link = get_art_link(char_soup, rarity == 5)

                    data = {
                        'cardId': card_id,
                        'cardTitle': card_title,
                        'cardName': card_name,
                        'rarity': rarity,
                        'portraitLink': portrait_link,
                        'artLink': art_link
                    }
                    res.append(data)


root = 'https://dbz-dokkanbattle.fandom.com'
website = f'{root}/wiki/All_Cards:_(1)001_to_(1)100'
result = requests.get(website)
content = result.text
soup = BeautifulSoup(content, 'lxml')
res = []

table = soup.find('table')
ids_container = soup.find('div', class_='mw-parser-output').find('p')
ids_links = ids_container.find_all('a')
for ids_index, ids_row in enumerate(ids_links):
    if ids_index > 0 and ids_index != (len(ids_links) - 1):
        table_result = requests.get(f'{root}/{ids_row["href"]}')
        content = table_result.text
        soup = BeautifulSoup(content, 'lxml')
        get_char_data(soup.find('table'))
    else:
        get_char_data(table)

print(json.dumps(res, indent=2, ensure_ascii=False))
