from django.core.management.base import BaseCommand, CommandError
from django.db.utils import OperationalError
from tropheo.models import UserAgent

from tropheo.settings import DATA_DIR
from tropheo.scrapers import MetaCriticScraper, TrophyScraper

import os.path


class Command(BaseCommand):

    help = 'Reads json file scraped from web and updates the database'

    def handle(self, *args, **options):
        filename = 'user_agents.txt'
        current_user_agents = {ua.user_agent: True for ua in UserAgent.objects.all()}
        i = 0
        try:
            user_agents = []
            with open(os.path.join(DATA_DIR, filename), 'r') as user_agent_file:
                for user_agent in user_agent_file.readlines():
                    if user_agent and user_agent not in current_user_agents:
                        user_agent = user_agent.strip()[1:-1-1]
                        if user_agent not in current_user_agents: 
                            UserAgent.objects.create(user_agent=user_agent)
                            i += 1
        except Exception as err:
            self.stderr.write(self.style.ERROR(CommandError(err)))

        self.stdout.write(self.style.SUCCESS('Successfully added %s new user agents to the database.' % i))
