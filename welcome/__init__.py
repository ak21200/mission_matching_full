from otree.api import *


doc = """
Your app description
"""



class Constants(BaseConstants):
    name_in_url = 'welcome'
    players_per_group = None
    num_rounds = 1



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class Splash(Page):
    pass


class Welcome(Page):
    pass


class Introduction(Page):
    pass


page_sequence = [
    Splash,
    Welcome,
    Introduction,
]
