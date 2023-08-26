
import json

import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent

ua = UserAgent()


def get_data(fight):
    try:
        headers = {'user-agent': ua.random}
        event_link = fight.find('span', class_="name").find('a').get("href")
        r = requests.get("https://www.tapology.com" + event_link, headers = headers)
        soup = bs(r.text, 'lxml')
        fight_cards = soup.find('ul', class_='fightCard').find_all(class_='fightCardFighterBout')
        for fight_card in fight_cards:
            try:
                headers = {'user-agent': ua.random}
                fighter_link = "https://www.tapology.com" + fight_card.find(class_='fightCardFighterName').find('a').get('href')
                with open('existing_fighters.txt', encoding='utf-8') as file:
                    existing_fighters = file.read().split('\n')
                if fighter_link not in existing_fighters:
                    with open('existing_fighters.txt', 'a', encoding='utf-8') as file:
                        file.write(fighter_link + '\n')
                else:
                    continue
                r = requests.get(fighter_link, headers=headers)
                soup = bs(r.text, 'lxml')
                fighter_img = soup.find(class_ = 'fighterImg').find('img').get('src')
                details = soup.find(class_='details').find('ul').find_all('li')
                all_details = []
                for detail in details:
                    detail_detail = detail.text.replace('\n', '')
                    all_details.append(detail_detail)
                print(all_details)
                opponents_details = {}
                all_details.append(f'fighter_link: {fighter_link}')
                for opponent in soup.find_all('div', {'class': 'result'}):
                    opponent_name = opponent.find(class_='name').text
                    status = opponent.parent.get('status')
                    opponent_details = opponent.find(class_ = 'summary').find(class_ = 'lead').text
                    event_name = opponent.find(class_ = 'notes').text
                    date = opponent.find(class_ = 'date').text
                    opponents_details[opponent_name.replace('\n', '')] = f'{event_name}|{status}|{opponent_details}|{date}'.replace('\n', '').replace('\u00b7', '')
                all_details.append(opponents_details)
                all_details.append(f'profile image: {fighter_img}')
                social_media_links = "social_media_links: " + ''.join(i.get('href') + "|" for i in soup.find(class_ = 'externalIconsHolder').find_all('a'))
                all_details.append(social_media_links)
                with open('data.json', encoding='utf-8') as file:
                    content = json.load(file)
                with open('data.json', 'w', encoding='utf-8') as file:
                    content[len(content.keys())] = all_details
                    json.dump(content, file, indent=4)
            except Exception as ex:
                continue
    except Exception as ex:
        print(ex)
        return 1


def main():
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump({}, file, indent=4)
    page = 1
    while True:
        r = requests.get(f'https://www.tapology.com/fightcenter_events?page={page}')
        with open('index.html', 'w', encoding='utf-8') as file:
            file.write(r.text[r.text.find('html') + 5:r.text.find('");')])
        with open('index.html', encoding='utf-8') as file:
            content = file.read()
        soup = bs(content, 'lxml')
        for event in soup.find_all('section', class_="fcListing"):
            get_data(event)

        page += 1


if __name__ == '__main__':
    main()
