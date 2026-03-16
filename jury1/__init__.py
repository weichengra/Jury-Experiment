"""Study 1: FRAND rate evaluation with 3 trials (inst=0: simple 3-factor, inst=1: complex 8-factor)"""
from otree.api import *
import random
from datetime import datetime, timezone
import requests
from os import environ


doc = """Study 1: FRAND rate evaluation"""


class C(BaseConstants):
    NAME_IN_URL = 'jury1'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    
    # FRAND rate slider settings ($0-$20, step 0.1)
    FRAND_MIN = 0
    FRAND_MAX = 20
    FRAND_STEP = 0.1
    SLIDER_TICKS = ['', '$5', '', '$15', '']
    
    # Comprehension check answers
    CORRECT_ANSWERS = {
        'comprehension_q1': 'false',
        'comprehension_q2': 'B',
        'comprehension_q3': 'C'
    }
    MAX_COMPREHENSION_ATTEMPTS = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


def creating_session(subsession: Subsession):
    """Assign treatment (inst=0: simple, inst=1: complex). Uses assigned_treatment from router in combined session."""
    for p in subsession.get_players():
        assigned_treatment = p.participant.vars.get('assigned_treatment', None)
        if assigned_treatment is not None:
            p.inst = assigned_treatment  # From router in combined session
        else:
            p.inst = (p.id_in_subsession - 1) % 2  # Alternating allocation when standalone


