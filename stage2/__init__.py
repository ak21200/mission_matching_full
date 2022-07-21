
import time
import json

from otree import settings
from otree.api import *

from sliders.image_utils import encode_image
from sliders import task_sliders

doc = """
"""


class Constants(BaseConstants):
    name_in_url = 'stage2'
    players_per_group = None
    num_rounds = 5
    earnings_per_round = cu(1.50)


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        p.participant.app_payoffs = {}
        p.participant.rounds = {}
        p.participant.stage_donation = {}


    session = subsession.session
    defaults = dict(
        trial_delay=1.0,
        retry_delay=0.1,
        num_sliders=48,
        num_columns=3,
        attempts_per_slider=50
    )
    session.params = {}
    for param in defaults:
        session.params[param] = session.config.get(param, defaults[param])


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    iteration = models.IntegerField(initial=0)
    participated = models.IntegerField(initial=0)
    num_correct = models.IntegerField(initial=0)
    potential_payoff = models.CurrencyField()
    charity = models.StringField()
    donation_amount = models.CurrencyField()
    piece_rate = models.CurrencyField()


# puzzle-specific stuff


class Puzzle(ExtraModel):
    """A model to keep record of sliders setup"""

    player = models.Link(Player)
    iteration = models.IntegerField()
    timestamp = models.FloatField()

    num_sliders = models.IntegerField()
    layout = models.LongStringField()

    response_timestamp = models.FloatField()
    num_correct = models.IntegerField(initial=0)
    is_solved = models.BooleanField(initial=False)


class Slider(ExtraModel):
    """A model to keep record of each slider"""

    puzzle = models.Link(Puzzle)
    idx = models.IntegerField()
    target = models.IntegerField()
    value = models.IntegerField()
    is_correct = models.BooleanField(initial=False)
    attempts = models.IntegerField(initial=0)


def generate_puzzle(player: Player) -> Puzzle:
    """Create new puzzle for a player"""
    params = player.session.params
    num = params['num_sliders']
    layout = task_sliders.generate_layout(params)
    puzzle = Puzzle.create(
        player=player, iteration=player.iteration, timestamp=time.time(),
        num_sliders=num,
        layout=json.dumps(layout)
    )
    for i in range(num):
        target, initial = task_sliders.generate_slider()
        Slider.create(
            puzzle=puzzle,
            idx=i,
            target=target,
            value=initial
        )
    return puzzle


def get_current_puzzle(player):
    puzzles = Puzzle.filter(player=player, iteration=player.iteration)
    if puzzles:
        [puzzle] = puzzles
        return puzzle


def get_slider(puzzle, idx):
    sliders = Slider.filter(puzzle=puzzle, idx=idx)
    if sliders:
        [puzzle] = sliders
        return puzzle


def encode_puzzle(puzzle: Puzzle):
    """Create data describing puzzle to send to client"""
    layout = json.loads(puzzle.layout)
    sliders = Slider.filter(puzzle=puzzle)
    # generate image for the puzzle
    image = task_sliders.render_image(layout, targets=[s.target for s in sliders])
    return dict(
        image=encode_image(image),
        size=layout['size'],
        grid=layout['grid'],
        sliders={s.idx: {'value': s.value, 'is_correct': s.is_correct} for s in sliders}
    )


def get_progress(player: Player):
    """Return current player progress"""
    return dict(
        iteration=player.iteration,
        solved=player.num_correct
    )


def handle_response(puzzle, slider, value):
    slider.value = task_sliders.snap_value(value, slider.target)
    slider.is_correct = slider.value == slider.target
    puzzle.num_correct = len(Slider.filter(puzzle=puzzle, is_correct=True))
    puzzle.is_solved = puzzle.num_correct == puzzle.num_sliders


