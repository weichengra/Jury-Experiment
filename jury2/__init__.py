"""Study 2: FRAND rate evaluation with 2 trials + reCAPTCHA (inst=0: simple 3-factor, inst=1: complex 8-factor)"""
from otree.api import *
import requests
from datetime import datetime, timezone
from os import environ


doc = """Study 2: FRAND rate evaluation with reCAPTCHA"""


class C(BaseConstants):
    NAME_IN_URL = 'jury2'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    FRAND_MIN = 0
    FRAND_MAX = 20
    FRAND_STEP = 0.1


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
    # Consent
    consent = models.StringField(
        choices=[['consent', 'I consent.'], ['no_consent', 'I do NOT consent.']],
        label='',
        widget=widgets.RadioSelect,
    )
    
    # Prolific ID
    prolific_id = models.StringField(
        label='What is your Prolific ID?',
        blank=False,
    )

    # Treatment
    inst = models.IntegerField(initial=0)

    # Comprehension check tracking (max 2 attempts)
    comprehension_attempts = models.IntegerField(initial=0)
    comprehension_passed = models.BooleanField(initial=False)
    
    # Comprehension questions - 當前答案（最後一次作答）
    comprehension_q1 = models.StringField(
        choices=[
            ['true', 'True'],
            ['false', 'False']
        ],
        label='''Standard essential patent (SEP) holders, who committed to follow FRAND obligation, have market power as their patent is the recognized standard. This means SEP holders can charge any price to maximize profits from their users.''',
        widget=widgets.RadioSelect,
    )
    
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
    
    comprehension_q3 = models.StringField(
        choices=[
            ['A', 'A. It reduced the royalty rate;'],
            ['B', 'B. It agreed to negotiate a new FRAND rate;'],
            ['C', 'C. It countersued PhoneMaker for patent infringement damages;'],
            ['D', 'D. It withdrew its SEP recognition.']
        ],
        label='How did NextGen respond to PhoneMaker\'s lawsuit in the United States',
        widget=widgets.RadioSelect,
    )
    
    # Comprehension questions - 第一次作答記錄
    comprehension_q1_attempt1 = models.StringField(blank=True)
    comprehension_q2_attempt1 = models.StringField(blank=True)
    comprehension_q3_attempt1 = models.StringField(blank=True)
    
    # Comprehension questions - 第二次作答記錄
    comprehension_q1_attempt2 = models.StringField(blank=True)
    comprehension_q2_attempt2 = models.StringField(blank=True)
    comprehension_q3_attempt2 = models.StringField(blank=True)
    
    # Evidence evaluation E1-E8
    evidence_e1 = models.StringField(
        label="E1 NextGen: NextGen's 6G technology is the most important innovation in PhoneMaker's latest phones.",
        choices=[['Yes,legally relevant', 'Yes,legally relevant'], ['No, not legally relevant', 'No, not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e2 = models.StringField(
        label="E2 NextGen: PhoneMaker acted unfairly by purposefully prolonging the FRAND rate negotiation.",
        choices=[['Yes,legally relevant', 'Yes,legally relevant'], ['No, not legally relevant', 'No, not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e3 = models.StringField(
        label="E3 NextGen: Royalty rates typically are about $14 per driverless cars and $12 per drones, in line with the $15 per device range.",
        choices=[['Yes,legally relevant', 'Yes,legally relevant'], ['No,not legally relevant', 'No,not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e4 = models.StringField(
        label="E4 NextGen: NextGen has spent $1 billion developing its 6G technology. To break even, it needs to make at least $10 per device for all devices estimated to be sold in the next five years.",
        choices=[['Yes,legally relevant', 'Yes,legally relevant'], ['No,not legally relevant', 'No,not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e5 = models.StringField(
        label="E5 PhoneMaker: NextGen did not disclose all requested information, slowing down the negotiation.",
        choices=[['Yes,legally relevant', 'Yes,legally relevant'], ['No,not legally relevant', 'No,not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e6 = models.StringField(
        label="E6 PhoneMaker: Royalty rates typically are about $3 per digital TVs and $2 per smart thermostat, far below the $15 range.",
        choices=[['Yes,legally relevant', 'Yes,legally relevant'], ['No,not legally relevant', 'No,not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e7 = models.StringField(
        label="E7 PhoneMaker: PhoneMaker's customers buy PhoneMaker 6G phones for new features not related to NextGen's 6G technology.",
        choices=[['Yes,legally relevant', 'Yes,legally relevant'], ['No,not legally relevant', 'No,not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    evidence_e8 = models.StringField(
        label="E8 PhoneMaker: Each PhoneMaker 6G phone sells for $500. If the royalty rate is charged higher than $5 per device, then PhoneMaker could not break even.",
        choices=[['Yes,legally relevant', 'Yes,legally relevant'], ['No,not legally relevant', 'No,not legally relevant']],
        widget=widgets.RadioSelect,
        blank=True,
    )

    # ========== FRAND Rate Slider 1 - 個人評估 ==========
    # 基於證據和陪審團指示重新評估 FRAND 費率
    frand_rate_0 = models.FloatField(
        label='Re-evaluate FRAND rate based on the evidence above and the jury instructions',
        min=C.FRAND_MIN,
        max=C.FRAND_MAX,
        blank=True,
    )

    # FRAND rate 2 - normative prediction
    frand_rate_2 = models.FloatField(
        label='FRAND rate that most participants would choose',
        min=C.FRAND_MIN,
        max=C.FRAND_MAX,
        blank=True,
    )

    # Negotiation fairness
    negotiate_fairly_nextgen = models.StringField(
        label='',
        choices=[['Yes', 'Yes'], ['No', 'No']],
        widget=widgets.RadioSelect,
        blank=True,
    )
    negotiate_fairly_phonemaker = models.StringField(
        label='',
        choices=[['Yes', 'Yes'], ['No', 'No']],
        widget=widgets.RadioSelect,
        blank=True,
    )

    # Germany court decision influence (determines page routing)
    germany_influenced = models.StringField(
        choices=[
            ['Yes', 'Yes'],
            ['No', 'No'],
        ],
        label=" ",
        widget=widgets.RadioSelect,
        blank=False,
    )

    # Explanation for Germany influence
    explain_choice = models.LongStringField(
        label='Please explain your choice.',
        blank=True,
    )

    # Revised FRAND rate after Germany info
    frand_rate_revised = models.FloatField(
        label='Re-evaluate FRAND rate based on the evidence above and the jury instructions',
        min=C.FRAND_MIN,
        max=C.FRAND_MAX,
        blank=True,
    )

    # Post-survey followup explanation
    post_survey_followup_q1 = models.LongStringField(
        label='Please explain your choice.',
        blank=True,
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
            ['Republican', 'Republican'],
            ['Democrat', 'Democrat'],
            ['Independent', 'Independent'],
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
    
    # ========== 年齡 (Age) ==========
    # 注意：此欄位目前未在任何頁面中收集（可能為保留欄位）
    age = models.IntegerField(
        label='How old are you?',
        min=18,
        max=125,
        blank=True,
    )

    # ========== 問卷結束驗證 (End of Survey) ==========
    # 包含 reCAPTCHA 驗證以防止機器人
    end_survey_verification = models.BooleanField(
        label='I am not a robot.',
        blank=True,  # 保留此欄位供結束頁面顯示；主要以 reCAPTCHA 作為實際驗證機制
    )
    recaptcha_response = models.LongStringField(blank=True)
    
    # ========== 問卷總時長 (Survey Duration) ==========
    # 從問卷開始到結束的總秒數
    survey_duration = models.FloatField(blank=True)
    
    # Page duration tracking
    duration_consent = models.FloatField(blank=True)
    duration_prolific_id = models.FloatField(blank=True)
    duration_comprehension = models.FloatField(blank=True)
    duration_failure = models.FloatField(blank=True)
    duration_exit = models.FloatField(blank=True)
    duration_success = models.FloatField(blank=True)
    duration_main_study = models.FloatField(blank=True)
    duration_germany_info = models.FloatField(blank=True)
    duration_post_survey_yes = models.FloatField(blank=True)
    duration_post_survey_no = models.FloatField(blank=True)
    duration_demographics = models.FloatField(blank=True)
    duration_demographic_q7 = models.FloatField(blank=True)
    duration_demographic_q8 = models.FloatField(blank=True)
    duration_demographic_q9 = models.FloatField(blank=True)
    duration_end_survey = models.FloatField(blank=True)
    
    # Slider interaction history
    frand_rate_0_history = models.LongStringField(blank=True)
    frand_rate_2_history = models.LongStringField(blank=True)
    frand_rate_revised_history = models.LongStringField(blank=True)
    
    # Mouse tracking data (JSON per page)
    mouse_tracking_data = models.LongStringField(blank=True)
    mouse_tracking_consent = models.LongStringField(blank=True)
    mouse_tracking_prolific_id = models.LongStringField(blank=True)
    mouse_tracking_comprehension = models.LongStringField(blank=True)
    mouse_tracking_failure = models.LongStringField(blank=True)
    mouse_tracking_exit = models.LongStringField(blank=True)
    mouse_tracking_success = models.LongStringField(blank=True)
    mouse_tracking_main_study = models.LongStringField(blank=True)
    mouse_tracking_germany_info = models.LongStringField(blank=True)
    mouse_tracking_post_survey_yes = models.LongStringField(blank=True)
    mouse_tracking_post_survey_no = models.LongStringField(blank=True)
    mouse_tracking_demographics = models.LongStringField(blank=True)
    mouse_tracking_demographic_q7 = models.LongStringField(blank=True)
    mouse_tracking_demographic_q8 = models.LongStringField(blank=True)
    mouse_tracking_demographic_q9 = models.LongStringField(blank=True)
    mouse_tracking_end_survey = models.LongStringField(blank=True)


def with_mouse_tracking(fields):
    """Add mouse tracking field to form"""
    base = fields or []
    if 'mouse_tracking_data' in base:
        return base
    return base + ['mouse_tracking_data']


def get_common_template_vars(player: Player = None) -> dict:
    """Get common template variables"""
    return {
        'MIN_SCREEN_WIDTH': 1024,
    }


def get_frand_slider_context(player: Player) -> dict:
    """Get FRAND slider context data"""
    prev = player.field_maybe_none('frand_rate_0')
    return {
        'min_value': C.FRAND_MIN,
        'max_value': C.FRAND_MAX,
        'step': C.FRAND_STEP,
        'previous_frand': prev if prev is not None else '',
    }


def verify_recaptcha(response_token: str) -> tuple[bool, str]:
    """Verify reCAPTCHA response token. Returns (success, error_message)."""
    if not response_token:
        return False, 'Please complete the reCAPTCHA verification.'
    
    secret_key = environ.get(
        'RECAPTCHA_SECRET_KEY',
        '6LexNngsAAAAAFGB7h5NkmeOuBcKYF98RT7G5YC_'
    )
    
    data = {
        'secret': secret_key,
        'response': response_token
    }
    
    try:
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data, timeout=5)
        result = r.json()
        
        if not result.get('success'):
            return False, 'reCAPTCHA verification failed. Please try again.'
        return True, ''
    except Exception:
        return False, 'Could not verify reCAPTCHA. Please check your internet connection.'


def check_comprehension(player: Player):
    """檢查理解問題是否全部答對"""
    correct_answers = {
        'comprehension_q1': 'false',
        'comprehension_q2': 'B',
        'comprehension_q3': 'C'
    }
    
    score = 0
    if player.comprehension_q1 == correct_answers['comprehension_q1']:
        score += 1
    if player.comprehension_q2 == correct_answers['comprehension_q2']:
        score += 1
    if player.comprehension_q3 == correct_answers['comprehension_q3']:
        score += 1
    
    return score == 3


# ========== PAGES ==========

class AssignedStudyMixin:
    """Check if participant is assigned to Study 2 (when using router)"""
    @staticmethod
    def is_displayed(player: Player):
        assigned_study = player.participant.vars.get('assigned_study', None)
        if assigned_study is not None:
            return assigned_study == 2
        return True


class PassedComprehensionMixin:
    """Requires consent and comprehension check passed, ensures assigned to Study 2"""
    @staticmethod
    def is_displayed(player: Player):
        assigned_study = player.participant.vars.get('assigned_study', None)
        if assigned_study is not None and assigned_study != 2:
            return False
        return player.consent == 'consent' and player.comprehension_passed


def is_prolific_id_duplicate(player: Player, prolific_id: str) -> bool:
    """Check for duplicate Prolific ID to prevent multiple participation"""
    if not prolific_id or not str(prolific_id).strip():
        return False
    
    prolific_id = str(prolific_id).strip().lower()
    session = player.session
    current_participant = player.participant
    
    # Check for duplicate ID using participant.vars
    for participant in session.get_participants():
        if participant.id_in_session != current_participant.id_in_session:
            stored_id = participant.vars.get('prolific_id', None)
            if stored_id and str(stored_id).strip().lower() == prolific_id:
                return True
    
    return False


class Consent(AssignedStudyMixin, Page):
    form_model = 'player'
    form_fields = with_mouse_tracking(['consent'])
    
    @staticmethod
    def is_displayed(player: Player):
        if not AssignedStudyMixin.is_displayed(player):
            return False
        player.participant.vars['survey_start_time'] = datetime.now(timezone.utc)
        player.participant.vars['page_start_consent'] = datetime.now(timezone.utc)
        return True
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_common_template_vars(player)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_consent')
        if start:
            player.duration_consent = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        if player.mouse_tracking_data:
            player.mouse_tracking_consent = player.mouse_tracking_data
        
        if player.consent != 'consent':
            pass


class ProlificID(Page):
    form_model = 'player'
    form_fields = with_mouse_tracking(['prolific_id'])
    
    @staticmethod
    def is_displayed(player: Player):
        if not AssignedStudyMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_prolific_id'] = datetime.now(timezone.utc)
        return player.consent == 'consent'
    
    @staticmethod
    def error_message(player: Player, values):
        """Check for duplicate Prolific ID"""
        prolific_id = values.get('prolific_id', '')
        if is_prolific_id_duplicate(player, prolific_id):
            return 'This Prolific ID has already been used in this study. Each person can only participate once.'
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_common_template_vars(player)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_prolific_id')
        if start:
            player.duration_prolific_id = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        if player.mouse_tracking_data:
            player.mouse_tracking_prolific_id = player.mouse_tracking_data
        
        if player.prolific_id:
            player.participant.vars['prolific_id'] = str(player.prolific_id).strip().lower()


class ComprehensionQuestions(Page):
    """
    理解測驗頁面
    
    內容：介紹事實 + 3 個理解問題
    流程：最多可嘗試 2 次，每次都會重新顯示此頁面
    
    """
    form_model = 'player'
    form_fields = with_mouse_tracking(['comprehension_q1', 'comprehension_q2', 'comprehension_q3'])
    
    @staticmethod
    def is_displayed(player: Player):
        if not AssignedStudyMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_comprehension'] = datetime.now(timezone.utc)
        return (
            player.consent == 'consent'
            and (not player.comprehension_passed)
            and player.comprehension_attempts < 2
        )
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_common_template_vars(player)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # 記錄這次作答
        attempt = player.comprehension_attempts + 1
        if attempt == 1:
            player.comprehension_q1_attempt1 = player.comprehension_q1
            player.comprehension_q2_attempt1 = player.comprehension_q2
            player.comprehension_q3_attempt1 = player.comprehension_q3
        elif attempt == 2:
            player.comprehension_q1_attempt2 = player.comprehension_q1
            player.comprehension_q2_attempt2 = player.comprehension_q2
            player.comprehension_q3_attempt2 = player.comprehension_q3
        
        start = player.participant.vars.get('page_start_comprehension')
        if start:
            duration = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
            current = player.field_maybe_none('duration_comprehension')
            if current is not None:
                player.duration_comprehension = round(current + duration, 1)
            else:
                player.duration_comprehension = duration
        
        if player.mouse_tracking_data:
            current_tracking = player.field_maybe_none('mouse_tracking_comprehension') or ''
            if current_tracking:
                # 如果已有資料，追加新資料（用分隔符）
                player.mouse_tracking_comprehension = current_tracking + '|||' + player.mouse_tracking_data
            else:
                player.mouse_tracking_comprehension = player.mouse_tracking_data
        
        # 結束一次 comprehension 嘗試（最多 2 次）
        player.comprehension_attempts += 1
        player.comprehension_passed = check_comprehension(player)



# 4. Failure 頁面
class Failure(Page):
    """
    第一次未通過理解測驗時顯示
    
    顯示條件：comprehension_attempts == 1 且 comprehension_passed == False
    提示：告知用戶還有一次機會
    """
    form_model = 'player'
    form_fields = with_mouse_tracking([])
    
    @staticmethod
    def is_displayed(player: Player):
        
        if not AssignedStudyMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_failure'] = datetime.now(timezone.utc)
        return (
            player.consent == 'consent'
            and (not player.comprehension_passed)
            and player.comprehension_attempts == 1
        )
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_common_template_vars(player)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_failure')
        if start:
            player.duration_failure = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_failure = player.mouse_tracking_data


# 5. ExitInstruction 頁面
class ExitInstruction(Page):
    """
    第二次未通過理解測驗時顯示並結束流程
    
    顯示條件：comprehension_attempts >= 2 且 comprehension_passed == False
    作用：終止參與者的問卷流程
    """
    form_model = 'player'
    form_fields = with_mouse_tracking([])
    
    @staticmethod
    def is_displayed(player: Player):
        
        if not AssignedStudyMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_exit'] = datetime.now(timezone.utc)
        return (
            player.consent == 'consent'
            and (not player.comprehension_passed)
            and player.comprehension_attempts >= 2
        )
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_common_template_vars(player)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_exit')
        if start:
            player.duration_exit = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_exit = player.mouse_tracking_data
        
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


# 6. Success 頁面
class Success(PassedComprehensionMixin, Page):
    """
    通過理解測驗後顯示
    
    顯示條件：comprehension_passed == True
    作用：確認通過測驗，準備進入主要研究
    """
    form_model = 'player'
    form_fields = with_mouse_tracking([])
    
    @staticmethod
    def is_displayed(player: Player):
        # 使用 PassedComprehensionMixin 的檢查
        if not PassedComprehensionMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_success'] = datetime.now(timezone.utc)
        return True
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_common_template_vars(player)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_success')
        if start:
            player.duration_success = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_success = player.mouse_tracking_data


# 7. 主研究整合頁面 (MainStudyIntegrated)
class MainStudyIntegrated(PassedComprehensionMixin, Page):
    """
    主要研究整合頁面，包含以下區塊：
    
    1. RECAP - 案件回顧
    2. COURT ORDER - 法院命令
    3. JURY INSTRUCTIONS - 陪審團指示（3 或 8 factors，由 inst 決定）
    4. EVIDENCE - 證據選擇（E1-E8，每項二選一）
    5. Negotiate Questions - 協商公平性問題（NextGen & PhoneMaker）
    6. FRAND Rate Sliders - 兩個 slider：
       - frand_rate_0: 個人評估
       - frand_rate_2: 多數參與者預測
    
    驗證：
    - 前端 JavaScript：檢查所有欄位是否填寫，顯示紅框和警告
    - 後端：檢查證據項目是否全部回答
    """
    form_model = 'player'
    form_fields = with_mouse_tracking([
        'evidence_e1', 'evidence_e2', 'evidence_e3', 'evidence_e4',  # 證據
        'evidence_e5', 'evidence_e6', 'evidence_e7', 'evidence_e8',
        'frand_rate_0', 'frand_rate_0_history',  # FRAND費率 + 歷史
        'frand_rate_2', 'frand_rate_2_history',  # FRAND費率 + 歷史
        'negotiate_fairly_nextgen', 'negotiate_fairly_phonemaker',
    ])
    
    @staticmethod
    def is_displayed(player: Player):
        # 使用 PassedComprehensionMixin 的檢查
        if not PassedComprehensionMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_main_study'] = datetime.now(timezone.utc)
        return True
    
    @staticmethod
    def vars_for_template(player: Player):
        ctx = get_common_template_vars(player)
        ctx.update({
            'min_value': C.FRAND_MIN,
            'max_value': C.FRAND_MAX,
            'step': C.FRAND_STEP,
            'inst': player.inst,  # 0 或 1
        })
        return ctx

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_main_study')
        if start:
            player.duration_main_study = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_main_study = player.mouse_tracking_data
    
    @staticmethod
    def error_message(player: Player, values):
        # 檢查是否所有證據都已回答
        evidence_fields = [
            'evidence_e1', 'evidence_e2', 'evidence_e3', 'evidence_e4',
            'evidence_e5', 'evidence_e6', 'evidence_e7', 'evidence_e8'
        ]
        # 檢查是否有任何證據未回答（是 None）
        unanswered = [f for f in evidence_fields if values.get(f) is None]
        if unanswered:
            return "Please answer all evidence items (E1-E8) before proceeding."


# 8. 德國案例資訊頁面 (GermanyInfo)
class GermanyInfo(PassedComprehensionMixin, Page):
    """
    德國案例資訊頁面
    
    內容：
    1. 德國法院判決資訊
    2. 是否受德國判決影響（germany_influenced: Yes/No）
    3. 解釋原因（explain_choice: 長文字）
    
    作用：決定後續頁面分流（PostSurveyInfo_Yes 或 PostSurveyInfo_No）
    """
    form_model = 'player'
    form_fields = with_mouse_tracking(['germany_influenced', 'explain_choice'])

    @staticmethod
    def is_displayed(player: Player):
        # 使用 PassedComprehensionMixin 的檢查
        if not PassedComprehensionMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_germany_info'] = datetime.now(timezone.utc)
        return True
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_germany_info')
        if start:
            player.duration_germany_info = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_germany_info = player.mouse_tracking_data

    @staticmethod
    def vars_for_template(player: Player):
        ctx = get_common_template_vars(player)
        ctx.update(get_frand_slider_context(player))
        return ctx


# 9. 後續調查頁面 - 受德國影響 (PostSurveyInfo_Yes)
class PostSurveyInfo_Yes(PassedComprehensionMixin, Page):
    """
    當 germany_influenced == 'Yes' 時顯示
    
    內容：
    1. 重新評估 FRAND 費率（frand_rate_revised）
    2. 解釋為何改變評估（post_survey_followup_q1）
    3. reCAPTCHA 驗證
    """
    form_model = 'player'
    form_fields = with_mouse_tracking(['frand_rate_revised', 'frand_rate_revised_history', 'post_survey_followup_q1', 'recaptcha_response'])
    
    @staticmethod
    def is_displayed(player: Player):
        # 使用 PassedComprehensionMixin 的檢查
        if not PassedComprehensionMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_post_survey_yes'] = datetime.now(timezone.utc)
        gi = player.field_maybe_none('germany_influenced')
        return gi == 'Yes'
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_post_survey_yes')
        if start:
            player.duration_post_survey_yes = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_post_survey_yes = player.mouse_tracking_data
    
    @staticmethod
    def vars_for_template(player: Player):
        ctx = get_common_template_vars(player)
        ctx.update(get_frand_slider_context(player))
        return ctx

    @staticmethod
    def error_message(player: Player, values):
        # 使用共用的 reCAPTCHA 驗證函數
        success, error_msg = verify_recaptcha(values.get('recaptcha_response'))
        if not success:
            return error_msg


# 10. 後續調查頁面 - 未受德國影響 (PostSurveyInfo_No)
class PostSurveyInfo_No(PassedComprehensionMixin, Page):
    """
    當 germany_influenced == 'No' 時顯示
    
    內容：
    1. 重新評估 FRAND 費率（frand_rate_revised）
    2. 解釋為何維持評估（post_survey_followup_q1）
    3. reCAPTCHA 驗證
    """
    form_model = 'player'
    form_fields = with_mouse_tracking(['frand_rate_revised', 'frand_rate_revised_history', 'post_survey_followup_q1', 'recaptcha_response'])
    
    @staticmethod
    def is_displayed(player: Player):
        # 使用 PassedComprehensionMixin 的檢查
        if not PassedComprehensionMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_post_survey_no'] = datetime.now(timezone.utc)
        gi = player.field_maybe_none('germany_influenced')
        return gi == 'No'
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_post_survey_no')
        if start:
            player.duration_post_survey_no = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_post_survey_no = player.mouse_tracking_data
    
    @staticmethod
    def vars_for_template(player: Player):
        ctx = get_common_template_vars(player)
        ctx.update(get_frand_slider_context(player))
        return ctx

    @staticmethod
    def error_message(player: Player, values):
        # 使用共用的 reCAPTCHA 驗證函數
        success, error_msg = verify_recaptcha(values.get('recaptcha_response'))
        if not success:
            return error_msg


# 11. 人口統計主頁面 (DemographicsCombinedPage)
class DemographicsCombinedPage(PassedComprehensionMixin, Page):
    """
    人口統計主頁面
    
    內容：收集 6 個基本人口統計問題（Q1-Q6）
    Q6 (教育程度) 的回答會決定是否顯示後續條件問題 (Q7-Q9)
    """
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
        # 使用 PassedComprehensionMixin 的檢查
        if not PassedComprehensionMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_demographics'] = datetime.now(timezone.utc)
        return True
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_common_template_vars(player)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_demographics')
        if start:
            player.duration_demographics = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_demographics = player.mouse_tracking_data


# 12. 人口統計 Q7 - 數學/物理課程 (DemographicQ7)
class DemographicQ7(PassedComprehensionMixin, Page):
    """
    條件顯示：當 Q6 教育程度為 Some_college, Associate, Bachelor, Graduate 時
    問題：是否修習過數學或物理科學課程
    """
    form_model = 'player'
    form_fields = with_mouse_tracking(['demographic_q7'])
    
    @staticmethod
    def is_displayed(player: Player):
        # 使用 PassedComprehensionMixin 的檢查
        if not PassedComprehensionMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_demographic_q7'] = datetime.now(timezone.utc)
        edu = player.field_maybe_none('demographic_q6')
        return edu in ['Some_college', 'Associate', 'Bachelor', 'Graduate']
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_common_template_vars(player)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_demographic_q7')
        if start:
            player.duration_demographic_q7 = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_demographic_q7 = player.mouse_tracking_data


# 13. 人口統計 Q8 - 商學課程 (DemographicQ8)
class DemographicQ8(PassedComprehensionMixin, Page):
    """
    條件顯示：當 Q6 教育程度為 Some_college, Associate, Bachelor, Graduate 時
    問題：是否修習過財金/經濟/會計/企管課程
    """
    form_model = 'player'
    form_fields = with_mouse_tracking(['demographic_q8'])
    
    @staticmethod
    def is_displayed(player: Player):
        # 使用 PassedComprehensionMixin 的檢查
        if not PassedComprehensionMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_demographic_q8'] = datetime.now(timezone.utc)
        edu = player.field_maybe_none('demographic_q6')
        return edu in ['Some_college', 'Associate', 'Bachelor', 'Graduate']
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_common_template_vars(player)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_demographic_q8')
        if start:
            player.duration_demographic_q8 = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_demographic_q8 = player.mouse_tracking_data


# 14. 人口統計 Q9 - 法學院 (DemographicQ9)
class DemographicQ9(PassedComprehensionMixin, Page):
    """
    條件顯示：當 Q6 教育程度為 Bachelor 或 Graduate 時
    問題：是否就讀過法學院
    """
    form_model = 'player'
    form_fields = with_mouse_tracking(['demographic_q9'])
    
    @staticmethod
    def is_displayed(player: Player):
        # 使用 PassedComprehensionMixin 的檢查
        if not PassedComprehensionMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_demographic_q9'] = datetime.now(timezone.utc)
        edu = player.field_maybe_none('demographic_q6')
        return edu in ['Bachelor', 'Graduate']
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_common_template_vars(player)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start = player.participant.vars.get('page_start_demographic_q9')
        if start:
            player.duration_demographic_q9 = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_demographic_q9 = player.mouse_tracking_data


# 15. 問卷結束頁面 (EndOfSurvey)
class EndOfSurvey(PassedComprehensionMixin, Page):
    """
    問卷結束頁面
    
    內容：
    1. 感謝訊息
    2. reCAPTCHA 驗證（防止機器人）
    3. 計算並儲存總問卷時長（survey_duration）
    """
    form_model = 'player'
    form_fields = with_mouse_tracking(['end_survey_verification', 'recaptcha_response'])

    @staticmethod
    def is_displayed(player: Player):
        # 使用 PassedComprehensionMixin 的檢查
        if not PassedComprehensionMixin.is_displayed(player):
            return False
        player.participant.vars['page_start_end_survey'] = datetime.now(timezone.utc)
        return True

    @staticmethod
    def vars_for_template(player: Player):
        return get_common_template_vars(player)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # 記錄本頁停留時間
        start = player.participant.vars.get('page_start_end_survey')
        if start:
            player.duration_end_survey = round((datetime.now(timezone.utc) - start).total_seconds(), 1)
        
        # 直接複製本頁滑鼠軌跡
        if player.mouse_tracking_data:
            player.mouse_tracking_end_survey = player.mouse_tracking_data
        
        # 計算總問卷時長
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
        
        # 儲存 Prolific 重定向 URL 到 participant.vars
        prolific_url = player.session.config.get('prolific_completion_url', '')
        if prolific_url:
            player.participant.vars['prolific_redirect'] = prolific_url

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        # 直接重定向到 Prolific
        prolific_url = player.participant.vars.get('prolific_redirect', '')
        if prolific_url:
            from otree.api import Redirect
            return Redirect(prolific_url)

    @staticmethod
    def error_message(player: Player, values):
        # 使用共用的 reCAPTCHA 驗證函數
        success, error_msg = verify_recaptcha(values.get('recaptcha_response'))
        if not success:
            return error_msg


# ========== PAGE SEQUENCE ==========
# 流程說明：
# - Comprehension 最多進行 2 次：第一次未通過會顯示 Failure 與第二次機會；第二次未通過會顯示 ExitInstruction 結束流程
# - `inst` 決定陪審團指示顯示簡易 (3 factors) 或複雜 (8 factors)
page_sequence = [
    Consent,
    ProlificID,
    # Comprehension attempt 1
    ComprehensionQuestions,
    Failure,
    # Comprehension attempt 2
    ComprehensionQuestions,
    ExitInstruction,
    Success,

    # Main study - 整合成單一頁面
    MainStudyIntegrated,  # 包含所有主要研究內容

    GermanyInfo,

    # PostSurvey block
    PostSurveyInfo_No,
    PostSurveyInfo_Yes,

    # Demographics (combined only)
    DemographicsCombinedPage,
    DemographicQ7,
    DemographicQ8,
    DemographicQ9,
    EndOfSurvey,
]

