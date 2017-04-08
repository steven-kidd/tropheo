from random import choice
from time import sleep
from dateutil.parser import parse as parse_date
from lxml import html

import requests

import os.path
import json
import string
import logging

from tropheo.settings import BASE_DIR


logger = logging.getLogger('django.server')
DATA_DIR = os.path.join(BASE_DIR, 'data')


class GenreBucket(object):

    def __init__(self):
        self._useless_genres = ['3d', 'roguelike', 'sim', 'career', 'team',
                                'individual', 'rail', 'other', 'space',
                                'nature', 'civilian', 'application',
                                'mission-based', 'static', 'exercise / fitness',
                                'top-down']
        self._bucket = {
            'adventure games': 'action adventure',
            'linear': 'adventure',
            'historic': 'action adventure',
            'console-style rpg': 'japanese-style',
            'point-and-click': 'role-playing',
            'visual novel': 'role-playing',
            'western-style': 'action rpg',
            'alternative': 'sports',
            'puzzle games': 'puzzle',
            'stacking': 'puzzle',
            'logic': 'puzzle',
            'matching': 'puzzle',
            'pc-style rpg': 'role-playing',
            'survival': 'horror',
            'sandbox': 'open-world',
            'parlor': 'arcade',
            'gambling': 'arcade',
            'pinball': 'arcade',
            'card battle games': 'arcade',
            'card battle': 'arcade',
            'board game': 'arcade',
            'trivia / game show': 'arcade',
            'board games': 'arcade',
            'board / card game': 'arcade',
            'futuristic': 'sci-fi',
            'military': 'shooter',
            'wwii': 'shooter',
            'light gun': 'shooter',
            'rhythm': 'music',
            'dancing': 'music',
            'music maker': 'music',
            'horizontal': 'scrolling',
            'vertical': 'scrolling',
            'tennis': 'sports',
            'football': 'sports',
            'soccer': 'sports',
            'basketball': 'sports',
            'baseball': 'sports',
            'wrestling': 'sports',
            'surfing': 'sports',
            'skateboarding': 'sports',
            'skate / skateboard': 'sports',
            'rugby': 'sports',
            'bowling': 'sports',
            'fishing': 'sports',
            'surf / wakeboard': 'sports',
            'wakeboarding': 'sports',
            'snowboarding': 'sports',
            'ski / snowboard': 'sports',
            'olympic sports': 'sports',
            'athletics': 'sports',
            'billiards': 'sports',
            'ice hockey': 'sports',
            'golf': 'sports',
            'boxing': 'sports',
            'boxing / martial arts': 'sports',
            'other sports games': 'sports',
            'formula one': 'driving',
            'demolition derby': 'driving',
            'motocross': 'driving',
            'racing': 'driving',
            'autombile': 'driving',
            'kart': 'driving',
            'motorcycle': 'driving',
            'stock car': 'driving',
            'car combat': 'driving',
            'vehicle': 'driving',
            'rally / offroad': 'driving',
            'gt / street': 'driving',
            'street': 'driving',
            'combat': 'fighting',
            'modern jet': 'flight',
            'helicopter': 'flight',
            'party / minigame': 'party',
            'other strategy games': 'strategy',
            'artillery': 'strategy',
            'wargame': 'strategy',
            'tactics': 'strategy',
            'tactical': 'strategy',
            'turn-based': 'strategy',
            'defense': 'strategy',
            'real-time': 'strategy',
            'business / tycoon': 'simulation',
            'virtual': 'simulation',
            'virtual life': 'simulation',
            'management': 'simulation',
            'tycoon': 'simulation',
            'mech': 'simulation',
            'compilations': 'compilation',
            'massively multiplayer online': 'massively multiplayer',
            'moba': 'massively multiplayer',
        }


    def bucket(self, genre):
        if genre in self._useless_genres:
            return ''
        elif genre in self._bucket:
            return self._bucket[genre]
        else:
            return genre

    def bucket_list(self, genre_list):
        unique_genres = set()
        for genre in genre_list:
            unique_genres.add(self.bucket(genre))
        return list(unique_genres)


