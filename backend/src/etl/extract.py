import csv
import re

import requests
from bs4 import BeautifulSoup, Tag, ResultSet

BASE_URL = 'https://blueypedia.fandom.com'


def get_episodes_guide_tables() -> ResultSet:
    url = f'{BASE_URL}/wiki/Episode_Guide'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find_all('table')


def is_episodes_table(candidate_table: Tag) -> bool:
    first_tr = candidate_table.find_all('tr')[0]
    th_elements = first_tr.find_all('th')
    if not th_elements:
        return False

    first_header = th_elements[0].get_text(strip=True)
    return first_header == '#'


def get_transcript(relative_url: str) -> str:
    url = f'{BASE_URL}{relative_url}/Script'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    transcript_parent_tag = soup.find('div', class_='mw-parser-output')
    lines = [tag.get_text(strip=True) for tag in transcript_parent_tag.find_all(['p', 'dl'])]
    return '\n'.join(lines)


def get_episodes_from_tables(episode_tables) -> list[dict]:
    episodes = []

    for i, table in enumerate(episode_tables):
        episode_rows = table.find_all('tr')[3:]
        for row in episode_rows:
            cells = row.find_all('td')
            if len(cells) < 2:
                continue

            url = cells[1].find_all('a')[0]['href']
            _episode = {
                'id': f'Episode:{build_id_from_url(url)}',
                'season': i + 1,
                'episode': int(cells[0].get_text(strip=True)),
                'title': cells[1].get_text(strip=True),
                'wiki_url': url
            }
            episodes.append(_episode)

    return episodes


def get_episodes():
    episodes_guide_tables = get_episodes_guide_tables()
    episode_tables = [t for t in episodes_guide_tables if is_episodes_table(t)]
    return get_episodes_from_tables(episode_tables)


def get_recap(relative_episode_url: str) -> list[str]:
    url = f'{BASE_URL}{relative_episode_url}'

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        recap_parent_tag = soup.find('div', class_='mw-collapsible-content')
        return [
            tag.get_text()
            for tag in recap_parent_tag.find_all(['p'])
            if not tag.get_text().startswith('Recap Credits') and not tag.get_text().strip() == ''
        ]
    except Exception as e:
        print(f'Failed to get recap from {relative_episode_url} due to {e}')
        return []


def get_transcripts():
    transcripts = [
        {
            'season': e['season'],
            'episode': e['episode'],
            'transcript': get_transcript(e['wiki_url'])
        }
        for e in episodes
    ]


def get_recap_parts():
    recaps = [
        {
            'episode_id': e['id'],
            'recap': get_recap(e['wiki_url'])
        }
        for e in episodes
    ]

    parts = []
    for recap in recaps:
        parts.extend([
            {
                'id': f'Recap:{recap["episode_id"]}_{i}',
                'episode_id': recap['episode_id'],
                'index': i,
                'text': r.strip()
            }
            for i, r in enumerate(recap['recap'])
        ])

    return parts


