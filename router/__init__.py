"""
Router - 自動分配參與者到Study 1或Study 2

每4人一組循環分配：
  參與者1 → Study 1, Simple
  參與者2 → Study 1, Complex
  參與者3 → Study 2, Simple
  參與者4 → Study 2, Complex
  (第5位開始循環)
"""
from otree.api import *


doc = "Router: 自動分配參與者到不同Study"


class C(BaseConstants):
    NAME_IN_URL = 'router'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


def creating_session(subsession: Subsession):
    """四人一組循環分配"""
    for p in subsession.get_players():
        participant_id = p.participant.id_in_session
        position_in_cycle = (participant_id - 1) % 4
        
        if position_in_cycle < 2:
            p.assigned_study = 1
            p.assigned_treatment = position_in_cycle
        else:
            p.assigned_study = 2
            p.assigned_treatment = position_in_cycle - 2
        
        # 設定清楚的study_condition標示
        study_name = f"Study {p.assigned_study}"
        treatment_name = "Simple" if p.assigned_treatment == 0 else "Complex"
        p.study_condition = f"{study_name} - {treatment_name}"
        
        p.participant.vars['assigned_study'] = p.assigned_study
        p.participant.vars['assigned_treatment'] = p.assigned_treatment


class Player(BasePlayer):
    assigned_study = models.IntegerField()  # 1=Study1, 2=Study2
    assigned_treatment = models.IntegerField()  # 0=Simple, 1=Complex
    study_condition = models.StringField()  # 清楚標示：例如 "Study 1 - Simple"


class RoutePage(Page):
    """路由頁面"""
    
    @staticmethod
    def vars_for_template(player: Player):
        treatment_name = 'Simple' if player.assigned_treatment == 0 else 'Complex'
        return dict(
            assigned_study=player.assigned_study,
            assigned_treatment=player.assigned_treatment,
            treatment_name=treatment_name,
            participant_id=player.participant.id_in_session,
        )
    
    @staticmethod
    def js_vars(player: Player):
        return dict(assigned_study=player.assigned_study)


page_sequence = [RoutePage]
