from random import shuffle, choice
import sys
import requests, logging, pdb


logger = logging.getLogger('django.server')


class PlayStationProfile(object):

    def __init__(self, username, psn_user_data):
        self.username = psn_user_data.get('handle', username)
        self.avatar = psn_user_data.get('avatarUrl', '')
        self.is_plus = bool(psn_user_data.get('isPlusUser', 0))
        self.level = int(psn_user_data.get('curLevel', 0))
        self.level_progress = int(psn_user_data.get('overallProgress', 0))

        game_data = psn_user_data.get('list', [])
        self.games = self._parse_games(game_data)
        self.game_count = len(self.games)
        self.average_completion = round(sum([int(g['progress']) for g in self.games]) / float(len(self.games)), 2)

        trophies = self._parse_trophies(game_data) # self.games double counts games across platforms.
        self.trophies = trophies
        self.platinum = trophies['platinum']
        self.gold = trophies['gold']
        self.silver = trophies['silver']
        self.bronze = trophies['bronze']

    @property
    def is_empty(self):
        q = sum([len(self.avatar), self.level, self.level_progress, len(self.games),
                 self.platinum, self.gold, self.silver, self.bronze, self.is_plus])
        return q == 0

    @property
    def is_private(self):
        q = sum([self.level, self.level_progress, len(self.games),
                 self.platinum, self.gold, self.silver, self.bronze])
        return q == 0 and self.is_plus

    @property
    def played_simple_ids(self):
        return [g['simple_id'] for g in self.games]

    @property
    def played_ids(self):
        return [g['id'] for g in self.games]

    @property
    def played_platforms(self):
        platforms = {
            'ps3': False,
            'ps4': False,
            'vita': False
        }
        for game in self.games:
            if game['platform'] in platforms:
                platforms[game['platform']] = True
                if platforms['ps3'] and platforms['ps4'] and platforms['vita']:
                    return platforms.keys()
        return [platform for platform, played in platforms.iteritems() if played]

    @property
    def json(self):
        return {
            'username': self.username,
            'avatar': self.avatar,
            'is_plus': self.is_plus,
            'level': self.level,
            'level_progress': self.level_progress,
            'games': self.games,
            'platinum': self.platinum,
            'gold': self.gold,
            'silver': self.silver,
            'bronze': self.bronze,
            'played_ids': self.played_ids,
            'played_simple_ids': self.played_simple_ids,
            'is_private': self.is_private,
            'is_empty': self.is_empty,
            'game_count': self.game_count,
            'played_platforms': self.played_platforms,
            'trophies': self.trophies
        }

    def __str__(self):
        return '%s is %s%% into level %s and is %sa plus member with %s games.\n' \
               'Trophies: %s Platinums, %s Golds, %s Silvers, %s Bronzes' % \
               (self.username, self.level_progress, self.level, '' if self.is_plus else 'not ',
                len(self.games), self.platinum, self.gold, self.silver, self.bronze)

    # def _query_psn(self, username, request_headers):
    #     base_url = 'https://io.playstation.com/playstation/psn/public/trophies/'
    #     payload = {'onlineId': username}
        
    #     response = requests.get(base_url, params=payload, headers=request_headers)
    #     print('GET %s %s' % (response.status_code, response.url))
    #     return response.json()

    def _parse_games(self, game_list):
        parsed_games = []
        for g in game_list:
            for platform in g['platform'].lower().split(','):
                parsed_games.append({
                    'game_id': g['gameId'],
                    'title': g['title'],
                    'platform': platform,
                    'trophies': g['trophies'],
                    'progress': g['progress'],
                    'image_url': g['imgUrl'],
                    'progress': g['progress'],
                    'id': ''.join(e.lower() for e in g['title'] if e.isalnum()) + platform,
                    'simple_id': ''.join(e.lower() for e in g['title'] if e.isalnum())
                })
        return parsed_games

    def _parse_trophies(self, games):
        trophies = {
            'platinum': 0,
            'gold': 0,
            'silver': 0,
            'bronze': 0
        }
        for game in games:
            for trophy in trophies.iterkeys():
                trophies[trophy] += game['trophies'][trophy]
        return trophies


class PlayStationNetwork(object):

    @staticmethod
    def query(psn_id, headers=None):
        base_url = 'https://io.playstation.com/playstation/psn/public/trophies/'
        payload = {'onlineId': psn_id}
        request_headers = {
            'origin': 'https://www.playstation.com',
            'Connection': 'Close'
        }
        if headers:
            for k, v in headers.iteritems():
                request_headers[k] = v
        
        response = requests.get(base_url, params=payload, headers=request_headers)
        return PlayStationProfile(psn_id, response.json())

__all__ = ['PlayStationNetwork']