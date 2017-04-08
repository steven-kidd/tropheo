from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from tropheo.models import Game

import os.path
import json

from tropheo.settings import DATA_DIR



class Command(BaseCommand):

    help = 'Reads json file scraped from web and updates the database'

    def handle(self, *args, **options):
        filename = 'playstation_game.json'
        try:
            joined_games = json.load(open(os.path.join(DATA_DIR, filename), 'r'))
        except:
            raise CommandError('%s is not a valid file. Try running "python manage.py scrape [...]" first' % filename)

        joined_ids = set(g['id'] for g in joined_games)

        db_ids = set(g.id for g in Game.objects.filter(id__in=joined_ids))

        new_ids = joined_ids.symmetric_difference(db_ids)

        skipped_game_ids = []
        # update new games from file.
        for game in joined_games:
            # add the new games to the database
            if game['id'] in new_ids:
                try:
                    Game.objects.create(**game)
                except IntegrityError as err:
                    skipped_game_ids.append(game['id'])
                    print('Skipped %s due to error %s' % (game, err))
            else: # check if there's new data, and update it.
                Game.objects.filter(id=game['id']).update(**game)

        self.stdout.write(self.style.NOTICE('Skipped %s new games.' % len(skipped_game_ids)))
        self.stdout.write(self.style.SUCCESS('Successfully added %s new games to the database and updated %s existing games.' % \
                                             (len(new_ids) - len(skipped_game_ids), len(db_ids))))