def save_csv(filename: str, items: list[dict]):
    with open(f'data/{filename}.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=items[0].keys())
        writer.writeheader()
        for item in items:
            writer.writerow(item)


def remove_parentheses(text):
    return re.sub(r'\s*\([^)]*\)', '', text)


def get_appearances_from_wiki(relative_episode_url) -> list[str]:
    url = f'{BASE_URL}{relative_episode_url}'

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        header = soup.find('span', id='Appearances')
        ul = header.find_next('ul')

        return [
            build_id_from_url(li.find('a')['href'])
            for li in ul.find_all('li')
            if not li.find('ul')
        ]
    except Exception as e:
        print(f'Failed to get appearances from {relative_episode_url} due to {e}')
        return []


def get_appearances():
    apperances_in_episodes = [
        {
            'episode_id': e['id'],
            'appearances': get_appearances_from_wiki(e['wiki_url'])
        }
        for e in episodes
    ]

    appearances = []
    for appearances_in_episode in apperances_in_episodes:
        appearances.extend([
            {
                'source_id': f'Character:{character_id}',
                'label': 'APPEARS_IN',
                'target_id': appearances_in_episode['episode_id'],
            }
            for character_id in appearances_in_episode['appearances']
            if '#' not in character_id
        ])

    return appearances


def get_main_characters_biographies():
    # Only four, not worth scraping automatically
    return [
        {
            'character': 'Chilli Heeler',
            'biography': "Chilli Heeler (née Cattle) is a main character in Bluey. She is the wife of Bandit, mother of Bluey and Bingo, aunt of Socks and Muffin, the younger sister of Brandy and the daughter of Mort and Chilli's Mum."
        },
        {
            'character': 'Bandit Heeler',
            'biography': "Bandit Heeler is a main character of Bluey. He is the husband of Chilli, the younger brother of Rad and the older brother of Stripe, father of Bluey and Bingo, uncle of Muffin and Socks, son of Bob and Chris, brother-in-law of Trixie and Brandy, and the son-in-law of Mort and Chilli's Mum."
        },
        {
            'character': 'Bluey Heeler',
            'biography': "Bluey Christine Heeler is a main character of Bluey. As the titular protagonist, she is the older daughter of Bandit and Chilli, the older sister of Bingo, the older cousin of Muffin and Socks, and the older niece of Stripe, Trixie, Rad, Frisky, and Brandy."
        },
        {
            'character': 'Bingo Heeler',
            'biography': "Bingo Heeler is one of the main characters of Bluey. Serving the role as a deuteragonist, she is the younger daughter of Bandit and Chilli, the younger sister of Bluey, the older cousin of Muffin and Socks, and the younger niece of Stripe, Trixie, Rad, and Brandy."
        }
    ]


def get_secondary_characters_list() -> dict[str, str]:
    characters_list_url = 'https://blueypedia.fandom.com/wiki/Category:Secondary_Characters'
    response = requests.get(characters_list_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    characters = soup.find_all('li', class_='category-page__member')
    return {
        c.get_text(strip=True): c.find('a')['href']
        for c in characters
    }


def get_secondary_characters_biographies():
    characters = get_secondary_characters_list()
    bios = []
    for character, relative_url in characters.items():
        url = f'{BASE_URL}{relative_url}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        biography = soup.find('span', id='Biography').find_next('p').get_text()
        bios.append({
            'character': character,
            'biography': biography.strip()
        })
    return bios


def get_relations():
    relations = []
    for c in characters:
        relative_url = f'/wiki/{c["id"][len('Character:'):]}'
        url = f'{BASE_URL}{relative_url}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        relatives_tag, friends_tag = None, None
        for tag in soup.find_all('div', attrs={'data-source': True}):
            if tag['data-source'] == 'relative(s)':
                relatives_tag = tag
            if tag['data-source'] == 'friend(s)':
                friends_tag = tag

        character_id = build_id_from_url(relative_url)
        if relatives_tag:
            relations.extend(get_related_to(character_id, relatives_tag))

        if friends_tag:
            relations.extend(get_friends_of(character_id, friends_tag))

    return relations


def get_related_to(character_id, relatives_tag):
    relations = []

    for a in relatives_tag.find_all('a'):
        source_id = build_id_from_url(a['href'])
        if 'Background_characters' not in source_id and 'Mentioned' not in source_id:
            relation_type = get_relation_type(a)
            relations.append({
                'source_id': f'Character:{source_id}',
                'label': 'IS_RELATIVE_OF',
                'target_id': f'Character:{character_id}',
                'relation_type': relation_type
            })

    return relations


def get_friends_of(character_id, friends_tag):
    relations = []

    for a in friends_tag.find_all('a'):
        source_id = build_id_from_url(a['href'])
        if 'Background_characters' not in source_id and 'Mentioned' not in source_id:
            relation_type = get_relation_type(a)
            relations.append({
                'source_id': f'Character:{source_id}',
                'label': 'IS_FRIEND_OF',
                'target_id': f'Character:{character_id}',
                'relation_type': relation_type
            })

    return relations


def get_relation_type(a):
    next_sibling = a.next_sibling
    while next_sibling and next_sibling.name != 'a':
        t = next_sibling.get_text().strip()
        if t:
            if match := re.search(r'\((.*?)\)', t):
                return match.group(1)
            else:
                return None
        next_sibling = next_sibling.next_sibling

    return None


ids_cache = {}


def build_id_from_url(relative_url):
    if relative_url in ids_cache:
        return ids_cache[relative_url]

    url = requests.get(f'{BASE_URL}{relative_url}').url
    _id = url.split('/wiki/')[1]
    ids_cache[relative_url] = _id

    return _id


def get_characters():
    main = [
        {
            'name': 'Bluey Heeler',
            'id': 'Character:Bluey_Heeler'
        },
        {
            'name': 'Bandit Heeler',
            'id': 'Character:Bandit_Heeler'
        },
        {
            'name': 'Bingo Heeler',
            'id': 'Character:Bingo_Heeler'
        },
        {
            'name': 'Chilli Heeler',
            'id': 'Character:Chilli_Heeler'
        }
    ]
    secondary = [
        {
            'name': name,
            'id': f'Character:{build_id_from_url(relative_url)}'
        }
        for name, relative_url
        in get_secondary_characters_list().items()
    ]
    return [*main, *secondary]


if __name__ == '__main__':
    episodes = get_episodes()
    save_csv('episodes', episodes)

    recap_parts = get_recap_parts()
    save_csv('recap_parts', recap_parts)

    appearances = get_appearances()
    save_csv('appearances', appearances)

    characters = get_characters()
    save_csv('characters', characters)

    all_relations = get_relations()
    save_csv('relations', all_relations)
