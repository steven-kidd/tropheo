from django.core.management.base import BaseCommand, CommandError
from django.db.utils import OperationalError
from trohpeo.models import UserAgent, Game

from tropheo.settings import BASE_DIR
from trohpeo.scrapers import MetaCriticScraper, TrophyScraper

import os.path
import json
import logging


logger = logging.getLogger(__name__)
DATA_DIR = os.path.join(BASE_DIR, 'data')


class Command(BaseCommand):

    help = '''
    Scrapes metacritic.com ps3trophies.com for new games, and can join the results together.
    Usage:  python manage.py [ps3, ps4, vita] [-t / --trophies] [-j / --join]
    [ps3, ps4, vita] == Any/All platforms to scrape from metacritic.  Writes 3 separate JSON files.
    [-t / --trophies] == Scrape ps3trophes.com for all trophy data.  Writes 1 JSON file.
    [-j / --join] == Joins the current JSON data together to create a full list of complete games.

    Ex.
    python manage.py scrape ps4 --trophies --join # scrapes ps4 ratings, trophies, writes new data file.
    '''

    def add_arguments(self, parser):
        parser.add_argument('platforms', nargs='+', type=str)

        # Named (optional) arguments
        parser.add_argument(
            '--join',
            action='store_true',
            dest='join',
            default=False,
            help='Join json data from scraped sites.',
        )
        parser.add_argument(
            '-j',
            action='store_true',
            dest='join',
            default=False,
            help='Join json data from scraped sites.',
        )
        parser.add_argument(
            '--trophies',
            action='store_true',
            dest='trophy_scrape',
            default=False,
            help='Scrape ps3trophies.com',
        )
        parser.add_argument(
            '-t',
            action='store_true',
            dest='join',
            default=False,
            help='Scrape ps3trophies.com',
        )

    def handle(self, *args, **options):
        user_agents = [ua.user_agent for ua in UserAgent.objects.all()]
        mc = MetaCriticScraper(user_agents)
        print('Scraping %s' % ' and '.join(options['platforms']))
        if options['platforms'] == ['update']:
            options['join'] = True
            options['platforms'] = ['ps3', 'ps4', 'vita']
        else:
            for platform in options['platforms']:
                try:
                    mc.scrape(platform)
                    self.stdout.write(self.style.NOTICE('Scraped %s' % platform))
                except OperationalError as err:
                    raise CommandError(err)
                except Exception as err:
                    raise CommandError('Could not scrape metacritic for %s games:  %s' % (platform, err))

        self.stdout.write(self.style.SUCCESS('Successfully Scraped %s' % ' & '.join(options['platforms'])))

        if 'trophy_scrape' in options and options['trophy_scrape']:
            try:
                tc = TrophyScraper(user_agents)
                tc.scrape()
                self.stdout.write(self.style.SUCCESS('Successfully Scraped trophies from ps3trophes.com'))
            except OperationalError as err:
                raise CommandError(err)
            except Exception as err:
                raise CommandError('Error scraping trophies: %s' % err)

        if 'join' in options and options['join']:
            joined_games, game_data = [], []
            trophy_data = json.load(open(os.path.join(DATA_DIR, 'trophies.json'), 'r'))
            for platform in options['platforms']:
                filename = platform + '.json'
                temp = json.load(open(os.path.join(DATA_DIR, filename), 'r'))
                game_data.extend(temp)
            
            self.stdout.write(self.style.NOTICE('Joining %s metacritic records with %s trophy records' % (len(game_data), len(trophy_data))))

            for game in game_data: # only games with scores to be added.
                final = {}
                for trophy in trophy_data:
                    if trophy['id'] == game['id']:
                        for k, v in game.iteritems():
                            final[k] = v
                        for k, v in trophy.iteritems():
                            if k not in final:
                                final[k] = v
                        joined_games.append(final)
                        break

            final_file = os.path.join(DATA_DIR, 'playstation_game.json')
            with open(final_file, 'w') as outfile:
                json.dump(joined_games, outfile, indent=4, sort_keys=True)
            self.stdout.write(self.style.SUCCESS('Successfully Wrote %s games to %s' % (len(joined_games), final_file)))

        self.stdout.write(self.style.SUCCESS('Success!'))