class Player(BasePlayer):
    # ===== 同意書 =====
    consent = models.StringField(
        choices=[['I consent', 'I consent.'], ['no_consent', 'I do NOT consent.']],
        label='',
        widget=widgets.RadioSelect,
    )
    
    # ===== Prolific ID =====
    prolific_ID = models.StringField(
        label='What is your Prolific ID?',
        blank=False,
    )

    # ===== Treatment =====
    inst = models.IntegerField(initial=0)

    # ===== 理解問題追蹤 =====
    comprehension_attempts = models.IntegerField(initial=0)
    comprehension_passed = models.BooleanField(initial=False)
    
    # ===== 理解問題 - 當前答案（最後一次作答）=====
    comprehension_q1 = models.StringField(
        choices=[
            ['true', 'True'],
            ['false', 'False']
        ],
        label='''Standard essential patent (SEP) holders, who committed to follow FRAND obligation, have market power as their patent is the recognized standard. This means SEP holders can charge any price to maximize profits from their users.''',
        widget=widgets.RadioSelect,
    )
    
    # 問題 2: Why did PhoneMaker sue NextGen?
    comprehension_q2 = models.StringField(
        choices=[
            ['A', 'A. PhoneMaker wanted to block NextGen from becoming the 6G standard;'],
            ['B', 'B. PhoneMaker claimed the $15 per device rate was too high;'],
            ['C', 'C. PhoneMaker claimed the $15 per device rate was too low;'],
            ['D', 'D. PhoneMaker wanted to block NextGen from entering the market.']
        ],
        label='Why did PhoneMaker sue NextGen?',
        widget=widgets.RadioSelect,
    )
    
    # 問題 3: How did NextGen respond?
    comprehension_q3 = models.StringField(
        choices=[
            ['A', 'A. It reduced the royalty rate;'],
            ['B', 'B. It agreed to negotiate a new FRAND rate;'],
            ['C', 'C. It countersued PhoneMaker for patent infringement damages;'],
            ['D', 'D. It withdrew its SEP recognition.']
        ],
        label='How did NextGen respond to PhoneMaker\'s lawsuit in the United States?',
        widget=widgets.RadioSelect,
    )
    
    # ===== 理解問題 - 第一次作答記錄 =====
    comprehension_q1_attempt1 = models.StringField(blank=True)
    comprehension_q2_attempt1 = models.StringField(blank=True)
    comprehension_q3_attempt1 = models.StringField(blank=True)
    
    # ===== 理解問題 - 第二次作答記錄 =====
    comprehension_q1_attempt2 = models.StringField(blank=True)
    comprehension_q2_attempt2 = models.StringField(blank=True)
    comprehension_q3_attempt2 = models.StringField(blank=True)
    
    # ===== 證據評估 E1-E8 =====
    evidence_e1 = models.StringField(
        label="E1 NextGen: NextGen's 6G technology is the most important innovation in PhoneMaker’s latest phones.",
        choices=[['Yes, legally relevant', 'Yes, legally relevant'], ['No, not legally relevant', 'No, not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e2 = models.StringField(
        label="E2 NextGen: PhoneMaker acted unfairly by purposefully prolonging the FRAND rate negotiation.",
        choices=[['Yes, legally relevant', 'Yes, legally relevant'], ['No, not legally relevant', 'No, not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e3 = models.StringField(
        label="E3 NextGen: Royalty rates typically are about $14 per driverless cars and $12 per drones, in line with the $15 per device range.",
        choices=[['Yes, legally relevant', 'Yes, legally relevant'], ['No, not legally relevant', 'No, not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e4 = models.StringField(
        label="E4 NextGen: NextGen has spent $1 billion developing its 6G technology. To break even, it needs to make at least $10 per device for all devices estimated to be sold in the next five years.",
        choices=[['Yes, legally relevant', 'Yes, legally relevant'], ['No, not legally relevant', 'No, not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e5 = models.StringField(
        label="E5 PhoneMaker: NextGen did not disclose all requested information, slowing down the negotiation.",
        choices=[['Yes, legally relevant', 'Yes, legally relevant'], ['No, not legally relevant', 'No, not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e6 = models.StringField(
        label="E6 PhoneMaker: Royalty rates typically are about $3 per digital TVs and $2 per smart thermostat, far below the $15 range.",
        choices=[['Yes, legally relevant', 'Yes, legally relevant'], ['No, not legally relevant', 'No, not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e7 = models.StringField(
        label="E7 PhoneMaker: PhoneMaker’s customers buy PhoneMaker 6G phones for new features not related to NextGen’s 6G technology.",
        choices=[['Yes, legally relevant', 'Yes, legally relevant'], ['No, not legally relevant', 'No, not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e8 = models.StringField(
        label="E8 PhoneMaker: Each PhoneMaker 6G phone sells for $500. If the royalty rate is charged higher than $5 per device, then PhoneMaker could not break even.",
        choices=[['Yes, legally relevant', 'Yes, legally relevant'], ['No, not legally relevant', 'No, not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    
    # FRAND rate evaluations (3 trials)
    frand_rate_1 = models.FloatField(
        label='the most appropriate FRAND rate($ per device)',
        min=C.FRAND_MIN,
        max=C.FRAND_MAX,
        blank=False,
    )
    
    frand_rate_2 = models.FloatField(
        label='FRAND rate that most participants would choose',
        min=C.FRAND_MIN,
        max=C.FRAND_MAX,
        blank=False,
    )
    
    negotiate_fairly_nextgen = models.StringField(
        label='',
        choices=[['Yes', 'Yes'], ['No', 'No']],
        widget=widgets.RadioSelect,
        blank=False,
    )
    negotiate_fairly_phonemaker = models.StringField(
        label='',
        choices=[['Yes', 'Yes'], ['No', 'No']],
        widget=widgets.RadioSelect,
        blank=False,
    )
    
    frand_rate_3 = models.FloatField(
        label='Re-evaluate FRAND rate based on the evidence above and the jury instructions',
        min=C.FRAND_MIN,
        max=C.FRAND_MAX,
        blank=False,
    )
    
    germany_effect = models.StringField(
        choices=[
            ['Yes', 'Yes'],
            ['No', 'No'],
        ],
        label="In your answer to the previous question (FRAND rate), did you take the German court's decision into consideration?",
        widget=widgets.RadioSelect,
        blank=False,
    )
    
    # 開放式回答
    germany_influenced = models.LongStringField(
        label='Please explain your choice.',
        blank=True,
    )
    
    frand_rate_4 = models.FloatField(
        label='Re-evaluate FRAND rate based on the evidence above and the jury instructions',
        min=C.FRAND_MIN,
        max=C.FRAND_MAX,
        blank=False,
    )
    
    post_survey_followup_q1 = models.LongStringField(
        label='Please explain your choice.',
        blank=False,
    )

    # Demographics
    demographic_q1 = models.StringField(
        label='Have you ever served on a jury?',
        choices=[
            ['No', 'No'],
            ['Yes_once', 'Yes, once.'],
            ['Yes_multiple', 'Yes, multiple times.'],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    demographic_q2 = models.StringField(
        label='Have you ever been involved in a lawsuit?',
        choices=[
            ['No', 'No'],
            ['Plaintiff', 'Yes, and I was the plaintiff'],
            ['Defendant', 'Yes, and I was the defendant'],
            ['Lawyer', 'Yes, and I was the lawyer'],
            ['Witness', 'Yes, and I was a witness'],
            ['Dont_know', 'I do not know'],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    demographic_q3 = models.StringField(
        label='What was your total household income before taxes during the past 12 months?',
        choices=[
            ['<25k', 'Less than $25,000'],
            ['25-49k', '$25,000-$49,999'],
            ['50-74k', '$50,000-$74,999'],
            ['75-99k', '$75,000-$99,999'],
            ['100-149k', '$100,000-$149,999'],
            ['150k+', '$150,000 or more'],
            ['Prefer_not', 'Prefer not to say'],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    demographic_q4 = models.StringField(
        label='Do you consider yourself liberal or conservative?',
        choices=[
            ['Liberal', 'Liberal'],
            ['Considerative', 'Considerative'],
            ['Neither', 'Neither'],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    demographic_q5 = models.StringField(
        label='Generally speaking, do you usually think of yourself as a Republican, a Democrat, an Independent, or something else?',
        choices=[
            ['Independent', 'Independent'],
            ['Republican', 'Republican'],
            ['Democrat', 'Democrat'],
            ['Other', 'Other'],
            ['None of the above', 'None of the above'],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    demographic_q6 = models.StringField(
        label='What is the highest level of education you have completed?',
        choices=[
            ['Some_high_school', 'Some high school or less'],
            ['High_school', 'High school diploma or GED'],
            ['Some_college', 'Some college, but no degree'],
            ['Associate', 'Associates or technical degree'],
            ['Bachelor', "Bachelor’s degree"],
            ['Graduate', 'Graduate or professional degree (MA, MS, MBA, PhD, JD, MD, DDS etc.)'],
            ['Prefer_not', 'Prefer not to say'],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    demographic_q7 = models.StringField(
        label='Did your curriculum in college or graduate school include courses in mathematics or other physical sciences?',
        choices=[['Yes', 'Yes'], ['No', 'No']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    demographic_q8 = models.StringField(
        label='Did your curriculum in college or graduate school include courses in finance/economics/accounting/business management?',
        choices=[['Yes', 'Yes'], ['No', 'No']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    demographic_q9 = models.StringField(
        label='Did you attend law school?',
        choices=[
            ['Yes_graduated', 'Yes and I graduated from it.'],
            ['Yes_attending', 'Yes (in attendance)'],
            ['Yes_not_complete', 'Yes, but I did not complete the program.'],
            ['No', 'No'],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    
    
    
    # Page duration tracking
    survey_duration = models.FloatField(blank=True)
    duration_consent = models.FloatField(blank=True)
    duration_prolific_ID = models.FloatField(blank=True)
    duration_comprehension_1 = models.FloatField(blank=True)
    duration_comprehension_2 = models.FloatField(blank=True)
    duration_failure = models.FloatField(blank=True)
    duration_success = models.FloatField(blank=True)
    duration_main_study = models.FloatField(blank=True)
    duration_germany_info = models.FloatField(blank=True)
    duration_post_survey_yes = models.FloatField(blank=True)
    duration_post_survey_no = models.FloatField(blank=True)
    duration_demographics_combined = models.FloatField(blank=True)
    duration_demographic_q7 = models.FloatField(blank=True)
    duration_demographic_q8 = models.FloatField(blank=True)
    duration_demographic_q9 = models.FloatField(blank=True)
    duration_end_survey = models.FloatField(blank=True)
    
    # reCAPTCHA verification
    recaptcha_response = models.LongStringField(blank=True)

    # Slider interaction history (comma-separated values)
    frand_rate_1_history = models.LongStringField(blank=True)
    frand_rate_2_history = models.LongStringField(blank=True)
    frand_rate_3_history = models.LongStringField(blank=True)
    frand_rate_4_history = models.LongStringField(blank=True)

    # Mouse tracking data (JSON per page)
    mouse_tracking_data = models.LongStringField(blank=True)
    mouse_tracking_consent = models.LongStringField(blank=True)
    mouse_tracking_prolific_ID = models.LongStringField(blank=True)
    mouse_tracking_comprehension_1 = models.LongStringField(blank=True)
    mouse_tracking_comprehension_2 = models.LongStringField(blank=True)
    mouse_tracking_failure = models.LongStringField(blank=True)
    mouse_tracking_exit_instruction = models.LongStringField(blank=True)
    mouse_tracking_success = models.LongStringField(blank=True)
    mouse_tracking_main_study = models.LongStringField(blank=True)
    mouse_tracking_germany_info = models.LongStringField(blank=True)
    mouse_tracking_post_survey_yes = models.LongStringField(blank=True)
    mouse_tracking_post_survey_no = models.LongStringField(blank=True)
    mouse_tracking_demographics_combined = models.LongStringField(blank=True)
    mouse_tracking_demographic_q7 = models.LongStringField(blank=True)
    mouse_tracking_demographic_q8 = models.LongStringField(blank=True)
    mouse_tracking_demographic_q9 = models.LongStringField(blank=True)
    mouse_tracking_end_survey = models.LongStringField(blank=True)


# ===== HELPER MIXINS =====
class PassedComprehensionMixin:
    """Requires consent and comprehension check passed, ensures assigned to Study 1"""
    @staticmethod
    def is_displayed(player: Player):
        assigned_study = player.participant.vars.get('assigned_study', None)
        if assigned_study is not None and assigned_study != 1:
            return False
        return player.consent == 'I consent' and player.comprehension_passed


def with_mouse_tracking(fields):
    """Add mouse tracking field to form"""
    base = fields or []
    if 'mouse_tracking_data' in base:
        return base
    return base + ['mouse_tracking_data']


def verify_recaptcha(response_token: str) -> tuple[bool, str]:
    """Verify reCAPTCHA response token. Returns (success, error_message)."""
    if not response_token:
        return False, 'Please complete the reCAPTCHA verification.'
    secret_key = environ.get('RECAPTCHA_SECRET_KEY', '6LcGaDUsAAAAAEk-gqW-dtU90jeXGnY2ROEkQfdK')
    try:
        r = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={'secret': secret_key, 'response': response_token},
            timeout=5
        )
        result = r.json()
        if not result.get('success'):
            return False, 'reCAPTCHA verification failed. Please try again.'
        return True, ''
    except Exception:
        return False, 'Could not verify reCAPTCHA. Please check your internet connection.'


class PageDurationMixin:
    """Track page viewing duration"""
    duration_field = None
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        frame = None
        try:
            import inspect
            frame = inspect.currentframe()
            caller_locals = frame.f_back.f_locals
            page_class = caller_locals.get('self').__class__
            field_name = getattr(page_class, 'duration_field', None)
        finally:
            del frame
            
        if not field_name:
            return
            
        page_start_key = f'{field_name}_start'
        if page_start_key in player.participant.vars:
            start_time = player.participant.vars[page_start_key]
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
                
            now = datetime.now(timezone.utc)
            duration = round((now - start_time).total_seconds(), 1)
            setattr(player, field_name, duration)
            
            # 清除臨時變數
            del player.participant.vars[page_start_key]


def check_comprehension(player: Player):
    """檢查理解問題是否答對"""
    return all([
        player.comprehension_q1 == C.CORRECT_ANSWERS['comprehension_q1'],
        player.comprehension_q2 == C.CORRECT_ANSWERS['comprehension_q2'],
        player.comprehension_q3 == C.CORRECT_ANSWERS['comprehension_q3']
    ])


def is_prolific_id_duplicate(player: Player, prolific_id: str) -> bool:
    """
    檢查 Prolific ID 是否已被其他參與者使用
    每人只能填寫一次，防止重複參與
    
    oTree 6.0 版本：使用 participant.vars 儲存所有參與者的 Prolific ID
    """
    if not prolific_id or not str(prolific_id).strip():
        return False
    
    prolific_id = str(prolific_id).strip().lower()
    session = player.session
    current_participant = player.participant
    
    # Check for duplicate Prolific ID across participants using participant.vars
    for participant in session.get_participants():
        if participant.id_in_session != current_participant.id_in_session:
            stored_id = participant.vars.get('prolific_id', None)
            if stored_id and str(stored_id).strip().lower() == prolific_id:
                return True
    
    return False


# Page classes

class AssignedStudyMixin:
    """Check if participant is assigned to Study 1 (when using router)"""
    @staticmethod
    def is_displayed(player: Player):
        assigned_study = player.participant.vars.get('assigned_study', None)
        if assigned_study is not None:
            return assigned_study == 1
        return True  # Display if no router assignment (standalone jury1)


class Consent(AssignedStudyMixin, Page):
    form_model = 'player'
    form_fields = with_mouse_tracking(['consent'])
    
    @staticmethod
    def is_displayed(player: Player):
        if not AssignedStudyMixin.is_displayed(player):
            return False
        now = datetime.now(timezone.utc)
        player.participant.vars['survey_start_time'] = now
        player.participant.vars['page_start_consent'] = now
        return True
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_consent' in player.participant.vars:
            start = player.participant.vars['page_start_consent']
            player.duration_consent = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_consent = player.mouse_tracking_data


class ProlificID(Page):
    form_model = 'player'
    form_fields = with_mouse_tracking(['prolific_ID'])
    
    @staticmethod
    def is_displayed(player: Player):
        if not AssignedStudyMixin.is_displayed(player):
            return False
        if player.consent == 'I consent':
            player.participant.vars['page_start_prolific'] = datetime.now(timezone.utc)
            return True
        return False
    
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'prolific_pid': player.participant.label or '',
        }

    @staticmethod
    def error_message(player: Player, values):
        """每人只能填寫一次：檢查 Prolific ID 是否已被使用"""
        prolific_id = values.get('prolific_ID', '')
        if is_prolific_id_duplicate(player, prolific_id):
            return 'This Prolific ID has already been used in this study. Each person can only participate once.'
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_prolific' in player.participant.vars:
            start = player.participant.vars['page_start_prolific']
            player.duration_prolific_ID = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_prolific_ID = player.mouse_tracking_data
        # 儲存 Prolific ID 到 participant.vars 以供重複檢查
        if player.prolific_ID:
            player.participant.vars['prolific_id'] = str(player.prolific_ID).strip().lower()


class ComprehensionQuestions(Page):
    form_model = 'player'
    form_fields = with_mouse_tracking(['comprehension_q1', 'comprehension_q2', 'comprehension_q3'])
    
    @staticmethod
    def is_displayed(player: Player):
        # 檢查是否被分配到此 Study
        if not AssignedStudyMixin.is_displayed(player):
            return False
        should_display = (
            player.consent == 'I consent'
            and (not player.comprehension_passed)
            and player.comprehension_attempts < C.MAX_COMPREHENSION_ATTEMPTS
        )
        if should_display:
            attempt = player.comprehension_attempts + 1
            player.participant.vars[f'page_start_comp_{attempt}'] = datetime.now(timezone.utc)
        return should_display
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        attempt = player.comprehension_attempts + 1
        start_key = f'page_start_comp_{attempt}'
        
        # 記錄這次作答
        if attempt == 1:
            player.comprehension_q1_attempt1 = player.comprehension_q1
            player.comprehension_q2_attempt1 = player.comprehension_q2
            player.comprehension_q3_attempt1 = player.comprehension_q3
        elif attempt == 2:
            player.comprehension_q1_attempt2 = player.comprehension_q1
            player.comprehension_q2_attempt2 = player.comprehension_q2
            player.comprehension_q3_attempt2 = player.comprehension_q3
        
        if start_key in player.participant.vars:
            start = player.participant.vars[start_key]
            duration = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
            if attempt == 1:
                player.duration_comprehension_1 = duration
                if player.mouse_tracking_data:
                    player.mouse_tracking_comprehension_1 = player.mouse_tracking_data
            elif attempt == 2:
                player.duration_comprehension_2 = duration
                if player.mouse_tracking_data:
                    player.mouse_tracking_comprehension_2 = player.mouse_tracking_data
        
        player.comprehension_attempts += 1
        player.comprehension_passed = check_comprehension(player)


class Failure(Page):
    form_model = 'player'
    form_fields = with_mouse_tracking([])
    
    @staticmethod
    def is_displayed(player: Player):
        # 檢查是否被分配到此 Study
        if not AssignedStudyMixin.is_displayed(player):
            return False
        should_display = (
            player.consent == 'I consent'
            and (not player.comprehension_passed)
            and player.comprehension_attempts == 1
        )
        if should_display:
            player.participant.vars['page_start_failure'] = datetime.now(timezone.utc)
        return should_display
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_failure' in player.participant.vars:
            start = player.participant.vars['page_start_failure']
            player.duration_failure = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_failure = player.mouse_tracking_data


class ExitInstruction(Page):
    form_model = 'player'
    form_fields = with_mouse_tracking([])
    
    @staticmethod
    def is_displayed(player: Player):
        # 檢查是否被分配到此 Study
        if not AssignedStudyMixin.is_displayed(player):
            return False
        should_display = (
            player.consent == 'I consent'
            and (not player.comprehension_passed)
            and player.comprehension_attempts >= C.MAX_COMPREHENSION_ATTEMPTS
        )
        if should_display:
            player.participant.vars['page_start_exit_instruction'] = datetime.now(timezone.utc)
        return should_display
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.mouse_tracking_data:
            player.mouse_tracking_exit_instruction = player.mouse_tracking_data
        
        # 計算總問卷時長（即使未通過理解測驗也要記錄）
        survey_start = player.participant.vars.get('survey_start_time')
        if survey_start:
            player.survey_duration = round((datetime.now(timezone.utc) - survey_start).total_seconds(), 1)
        elif player.participant.time_started_utc:
            start_time = player.participant.time_started_utc
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
                
            now = datetime.now(timezone.utc)
            player.survey_duration = round((now - start_time).total_seconds(), 1)


class Success(PassedComprehensionMixin, Page):
    form_model = 'player'
    form_fields = with_mouse_tracking([])
    
    @staticmethod
    def is_displayed(player: Player):
        should_display = PassedComprehensionMixin.is_displayed(player)
        if should_display:
            player.participant.vars['page_start_success'] = datetime.now(timezone.utc)
        return should_display
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_success' in player.participant.vars:
            start = player.participant.vars['page_start_success']
            player.duration_success = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_success = player.mouse_tracking_data


class MainStudyIntegrated(PassedComprehensionMixin, Page):
    """主研究：證據評估 + FRAND 費率"""
    form_model = 'player'
    form_fields = with_mouse_tracking([
        'evidence_e1', 'evidence_e2', 'evidence_e3', 'evidence_e4',
        'evidence_e5', 'evidence_e6', 'evidence_e7', 'evidence_e8',
        'frand_rate_1', 'frand_rate_2',
        'negotiate_fairly_nextgen', 'negotiate_fairly_phonemaker',
        'frand_rate_1_history', 'frand_rate_2_history',
    ])
    
    @staticmethod
    def is_displayed(player: Player):
        should_display = PassedComprehensionMixin.is_displayed(player)
        if should_display:
            player.participant.vars['page_start_mainstudy'] = datetime.now(timezone.utc)
        return should_display
    
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'min_value': C.FRAND_MIN,
            'max_value': C.FRAND_MAX,
            'step': C.FRAND_STEP,
            'slider_ticks': C.SLIDER_TICKS,
            'inst': player.inst,  # 0 或 1
        }

    @staticmethod
    def error_message(player: Player, values):
        required_fields = [
            'evidence_e1', 'evidence_e2', 'evidence_e3', 'evidence_e4',
            'evidence_e5', 'evidence_e6', 'evidence_e7', 'evidence_e8'
        ]
        for field in required_fields:
            if not values.get(field):
                return "Please answer all questions."
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_mainstudy' in player.participant.vars:
            start = player.participant.vars['page_start_mainstudy']
            player.duration_main_study = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_main_study = player.mouse_tracking_data


class GermanyInfo(PassedComprehensionMixin, Page):
    """德國案例與費率重評"""
    form_model = 'player'
    form_fields = with_mouse_tracking(['frand_rate_3', 'germany_effect', 'germany_influenced', 'frand_rate_3_history'])

    @staticmethod
    def is_displayed(player: Player):
        should_display = PassedComprehensionMixin.is_displayed(player)
        if should_display:
            player.participant.vars['page_start_germany'] = datetime.now(timezone.utc)
        return should_display

    @staticmethod
    def vars_for_template(player: Player):
        prev = player.field_maybe_none('frand_rate_1')
        return {
            'min_value': C.FRAND_MIN,
            'max_value': C.FRAND_MAX,
            'step': C.FRAND_STEP,
            'slider_ticks': C.SLIDER_TICKS,
            'previous_frand': prev if prev is not None else '',
        }
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_germany' in player.participant.vars:
            start = player.participant.vars['page_start_germany']
            player.duration_germany_info = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_germany_info = player.mouse_tracking_data


class PostSurveyInfo_Yes(PassedComprehensionMixin, Page):
    """後續問卷 - 受德國影響"""
    form_model = 'player'
    form_fields = with_mouse_tracking(['frand_rate_4', 'post_survey_followup_q1', 'frand_rate_4_history', 'recaptcha_response'])
    
    @staticmethod
    def is_displayed(player: Player):
        gi = player.field_maybe_none('germany_effect')
        should_display = PassedComprehensionMixin.is_displayed(player) and gi == 'Yes'
        if should_display:
            player.participant.vars['page_start_postsurvey_yes'] = datetime.now(timezone.utc)
        return should_display
    
    @staticmethod
    def vars_for_template(player: Player):
        prev = player.field_maybe_none('frand_rate_3')
        return {
            'min_value': C.FRAND_MIN,
            'max_value': C.FRAND_MAX,
            'step': C.FRAND_STEP,
            'slider_ticks': C.SLIDER_TICKS,
            'previous_frand': prev if prev is not None else '',
        }
    
    @staticmethod
    def error_message(player: Player, values):
        success, error_msg = verify_recaptcha(values.get('recaptcha_response'))
        if not success:
            return error_msg

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_postsurvey_yes' in player.participant.vars:
            start = player.participant.vars['page_start_postsurvey_yes']
            player.duration_post_survey_yes = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_post_survey_yes = player.mouse_tracking_data


class PostSurveyInfo_No(PassedComprehensionMixin, Page):
    """後續問卷 - 未受德國影響"""
    form_model = 'player'
    form_fields = with_mouse_tracking(['frand_rate_4', 'post_survey_followup_q1', 'frand_rate_4_history', 'recaptcha_response'])
    
    @staticmethod
    def is_displayed(player: Player):
        gi = player.field_maybe_none('germany_effect')
        should_display = PassedComprehensionMixin.is_displayed(player) and gi == 'No'
        if should_display:
            player.participant.vars['page_start_postsurvey_no'] = datetime.now(timezone.utc)
        return should_display
    
    @staticmethod
    def vars_for_template(player: Player):
        prev = player.field_maybe_none('frand_rate_3')
        return {
            'min_value': C.FRAND_MIN,
            'max_value': C.FRAND_MAX,
            'step': C.FRAND_STEP,
            'slider_ticks': C.SLIDER_TICKS,
            'previous_frand': prev if prev is not None else '',
        }
    
    @staticmethod
    def error_message(player: Player, values):
        success, error_msg = verify_recaptcha(values.get('recaptcha_response'))
        if not success:
            return error_msg

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_postsurvey_no' in player.participant.vars:
            start = player.participant.vars['page_start_postsurvey_no']
            player.duration_post_survey_no = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_post_survey_no = player.mouse_tracking_data


class DemographicsCombinedPage(PassedComprehensionMixin, Page):
    """人口統計 Q1-Q6"""
    form_model = 'player'
    form_fields = with_mouse_tracking([
        'demographic_q1',
        'demographic_q2',
        'demographic_q3',
        'demographic_q4',
        'demographic_q5',
        'demographic_q6',
    ])
    
    @staticmethod
    def is_displayed(player: Player):
        should_display = PassedComprehensionMixin.is_displayed(player)
        if should_display:
            player.participant.vars['page_start_demographics'] = datetime.now(timezone.utc)
        return should_display
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_demographics' in player.participant.vars:
            start = player.participant.vars['page_start_demographics']
            player.duration_demographics_combined = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_demographics_combined = player.mouse_tracking_data


class DemographicQ7(PassedComprehensionMixin, Page):
    """數學/理科背景（大學以上）"""
    form_model = 'player'
    form_fields = with_mouse_tracking(['demographic_q7'])
    
    @staticmethod
    def is_displayed(player: Player):
        edu = player.field_maybe_none('demographic_q6')
        should_display = (
            PassedComprehensionMixin.is_displayed(player)
            and edu in ['Some_college', 'Associate', 'Bachelor', 'Graduate']
        )
        if should_display:
            player.participant.vars['page_start_demog_q7'] = datetime.now(timezone.utc)
        return should_display
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_demog_q7' in player.participant.vars:
            start = player.participant.vars['page_start_demog_q7']
            player.duration_demographic_q7 = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_demographic_q7 = player.mouse_tracking_data


class DemographicQ8(PassedComprehensionMixin, Page):
    """商科/經濟背景（大學以上）"""
    form_model = 'player'
    form_fields = with_mouse_tracking(['demographic_q8'])
    
    @staticmethod
    def is_displayed(player: Player):
        edu = player.field_maybe_none('demographic_q6')
        should_display = (
            PassedComprehensionMixin.is_displayed(player)
            and edu in ['Some_college', 'Associate', 'Bachelor', 'Graduate']
        )
        if should_display:
            player.participant.vars['page_start_demog_q8'] = datetime.now(timezone.utc)
        return should_display
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_demog_q8' in player.participant.vars:
            start = player.participant.vars['page_start_demog_q8']
            player.duration_demographic_q8 = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_demographic_q8 = player.mouse_tracking_data


class DemographicQ9(PassedComprehensionMixin, Page):
    """法學院經驗（學士以上）"""
    form_model = 'player'
    form_fields = with_mouse_tracking(['demographic_q9'])
    
    @staticmethod
    def is_displayed(player: Player):
        edu = player.field_maybe_none('demographic_q6')
        should_display = (
            PassedComprehensionMixin.is_displayed(player)
            and edu in ['Bachelor', 'Graduate']
        )
        if should_display:
            player.participant.vars['page_start_demog_q9'] = datetime.now(timezone.utc)
        return should_display
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'page_start_demog_q9' in player.participant.vars:
            start = player.participant.vars['page_start_demog_q9']
            player.duration_demographic_q9 = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_demographic_q9 = player.mouse_tracking_data


class EndOfSurvey(PassedComprehensionMixin, Page):
    """研究結束"""
    form_model = 'player'
    form_fields = with_mouse_tracking(['recaptcha_response'])

    @staticmethod
    def is_displayed(player: Player):
        if not PassedComprehensionMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_end_survey'] = datetime.now(timezone.utc)
        return True

    @staticmethod
    def error_message(player: Player, values):
        success, error_msg = verify_recaptcha(values.get('recaptcha_response'))
        if not success:
            return error_msg

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_end_survey')
        if start:
            player.duration_end_survey = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        if player.participant.time_started_utc:
            start_time = player.participant.time_started_utc
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            player.survey_duration = round((now - start_time).total_seconds(), 1)
        if player.mouse_tracking_data:
            player.mouse_tracking_end_survey = player.mouse_tracking_data


class ThankYouPage(PassedComprehensionMixin, Page):
    """感謝頁面，自動跳轉到 Prolific"""
    form_model = 'player'
    form_fields = []

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'prolific_url': player.session.config.get('prolific_completion_url', '')
        }


# ===== PAGE SEQUENCE =====
page_sequence = [
    Consent,
    ProlificID,
    ComprehensionQuestions,
    Failure,
    ComprehensionQuestions,
    ExitInstruction,
    Success,
    MainStudyIntegrated,
    GermanyInfo,
    PostSurveyInfo_No,
    PostSurveyInfo_Yes,
    DemographicsCombinedPage,
    DemographicQ7,
    DemographicQ8,
    DemographicQ9,
    EndOfSurvey,
    ThankYouPage,
]

