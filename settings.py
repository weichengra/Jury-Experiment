"""
oTree 專案設定檔 - Jury Experiment

專案：陪審團決策研究 - FRAND 費率評估
應用程式：router (路由分配) → jury1 (Study 1) / jury2 (Study 2)

Session配置：每4人一組循環分配
  參與者1 → Study 1, Simple (3因素)
  參與者2 → Study 1, Complex (8因素)
  參與者3 → Study 2, Simple (3因素)
  參與者4 → Study 2, Complex (8因素)
  (第5位開始循環重複)

最後更新：2026年2月2日
"""
from os import environ


SESSION_CONFIGS = [
    dict(
        name='jury_combined',
        display_name="Jury Study - FRAND Rate Evaluation",
        app_sequence=['router', 'jury1', 'jury2'],
        num_demo_participants=900,
    ),
]

# Prolific 完成重定向設定
PROLIFIC_COMPLETION_CODE = environ.get('PROLIFIC_COMPLETION_CODE', 'C105YIDJ')

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
    prolific_completion_url=f"https://app.prolific.com/submissions/complete?cc={PROLIFIC_COMPLETION_CODE}"
)

PARTICIPANT_FIELDS = ['PROLIFIC_PID']
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = '1936633548744'
ALLOWED_HOSTS = ['*']  # 允許所有主機（Heroku 部署需要）

# Production vs Development mode
OTREE_PRODUCTION = environ.get('OTREE_PRODUCTION') not in {None, '', '0'}
DEBUG = False  # 永久隱藏 debug 資訊（包含本地開發）
INSTALLED_APPS = ['otree']

# 限制桌面端填寫（最小寬度1024px）
BROWSER_ROWS_TYPE = 'bootstrap3'
FORM_RENDERER = {'browser_rows': {'min_width': 1024}}
MIN_SCREEN_WIDTH = 1024

# CSV輸出UTF-8編碼
import csv
csv.register_dialect('excel-utf8', delimiter=',', quotechar='"', 
                     quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')

# 螢幕寬度限制
MIN_SCREEN_WIDTH = 1024
