from otree.api import *


class Constants(BaseConstants):
    name_in_url = 'survey'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gender = models.IntegerField(
        label='What gender do you identify as?',
        choices=[
            [1, 'Male'],
            [2, 'Female'],
            [3, 'Other'],
            [4, 'Prefer not to say']
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    ethnicity = models.IntegerField(
        choices=[
            [1, 'White'],
            [2, 'Asian or Asian British'],
            [3, 'Black, Black British, Caribbean or African'],
            [4, 'Mixed or multiple ethnic groups'],
            [5, 'Other'],
            [6, 'Prefer no to say']
        ],
        label='Which is your ethnic group?',
        widget=widgets.RadioSelect,
        blank=True,
    )
    employment_status = models.IntegerField(
        label='What is your current employment status?',
        choices=[
            [1, 'Employed (full-time)'],
            [2, 'Employed (part-time)'],
            [3, 'Unpaid work'],
            [4, 'Unemployed']
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    strength_ciswo = models.IntegerField(
        choices=[
            [0, 'Strongly disagree'],
            [1, 'Somewhat disagree'],
            [2, 'Neither agree nor disagree'],
            [3, 'Somewhat agree'],
            [4, 'Strongly agree']
        ],
        widget=widgets.RadioSelectHorizontal,
        label=''
    )
    strength_ember = models.IntegerField(
        choices=[
            [0, 'Strongly disagree'],
            [1, 'Somewhat disagree'],
            [2, 'Neither agree nor disagree'],
            [3, 'Somewhat agree'],
            [4, 'Strongly agree']
        ],
        widget=widgets.RadioSelectHorizontal,
        label=''
    )
    strength_care = models.IntegerField(
        choices=[
            [0, 'Strongly disagree'],
            [1, 'Somewhat disagree'],
            [2, 'Neither agree nor disagree'],
            [3, 'Somewhat agree'],
            [4, 'Strongly agree']
        ],
        widget=widgets.RadioSelectHorizontal,
        label=''
    )
    strength_bpas = models.IntegerField(
        choices=[
            [0, 'Strongly disagree'],
            [1, 'Somewhat disagree'],
            [2, 'Neither agree nor disagree'],
            [3, 'Somewhat agree'],
            [4, 'Strongly agree']
        ],
        widget=widgets.RadioSelectHorizontal,
        label=''
    )
    age = models.IntegerField(
        label="How old are you?",
        blank=True,
    )
    countryborn = models.StringField(
        label="Which country (or countries) were you a citizen of when you were born?",
        blank=True,
    )

    countrynow = models.StringField(
        label="In which country is your current permanent residence? "
              "(If you are in the UK on a student visa, this is where 'home' is.)",
        blank=True,
    )

    department = models.StringField(
        label="In which School are you currently enrolled? (For example, BIO, ECO, EDU, ...)",
        blank=True,
    )
    degree = models.IntegerField(
        label="What type of degree course are you currently enrolled on?",
        choices=[
            [1, 'INTO'],
            [2, 'Bachelor'],
            [3, 'PG Diploma'],
            [4, 'Master'],
            [5, 'PhD'],
            [6, 'I am a member of staff'],
            [7, 'Other degree course or affiliation'],
            [8, 'Prefer not to say']
        ],
        widget=widgets.RadioSelect,
        blank=True,
        initial=None
    )

    timeuea = models.IntegerField(
        label="How long have you been at UEA?",
        choices=[
            [1, "This is my first year"],
            [2, "This is my second year"],
            [3, "This is my third year"],
            [4, "This is my fourth year"],
            [5, "I have been here more than four years"],
            [6, "Prefer not to say"]
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )

# FUNCTIONS
# PAGES


class Introduction(Page):
    pass


class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'gender', 'ethnicity', 'employment_status', 'age', 'countryborn',
        'countrynow', 'department', 'degree', 'timeuea'
    ]


class MissionStrength(Page):
    form_model = 'player'
    form_fields = ['strength_ciswo', 'strength_ember', 'strength_care', 'strength_bpas']


page_sequence = [
    Introduction,
    MissionStrength,
    Demographics,
]
