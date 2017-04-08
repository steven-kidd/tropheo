from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView, UpdateView
from django.contrib import messages
from django.core.paginator import Paginator

from ratelimit.decorators import ratelimit
from django.contrib.auth.mixins import LoginRequiredMixin

from registration.forms import RegistrationFormUniqueEmail

from .models import Ngame, UserAgent, Profile
from .forms import PlayStationIdForm, GameSearchForm#, RegistrationFormSet
from .psn import PlayStationNetwork as PSN

import logging
import operator


logger = logging.getLogger('django.server')

class IndexView(ListView):
    """View for home page"""
    template_name = 'index.html'
    model = Ngame
    context_object_name = 'games'
    paginate_by = 12
    paginate_orphans = 3

    def get_queryset(self, **kwargs):
        queryset = Ngame.objects.all()
        try:
            played_game_ids = self.request.user.profile._get_played_game_ids()
        except AttributeError:
            return queryset
        queryset = queryset.exclude(id__in=played_game_ids)
        return queryset.filter(weighted_score__gte=1).order_by('-weighted_score')


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)
        # Add in the publisher
        try:
            genre_data = self.request.user.profile._get_game_genres()
            if genre_data == {}:
                raise AttributeError
        except AttributeError:
            return context

        xdata = [genre for genre in genre_data if genre_data[genre] > 3]
        ydata = [genre_data[genre] for genre in xdata]

        genre_data = {
            'charttype': 'pieChart',
            'chartdata': {'x': xdata, 'y1': ydata},
            'chartcontainer': 'piechart_container',
            'extra': {
                'x_is_date': False,
                'x_axis_format': '%d',
                'tag_script_js': True,
                'jquery_on_ready': False,
                'resize': True,
                'donut': True,
                'show_labels': True,
                'margin_top': 0, 'margin_bottom': 0,
                'margin_left': 0, 'margin_right': 0,
                'color_category': 'category20c',
                # "tooltip": {"y_start": "", "y_end": " cal"}
            }
        }

        other_data = {
            'charttype': 'pieChart',
            'chartdata': {'x': xdata, 'y': ydata},
            'chartcontainer': 'otherchart_container',
            'extra': {
                'x_is_date': False,
                'x_axis_format': '%d',
                'tag_script_js': True,
                'jquery_on_ready': False,
                'resize': True,
                'donut': True,
                'show_labels': True,
                'margin_top': 0, 'margin_bottom': 0,
                'margin_left': 0, 'margin_right': 0,
                'color_category': 'category20c',
                # "tooltip": {"y_start": "", "y_end": " cal"},
            }
        }
        context.update({'genre_chart': genre_data, 'other_chart': other_data})
        return context


# Not being used?
# class RegistrationView(LoginRequiredMixin, FormView):
#     """View for signing up new users"""
#     template_name = 'registration/registration_form.html'
#     form_class = RegistrationFormUniqueEmail
#     # second_form_class = RegistrationFormUniqueEmail
#     success_url = '/register/complete/'

#     # def get_context_data(self, **kwargs):
#     #     context = super(RegistrationView, self).get_context_data(**kwargs)
#     #     if 'form' not in context:
#     #         context['form'] = self.form_class(initial={'some_field': context['model'].some_field})
#     #     if 'form2' not in context:
#     #         context['form2'] = self.second_form_class(initial={'another_field': context['model'].another_field})
#     #     return context

#     # ProfileInlineFormset = inlineformset_factory(User, Profile, fields=('website', 'bio', 'phone', 'city', 'country', 'organization'))
#     # formset = ProfileInlineFormset(instance=self.request.user)

#     def form_invalid(self, form, **kwargs):
#         context = self.get_context_data(**kwargs)
#         context['form'] = form
#         return super(RegistrationView, self).form_invalid(form)

#     def form_valid(self, form):
#         new_user = User.objects.create_user(
#                 username=form.cleaned_data['username'],
#                 password=form.cleaned_data['password1'],
#                 email=form.cleaned_data['email'],
#                 first_name=form.cleaned_data['first_name'],
#                 last_name=form.cleaned_data['last_name'],
#                 is_active=True
#         )
#         print('New User is active: %s' % new_user.is_active)
#         new_user = authenticate(username=form.cleaned_data['username'],
#                                 password=form.cleaned_data['password1'])
#         login(self.request, new_user)
#         return super(RegistrationView, self).form_valid(form)