class Scraper(object):

    def __init__(self, user_agent_list):
        self._user_agents = user_agent_list

    @property
    def headers(self):
        return {
            'User-Agent': choice(self._user_agents),
            'Connection': 'Close'
        }

    def _parse_value(self, tree, xpath, default, name, strip=False):
        try:
            val = tree.xpath(xpath)[0].strip()
            if type(default) is int:
                val = int(val)
            elif type(default) is float:
                val = float(val)
            elif type(default) is list:
                if strip:
                    val = [v.strip().lower() for v in val.split(', ')]
                else:
                    val = [v.lower() for v in val.split(', ')]

        except IndexError:
            logger.debug('Could not get %s xpath "%s", using value: %s', name, xpath, default)
            val = default
        except ValueError:
            logger.debug('%s element found is not of the type %s', name, type(default))
            val = default
        return val


class TrophyScraper(Scraper):

    def __init__(self, user_agent_list):
        self._user_agents = user_agent_list
        self.url = 'http://ps3trophies.com/games/all/'
        self._default_platform = 'ps3'
        self.trophy_points = {
            'bronze': 15,
            'silver': 30,
            'gold': 90,
            'platinum': 180
        }

    def _calc_trophy_points(self, game):
        points = 0
        for trophy_type, trophy_points in self.trophy_points.iteritems():
            points += (game[trophy_type] * trophy_points)
        return points

    def _parse_game(self, game_div):
        game = {}
        game['title'] = self._parse_value(game_div, './/div/b/a/text()', 'N/A', 'Title')
        game['bronze'] = self._parse_value(game_div, './/div[@class="bronze"]/text()', 0, 'Bronze Trophies')
        game['silver'] = self._parse_value(game_div, './/div[@class="silver"]/text()', 0, 'Silver Trophies')
        game['gold'] = self._parse_value(game_div, './/div[@class="gold"]/text()', 0, 'Gold Trophies')
        game['platinum'] = len(game_div.xpath('.//img[@title="This game has a platinum trophy"]'))
        game['points'] = self._calc_trophy_points(game)

        try:
            raw_platform = game_div.xpath('.//div/b/text()')
            game['platform'] = [p.strip().lower().replace('(','').replace(')', '') for p in raw_platform if len(p.strip()) > 0][0]
        except IndexError:
            game['platform'] = self._default_platform

        game['simple_id'] = ''.join(e for e in game['title'] if e.isalnum()).lower()
        game['id'] = game['simple_id'] + game['platform'].lower()
        return game


    def scrape(self):
        suffixes = ['number'] + list(string.lowercase)
        valid_games = []
        logger.info('Scraping all game trophy data from %s', self.url)
        for suffix in suffixes:
            response = requests.get(self.url + suffix, headers=self.headers)
            tree = html.fromstring(response.text)
            try:
                raw_games = tree.xpath('//div[@class="content"]//div[@class="holder"]')[1:]
            except IndexError:
                logger.error('Could not get %s trophies.', suffix.upper())
            games = [self._parse_game(game) for game in raw_games]
            valid_games.extend([game for game in games if game['title'] != 'N/A'])

            logger.info('Scraped %s games that start with a "%s"', len(games), suffix.upper())

        trophy_file = os.path.join(DATA_DIR, 'trophies.json')
        with open(trophy_file, 'w') as outfile:
            json.dump(valid_games, outfile, indent=4, sort_keys=True)
        logger.info('Scraped trophy data for %s games into %s', len(valid_games), trophy_file)
        return