def play_game(player: Player, message: dict):

    session = player.session
    my_id = player.id_in_group
    params = session.params

    now = time.time()
    # the current puzzle or none
    puzzle = get_current_puzzle(player)

    message_type = message['type']

    if message_type == 'load':
        p = get_progress(player)
        if puzzle:
            return {my_id: dict(type='status', progress=p, puzzle=encode_puzzle(puzzle))}
        else:
            return {my_id: dict(type='status', progress=p)}

    if message_type == "new":
        if puzzle is not None:
            raise RuntimeError("trying to create 2nd puzzle")

        player.iteration += 5
        z = generate_puzzle(player)
        p = get_progress(player)

        return {my_id: dict(type='puzzle', puzzle=encode_puzzle(z), progress=p)}

    if message_type == "value":
        if puzzle is None:
            raise RuntimeError("missing puzzle")
        if puzzle.response_timestamp and now < puzzle.response_timestamp + params["retry_delay"]:
            raise RuntimeError("retrying too fast")

        slider = get_slider(puzzle, int(message["slider"]))

        if slider is None:
            raise RuntimeError("missing slider")
        if slider.attempts >= params['attempts_per_slider']:
            raise RuntimeError("too many slider motions")

        value = int(message["value"])
        handle_response(puzzle, slider, value)
        puzzle.response_timestamp = now
        slider.attempts += 1
        player.num_correct = puzzle.num_correct

        p = get_progress(player)
        return {
            my_id: dict(
                type='feedback',
                slider=slider.idx,
                value=slider.value,
                is_correct=slider.is_correct,
                is_completed=puzzle.is_solved,
                progress=p,
            )
        }


charity_names = {
    "CISWO": "CISWO (Coal Industry Social Welfare Organisation)",
    "Ember": "The Crowd: Ember",
    "CARE": "CARE (Christian Action, Research, and Education)",
    "BPAS": "BPAS (British Pregnancy Advisory Service)",
}

class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        if player.participant.match:
            charity = player.participant.vars['charity_rank'][1]
        else:
            charity = player.participant.vars['charity_rank'][4]
        return {
            'charity_name': charity_names[charity]
        }


class Game(Page):
    template_name = "global/Game.html"
    live_method = play_game

    @staticmethod
    def get_timeout_seconds(player: Player):
        return player.session.config['task_seconds']

    @staticmethod
    def js_vars(player: Player):
        return dict(
            params=player.session.params,
            slider_size=task_sliders.SLIDER_BBOX,
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            params=player.session.params,
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        puzzle = get_current_puzzle(player)

        if puzzle and puzzle.response_timestamp:
            player.num_correct = puzzle.num_correct
        player.participated = 1

        if (player.participant.penalty == 3 and player.num_correct > 20) or (player.participant.penalty == 4 and player.num_correct > 20):
            player.piece_rate = player.num_correct * cu(0.05) - cu(1.75)
            player.participant.app_payoffs['stage2'] = (
                player.participant.app_payoffs.get('stage2', cu(0)) +
                Constants.earnings_per_round + player.piece_rate
            )
        else:
            player.participant.app_payoffs['stage2'] = (
                    player.participant.app_payoffs.get('stage2', cu(0)) +
                    Constants.earnings_per_round
            )
        player.donation_amount = player.num_correct * cu(0.05)
        player.participant.stage_donation['stage2'] = (
                player.participant.stage_donation.get('stage2', cu(0)) +
                player.donation_amount
        )

class Results(Page):
    template_name = "global/Results.html"

    @staticmethod
    def is_displayed(player: Player):
        participant = player.participant
        return (
            player.round_number == 5 or
            (participant.penalty == 2 and player.num_correct < 20) or
            (participant.penalty == 4 and player.num_correct < 20)
        )

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'termination': player.participant.penalty == 2 and player.num_correct < 20,
            'termination': player.participant.penalty == 4 and player.num_correct < 20,
            'potential_payoff': player.participant.app_payoffs['stage2'],
        }

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        if player.participant.penalty == 2 and player.num_correct < 20:
            return 'survey'
        if player.participant.penalty == 4 and player.num_correct < 20:
            return 'survey'


page_sequence = [
    Instructions,
    Game,
    Results,
]