class UpdatePlayStationProfileView(LoginRequiredMixin, FormView):
    template_name = 'registration/update_profile.html'
    success_url = '/'
    form_class = PlayStationIdForm

    def form_valid(self, form):
        ua = UserAgent.objects.all().order_by('?').first().user_agent
        psn_id = form.cleaned_data.get('psn_id')
        psn_user_data = PSN.query(psn_id, {'User-Agent': ua})
        instance = self.request.user

        if psn_user_data.is_private:
            print('user is private')
            messages.warning(self.request, '%s has their Trophy sharing settings set to private.' % \
                             form.cleaned_data['psn_id'])
            instance.profile.is_empty = False
            instance.profile.is_private = True
            instance.save()

        elif psn_user_data.is_empty:
            print('user is empty')
            messages.warning(self.request, 'Oops! %s is either a private user, or is not a valid ID.' % \
                             form.cleaned_data['psn_id'])

        else:
            # messages.success(self.request, 'Your profile has been successfully updated!')
            instance.profile.psn_id = psn_id
            instance.profile.avatar = psn_user_data.avatar
            instance.profile.is_plus = psn_user_data.is_plus
            instance.profile.level = psn_user_data.level
            instance.profile.level_progress = psn_user_data.level_progress
            instance.profile.game_count = psn_user_data.game_count
            instance.profile.platinum = psn_user_data.platinum
            instance.profile.gold = psn_user_data.gold
            instance.profile.silver = psn_user_data.silver
            instance.profile.bronze = psn_user_data.bronze
            instance.profile.is_private = psn_user_data.is_private
            instance.profile.is_empty = psn_user_data.is_empty

            instance.save()
            games = Ngame.objects.filter(pk__in=psn_user_data.played_ids)
            # good_unplayed_game_list = Ngame.objects.filter(weighted_score__gte=1).exclude(id__in=psn_user_data.played_ids)
            # page = self.request.GET.get('page', 1)
            # paginator = Paginator(good_unplayed_game_list, 20, orphans=3)
            print('%s profile games, %s games in DB' % (len(psn_user_data.played_ids), len(games)))
            for game in games:
                instance.profile.played_games.add(game)

        return super(UpdatePlayStationProfileView, self).form_valid(form)


class AboutView(TemplateView):
    """View for about page"""
    template_name = 'about.html'

# OLD STUFF, SHOULD PROBABLY DELETE

class PSNTemplateView(TemplateView):

    def _query_psn(self, request, form):
        if form.is_valid():
            ua = UserAgent.objects.all().order_by('?').first().user_agent
            user = PSN.query(form.cleaned_data['psn_id'], {'User-Agent': ua})

            if user.is_private:
                messages.warning(request, '%s has their Trophy sharing settings set to private.' % \
                                 form.cleaned_data['username'])
            elif user.is_empty:
                messages.warning(request, 'Oops! %s is either a private user, or is not a valid ID.' % \
                                 form.cleaned_data['username'])
            else:
                request.session['psn-user-data'] = user.json
                return redirect('user_found', username=form.cleaned_data['username'])

        return render(request, 'index.html', {'form': form})


class UserSearchView(PSNTemplateView):

    def get(self, request, username=None):
        if 'psn-user-data' in request.session:
            user = request.session['psn-user-data']
            if user['username'] == username:
                played_game_progress = {g['id']: g['progress'] for g in user['games']}

                all_games = Ngame.objects.all()
                played_game_list = all_games.filter(id__in=user['played_ids'])
                profile = {}
                for g in all_games:
                    for e in g.genre.split(','):
                        e1 = e.replace('[','').replace(']','')
                        if e1 not in profile:
                            profile[e1] = 1
                        else:
                            profile[e1] += 1

                good_unplayed_game_list = all_games.filter(weighted_score__gte=1).exclude(simple_id__in=user['played_simple_ids'])

                # recommended_games = # maybe game_progress as weighted average, along with "score" and 

                page = request.GET.get('page', 1)
                paginator = Paginator(good_unplayed_game_list, 20, orphans=3)
                try:
                    games = paginator.page(page)
                except PageNotAnInteger:
                    games = paginator.page(1)
                except EmptyPage:
                    games = paginator.page(paginator.num_pages)

                context = {
                    'userdata': request.session['psn-user-data'],
                    'games': games,
                    'profile': sorted(profile.items(), key=operator.itemgetter(1), reverse=True)
                }
                logger.info('%s ~ Level %s ~ %s Games Played ~ %s Platinum Trophies',
                       user['username'], user['level'], len(user['played_ids']), user['platinum'])
                return render(request, 'dashboard.html', context=context)
            else:
                request.session.flush()
                return self._query_psn(request, PlayStationIdForm({'username': username}))
        elif not username:
            return redirect('home')
        else:
            return self._query_psn(request, PlayStationIdForm({'username': username}))


class GamePageView(TemplateView):

    def get(self, request, **kwargs):
        high_level_genres = ['party', 'sports & games', 'racing', 'alternative', 'music / rhythm', 'open-world', '']
        # genres = []
        # for g in Ngame.objects.all().values('genre'):
        #     genres.extend([x.strip() for x in ast.literal_eval(g['genre'].encode('ascii'))])
        # genres = set(genres)
        # print genres
        if 'searchform' in request.GET:
            form = request.GET['searchform']
        else:
            form = GameSearchForm()

        if 'psn-user-data' in request.session:
            user = request.session['psn-user-data']
            logger.info('%s ~ Level %s ~ %s Games Played ~ %s Platinum Trophies',
                        user['username'], user['level'], len(user['played_ids']), user['platinum'])
            game_list = Ngame.objects.exclude(simple_id__in=user['played_simple_ids']).filter(weighted_score__gte=0.5).order_by('-score')
        else:
            game_list = Ngame.objects.all().order_by('-score')

        page = request.GET.get('page', 1)
        paginator = Paginator(game_list, 25, orphans=3)
        try:
            games = paginator.page(page)
        except PageNotAnInteger:
            games = paginator.page(1)
        except EmptyPage:
            games = paginator.page(paginator.num_pages)

        return render(request, 'games.html', context={'games': games, 'form': form})