class MetaCriticScraper(Scraper):

    def __init__(self, user_agent_list):
        self._user_agents = user_agent_list
        self._bucket = GenreBucket()
        self.url = 'http://www.metacritic.com/browse/games/score/metascore/all/$PLATFORM/filtered?view=detailed&page=$PAGE_NUM'

    def _dig_for_genre(self, tree):
        genre = []
        try:
            url = self._parse_value(tree, './/h3[@class="product_title"]//@href', None, 'Game URL')
            if url:
                dig_response = requests.get('http://metacritic.com' + url, headers=self.headers)
                if dig_response.status_code == 429:
                    sleep_time = 5
                    logger.warn('Too many requests.  Sleeping for %s and re-trying.', sleep_time)
                    sleep(sleep_time)
                    dig_response = requests.get('http://metacritic.com' + url, headers=self.headers)
                dig_tree = html.fromstring(dig_response.text)
                genre = self._parse_value(dig_tree, '//span[@itemprop="genre"]/text()', [], 'Genre')
                logger.info('dug into %s for genre %s', dig_response.url, genre)
            if genre == []:
                logger.warn('dug for genre, but found nothing for %s', dig_response.url)
        except Exception as err:
            logger.error('%s %s', type(err), err)
        if type(genre) is not list:
            logger.error('why isnt this a list??')
        return genre

    def _get_game_data(self, tree, platform):
        stats_div = tree.xpath('.//div[@class="product_basics stats"]')[0]
        img_div = tree.xpath('.//div[@class="product_basics product_image small_image"]')[0]

        title  = self._parse_value(stats_div, './/div[@class="basic_stat product_title"]/h3/a/text()', 'N/A', 'Game Title')
        critic_score = self._parse_value(stats_div, './/a[@class="basic_stat product_score"]/span/text()', -1, 'Critic Score')
        user_score = self._parse_value(stats_div, './/li[@class="stat product_avguserscore"]/span[2]/text()', -0.1, 'User Score')
        release_date = self._parse_value(stats_div, './/li[@class="stat release_date"]/span[2]/text()', 'Jan 1, 1900', 'Release Date')
        publisher = self._parse_value(stats_div, './/li[@class="stat publisher"]/span[2]/text()', 'N/A', 'Publisher')
        genre = self._parse_value(stats_div, './/li[@class="stat genre"]/span[2]/text()', [], 'Genre', strip=True)
        genre = self._dig_for_genre(stats_div) if genre == [] else genre
        maturity_rating = self._parse_value(stats_div, './/li[@class="stat maturity_rating"]/span[2]/text()', 'N/A', 'Maturity Rating')
        image_url = self._parse_value(img_div, './/img[@class="product_image small_image"]/@src', 'N/A', 'Image Url')
        game = {
            'id': ''.join(e for e in title if e.isalnum()).lower() + platform,
            'simple_id': ''.join(e for e in title if e.isalnum()).lower(),
            'title': title,
            'critic_score': critic_score,
            'user_score': int(user_score * 10),
            'release_date': str(parse_date(release_date).date()),
            'publisher': publisher,
            'genre': ','.join(list(set(genre))),
            'top_genre': self._bucket.bucket_list(genre),
            'maturity_rating': maturity_rating,
            'image_url': image_url,
            'platform': platform
        }
        return game

    def get_games(self, tree, platform):
        try:
            main_list = tree.xpath('//div[@id="main"]')[0]
        except IndexError:
            logger.error('Could not find the main content (div id=main).  Retrying.')
            try:
                main_list = tree.xpath('//div[@id="main"]')[0]
            except IndexError:
                logger.error('Could not find the main content (div id=main).  Giving up.')
                return []
        raw_game_divs = main_list.xpath('.//li/div')
        return [self._get_game_data(raw_game_div, platform) for raw_game_div in raw_game_divs]

    def _metacritic_request(self, platform, page_num):
        url = self.url.replace('$PLATFORM', platform).replace('$PAGE_NUM', str(page_num))
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError('Bad Status Code %s for request to %s' % (response.status_code, response.url))
        return response


    def get_pagination_count(self, tree):
        return self._parse_value(tree, '//li[@class="page last_page"]/a/text()', 0, 'Total Pagination')

    def scrape(self, platform):
        if platform.lower() not in ['ps3', 'vita', 'ps4']:
            logger.error('Platform must be "PS3", "PS4", or "VITA"')
            return

        current_page = 0
        response = self._metacritic_request(platform, current_page)
        tree = html.fromstring(response.text)

        page_count = self.get_pagination_count(tree)
        logger.info('Scraping %s pages of %s games from %s', page_count, platform, response.url)

        games = self.get_games(tree, platform)

        for _ in range(1, page_count + 1):
            current_page += 1
            response = self._metacritic_request(platform, current_page)
            tree = html.fromstring(response.text)
            games.extend(self.get_games(tree, platform))
            logger.info('Scraped %s %s games from %s', len(games), platform, response.url)

        datafile = os.path.join(DATA_DIR, '%s.json' % platform)
        with open(datafile, 'w') as outfile:
            json.dump(games, outfile, indent=4, sort_keys=True)

        logger.info('Wrote %s %s games to %s', len(games), platform, datafile)
        return
