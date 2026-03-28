import requests
import time
import random
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict
import pytz
import qrcode
from io import BytesIO
import os
import threading
import logging
import sys
import socket
import urllib3
import pickle
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
from PIL import Image, ImageDraw, ImageFont
import hashlib
import mimetypes

# غیرفعال کردن warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ======================
# تنظیمات لاگ
# ======================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ======================
# تنظیمات بات
# ======================
BOT_TOKEN = "1717974974:BH5JRsUqofb7dAyA4XGqRvSZDVNBh9loEuo"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/"

# ======================
# ✅ لیست ادمین‌های اصلی
# ======================
MASTER_ADMINS = [759010455]

# ======================
# لینک‌ها
# ======================
SUPPORT_LINK = "@ostadhossein8893"
ADS_LINK = "@ostadhossein8893"

# ======================
# سیستم ارسال همگانی
# ======================
all_groups = set()
group_names = {}
user_contacts = {}

broadcast_stats = {
    "total_broadcasts": 0,
    "total_messages_sent": 0,
    "last_broadcast": None
}
broadcast_status = {}

# ======================
# سیستم فعالسازی گروه
# ======================
active_groups = set()
activation_time = {}
ignored_messages = set()

# ======================
# پاسخ‌های سرگرمی ثابت
# ======================
responses = {
    "سلام": ["خوبی.", "چه خبر؟", "سلام علیکم", "درود", "سلام گل", "علیک سلام"],
    "این چه سمیه": ["همینه که هست", "برو عشق کن", "سوختی؟", "دوس داری بگی سم؟"],
    "خوبی": ["آره بابا", "قربونت. تو چی؟", "خوبم مرسی", "عالی", "دمت گرم"],
    "قوانین": ["📜 قوانین گروه:\n1. احترام متقابل\n2. عدم ارسال فحش\n3. عدم تبلیغات\n4. موضوعات مناسب"],
    "خداحافظ": ["🗣️ بای بای", "📞 بعداً می‌بینمت", "💚 مرسی که بودی", "🕊️ به امید دیدار"],
    "چه خبر": ["📰 خبر خاصی نیست", "🌞 همه چی آرومه", "🔥 تو بگو چه خبر", "💨 همینجوری داریم می‌گذرونیم"],
    "بیا": ["🚶 دارم میام", "🏃‍♂️ یه لحظه صبر کن", "⌛ رسیدم چی کار داری؟"],
    "دوس داری": ["❤️ آره", "💔 نه", "🤔 بستگی داره به چی", "👍 اوکیه"],
    "باحالی": ["😊 تو هم باحالی", "🤝 دستت درد نکنه", "💙 ممنون لطف داری"],
    "یاور": ["جانم؟","در خدمتم.","کاری داری؟"]
}

# ======================
# دیتابیس کلمات
# ======================
word_database = {
    "سلام": "Hello", "خوبی": "How are you?", "ممنون": "Thank you",
    "خداحافظ": "Goodbye", "صبح بخیر": "Good morning", "شب بخیر": "Good night",
    "عشق": "Love", "دوست": "Friend", "خانواده": "Family", "کار": "Work",
    "مدرسه": "School", "کتاب": "Book", "ماشین": "Car", "خانه": "House",
    "آب": "Water", "غذا": "Food", "آسمان": "Sky", "زمین": "Earth",
    "آتش": "Fire", "باد": "Wind", "باران": "Rain", "برف": "Snow",
    "خورشید": "Sun", "ماه": "Moon", "ستاره": "Star", "گل": "Flower",
    "درخت": "Tree", "پرنده": "Bird", "ماهی": "Fish", "اسب": "Horse",
}

# ======================
# دانستنی‌های جالب
# ======================
fun_facts = [
    "🐧 پنگوئن‌ها می‌توانند تا ۱.۵ متر به بالا بپرند!",
    "🦒 زرافه‌ها فقط ۳۰ دقیقه در روز می‌خوابند!",
    "🐘 فیل‌ها تنها حیواناتی هستند که نمی‌توانند بپرند!",
    "🦷 حلزون‌ها حدود ۲۵۰۰۰ دندان دارند!",
    "🐝 زنبورها برای تولید ۱ کیلوگرم عسل، باید ۴ میلیون بار روی گل‌ها بنشینند!",
    "🌍 ۹۰٪ از جمعیت جهان در نیمکره شمالی زندگی می‌کنند!",
    "🌊 ۹۴٪ از موجودات زنده جهان در اقیانوس‌ها هستند!",
    "🔥 آتش‌فشان‌ها می‌توانند تا ۱۰۰۰ درجه سانتیگراد دما داشته باشند!",
    "❄️ قطب جنوب سردترین نقطه زمین با دمای -۸۹ درجه است!",
    "🌈 رنگین‌کمان در واقع یک دایره کامل است، ولی ما فقط نیمی از آن را می‌بینیم!",
    "💡 مغز انسان در طول روز ۲۰٪ از انرژی بدن را مصرف می‌کند!",
    "👃 انسان می‌تواند بیش از ۱ تریلیون بوی مختلف را تشخیص دهد!",
    "👁️ چشم انسان می‌تواند ۱۰ میلیون رنگ مختلف را ببیند!",
    "💪 زبان قوی‌ترین عضله بدن است!",
    "🦷 مینای دندان سخت‌ترین ماده در بدن انسان است!",
]

# ======================
# رپ‌های خفن
# ======================
raps = [
    """
🎤 **رپ اختصاصی یاور**

من یاور هستم میام تو گروه
با هر کی باشی میزنمش به توپ
اگه بخوای جوک بگی یا حال کنی
بیا با من دوست شو تو این محیط شاد
    """,
    """
🎤 **یاور توی گروه**

هر کی بگه سلام میام جواب میدم
با یه لبخند قشنگ همه رو خوشحال میدم
اگه بخوای بازی یا چیستان بگی
منم با تو میام تا ببینیم کی برنده می‌شه
    """,
    """
🎤 **بچه‌های با حال**

تو این گروه همه با هم رفیقیم
با یاور کنار هم همیشه شادیم
اگه یه روزی دلتو کسی شکست
بیا به من بگو تا باهات همدرد شم
    """,
    """
🎤 **یاور همیشه هست**

هر وقت دلت گرفت یا ناراحت شدی
یاور رو صدا کن تا باهات حرف بزنه
با یه لبخند قشنگ حالتو عوض کنه
همیشه کنارتم فراموشت نکنم
    """,
]

# ======================
# اس ام اس عاشقانه
# ======================
love_sms = [
    "❤️ هر جا باشی، دلم پیش توئه...",
    "💕 دوست دارم وقتی می‌خندی، دنیا قشنگ‌تر می‌شه...",
    "💗 تو اومدی و زندگیم رنگ گرفت...",
    "💖 بدون تو هوای دلم بارونیه...",
    "💝 دلم برای یه لبخند ساده‌ات تنگ شده...",
    "💓 عشق یعنی تو باشی و من دیوونه‌ات...",
    "💞 گاهی یه نگاه کافیه تا دنیا رو فراموش کنی...",
    "💘 تو رو خدا یه بارم شده به فکرم باش...",
    "💟 همیشه ته دلم یه چیزی هست به اسم عشق تو...",
]

# ======================
# فال حافظ
# ======================
hafez_fal = [
    """
🍃 **فال حافظ**

الا یا ایها الساقی ادر کأسا و ناولها
که عشق آسان نمود اول ولی افتاد مشکل‌ها

**تفسیر:**
در کارهایت عجله نکن. هر چیزی به وقت خودش.
صبر داشته باش و به خدا توکل کن.
    """,
    """
🍃 **فال حافظ**

صبا وقت سحر بویی ز زلف یار می‌آورد
دل شیدای ما را بوی آن دلدار می‌آورد

**تفسیر:**
خبرهای خوبی به تو می‌رسد. منتظر یک اتفاق خوشایند باش.
کسی که دوستش داری به تو نزدیک می‌شود.
    """,
    """
🍃 **فال حافظ**

دوش دیدم که ملایک در میخانه زدند
گل آدم بسرشتند و به پیمانه زدند

**تفسیر:**
امروز روز خوبی برای شروع کارهای جدید است.
به خدا توکل کن و قدم بردار.
    """,
    """
🍃 **فال حافظ**

صلاح کار کجا و من خراب کجا
ببین تفاوت ره از کجاست تا به کجا

**تفسیر:**
مسیر زندگی خود را پیدا کرده‌ای. به راهت ادامه بده.
موفقیت در انتظار توست.
    """,
    """
🍃 **فال حافظ**

یوسف گمگشته باز آید به کنعان غم مخور
کلبه احزان شود روزی گلستان غم مخور

**تفسیر:**
غمگین نباش، مشکلات تمام می‌شوند.
روزهای خوب در راه است.
    """,
]

# ======================
# پیام‌های انگیزشی
# ======================
motivation = [
    "💪 هر روز یک قدم به هدفت نزدیک‌تر می‌شی، ادامه بده!",
    "🌟 تو می‌تونی به هر چی می‌خوای برسی، فقط باور داشته باش!",
    "✨ ناامیدی بزرگترین دشمن موفقیت است، پس همیشه امیدوار باش!",
    "🎯 به راهت ادامه بده، موفقیت در انتظارته!",
    "🌠 از امروز شروع کن، فردا دیر شده!",
    "⭐️ هیچکس نمی‌تونه بهت بگه نمی‌تونی، جز خودت!",
    "⚡️ قدرتی که دنبالشی، همیشه درون تو بوده!",
]

# ======================
# معماهای جالب
# ======================
riddles_cool = [
    {"q": "چیست آن که هر چه بیشتر از آن برداری، بزرگتر می‌شود؟", "a": "چاله", "hint": "توی زمین هست"},
    {"q": "آن چیست که چشم دارد ولی نمی‌بیند؟", "a": "سیب زمینی", "hint": "خوراکیه"},
    {"q": "آن چیست که هر چه بیشتر به آن بدهی، کمتر می‌شود？", "a": "شمع", "hint": "توی تاریکی استفاده می‌شه"},
    {"q": "کدام ماه ۲۸ روز دارد؟", "a": "همه ماه‌ها", "hint": "به تقویم نگاه کن"},
    {"q": "چیست آن که با نفس کشیدن می‌میرد؟", "a": "آتش", "hint": "با آب هم می‌میره"},
    {"q": "آن چیست که همیشه می‌آید ولی هرگز نمی‌رسد؟", "a": "فردا", "hint": "وقتی میاد اسمش عوض می‌شه"},
    {"q": "چیست آن که مال توست ولی دیگران بیشتر از تو استفاده می‌کنند؟", "a": "اسم تو", "hint": "همه صدات می‌زنن"},
    {"q": "چه چیز را می‌شکند بی آن که لمسش کنی؟", "a": "قول", "hint": "بهش وفا نمی‌کنی"},
    {"q": "چه دریاچه‌ای هیچ آبی ندارد؟", "a": "نقشه", "hint": "توی کتاب جغرافی هست"},
]

# ======================
# نقل قول‌های معروف
# ======================
quotes = [
    "📚 **شکسپیر:** بودن یا نبودن، مسئله این است!",
    "📚 **مولانا:** تو مپندار که من شعر به خود می‌گویم، عاشقم عاشق و دیوانه آن دلبر خویش",
    "📚 **حافظ:** دوش دیدم که ملایک در میخانه زدند، گل آدم بسرشتند و به پیمانه زدند",
    "📚 **سعدی:** بنی آدم اعضای یک پیکرند، که در آفرینش ز یک گوهرند",
    "📚 **نیچه:** آنچه ما را نکشد، قوی‌ترمان می‌کند",
    "📚 **انیشتین:** تخیل مهمتر از دانش است",
    "📚 **ویل دورانت:** تمدن رودی است با دو ساحل",
    "📚 **چخوف:** کوتاهی سخن، خواهر استعداد است",
]

# ======================
# سوالات مسابقه
# ======================
quiz_questions = [
    {"q": "پایتخت ایران کجاست؟", "options": ["تهران", "اصفهان", "شیراز", "مشهد"], "a": "تهران"},
    {"q": "کدام سیاره به سیاره سرخ معروف است؟", "options": ["مریخ", "زهره", "مشتری", "زحل"], "a": "مریخ"},
    {"q": "مادر حضرت موسی چه نام داشت؟", "options": ["یوکابد", "هاجر", "ساره", "مریم"], "a": "یوکابد"},
    {"q": "کدام حیوان سریع‌ترین حیوان خشکی است？", "options": ["یوزپلنگ", "شیر", "پلنگ", "اسب"], "a": "یوزپلنگ"},
    {"q": "بزرگترین اقیانوس جهان کدام است؟", "options": ["آرام", "اطلس", "هند", "قطبی"], "a": "آرام"},
]

# ======================
# دسته‌بندی کلمات
# ======================
word_categories = {
    "عمومی": ["پایتخت", "کتاب", "مدرسه", "دانشگاه", "کامپیوتر", "تلفن", "ماشین", "هواپیما"],
    "حیوانات": ["شیر", "پلنگ", "فیل", "زرافه", "خرگوش", "موش", "گربه", "سگ"],
    "میوه‌ها": ["سیب", "پرتقال", "موز", "انگور", "هندوانه", "کیوی", "انار", "گیلاس"],
    "رنگ‌ها": ["قرمز", "آبی", "سبز", "زرد", "بنفش", "نارنجی", "صورتی", "قهوه‌ای"],
    "مشاغل": ["دکتر", "مهندس", "معلم", "خلبان", "نجار", "نقاش", "راننده", "آشپز"]
}

# ======================
# تنظیمات گروه
# ======================
group_config = {}

# ======================
# قفل‌های اصلی
# ======================
LOCK_GIF = False
LOCK_STICKER = False
LOCK_PHOTO = False
LOCK_VIDEO = False
LOCK_VOICE = False
LOCK_FILE = False
LOCK_FORWARD = False
LOCK_CONTACT = False
LOCK_LOCATION = False
LOCK_COMMAND = False
LOCK_BOT = False
LOCK_PERSIAN = False
LOCK_ENGLISH = False
LOCK_HASHTAG = False
LOCK_REPLY = False
LOCK_SWEAR = True
LOCK_ADVANCED = False

# ======================
# تنظیمات پیشرفته
# ======================
AUTO_LOCK = False
GROUP_LOCK = False
STRICT_MODE = False
GROUP_RULES = "📜 قوانین گروه:\n1. احترام متقابل\n2. عدم ارسال فحش\n3. عدم تبلیغات\n4. موضوعات مناسب"
LINK_FILTER = False
ALLOWED_LINKS = []
ALLOWED_DOMAINS = ["t.me", "telegram.me", "bale.ai", "balemessenger.com"]

LINK_PATTERNS = [
    r'https?://[^\s]+',
    r'www\.[^\s]+',
    r't\.me/[^\s]+',
    r'telegram\.me/[^\s]+',
    r'bale\.ai/[^\s]+',
    r'balemessenger\.com/[^\s]+',
    r'@[a-zA-Z0-9_]+',
    r'[a-zA-Z0-9_]+\.(com|org|ir|net|me|tv)/[^\s]*',
]

# ======================
# سیستم آنتی اسپم
# ======================
ANTI_SPAM_ENABLED = True
spam_count = {}
spam_time = {}
duplicate_messages = {}
MAX_SPAM_COUNT = 5

# ======================
# سیستم مجازات
# ======================
punishments = {}
warnings = {}
warning_reasons = {}
MAX_WARNINGS = 3
banned_users = set()
kick_log = []

# ======================
# امنیت و لاگ
# ======================
security_log = []
MAX_LOG_SIZE = 1000
admin_alerts = True

# ======================
# سیستم خوشامدگویی
# ======================
WELCOME_ENABLED = True
WELCOME_MESSAGE = """👋 سلام {user} خوش اومدی به گروه!

📜 لطفاً قوانین رو مطالعه کن:
{rules}

🎉 از حضورت خوشحالیم!"""
welcomed_users = set()

# ======================
# سیستم تیکت
# ======================
tickets = {}
ticket_counter = 0

# ======================
# آمار گروه
# ======================
group_stats = {
    "total_messages": 0,
    "today_messages": 0,
    "last_reset": datetime.now().date().isoformat(),
    "active_users": {},
    "spam_detected": 0,
    "warnings_issued": 0,
    "kicks_performed": 0,
    "security_alerts": 0,
    "punishments": {
        "ban": 0,
        "ban_pulse": 0,
        "mute": 0,
        "success_mute": 0
    }
}

# ======================
# بازی‌ها
# ======================
games = {
    "word_game": {
        "active": False,
        "word": "",
        "hint": "",
        "players": {},
        "start_time": None,
        "duration": 60,
        "category": "",
        "attempts": {}
    },
    "riddle": {
        "active": False,
        "question": "",
        "answer": "",
        "prize": 0,
        "hint_count": 0,
        "start_time": None
    },
    "mafia": {
        "active": False,
        "players": {},
        "roles": {},
        "phase": "night",
        "day": 1,
        "votes": {},
        "mafia_kill": None,
        "detective_check": None,
        "doctor_save": None,
        "start_time": None
    },
    "word_chain": {
        "active": False,
        "last_word": "",
        "last_char": "",
        "players": [],
        "current_player": None,
        "used_words": set(),
        "scores": {},
        "start_time": None
    },
    "quiz": {
        "active": False,
        "question": None,
        "answers": {},
        "correct_answer": "",
        "points": 10,
        "time_left": 30,
        "start_time": None
    }
}

# ======================
# بازی حدس عدد
# ======================
number_game = {
    "active": False,
    "number": 0,
    "min": 0,
    "max": 100,
    "players": {},
    "guesses": {},
    "start_time": None,
    "end_time": None,
    "chat_id": None
}

# ======================
# بازی اسم فامیل
# ======================
name_family_game = {
    "active": False,
    "letter": "",
    "categories": ["اسم", "فامیل", "شهر", "کشور", "غذا", "میوه", "حیوان", "رنگ", "ماشین", "شغل"],
    "answers": {},
    "players": set(),
    "start_time": None,
    "time_limit": 60
}

# ======================
# سیستم امتیاز و سطح‌بندی
# ======================
SCORE_SYSTEM_ENABLED = True
user_scores = {}
user_levels = {}

level_thresholds = {
    1: 0,
    2: 100,
    3: 300,
    4: 600,
    5: 1000,
    6: 1500,
    7: 2100,
    8: 2800,
    9: 3600,
    10: 4500,
}

level_titles = {
    1: "تازه وارد",
    2: "عضو فعال",
    3: "کاربر معمولی",
    4: "کاربر با تجربه",
    5: "عضو ویژه",
    6: "کاربر حرفه‌ای",
    7: "کارشناس گروه",
    8: "استاد",
    9: "افسانه",
    10: "الهه گروه"
}

# ======================
# کلمات ممنوعه
# ======================
banned_words = ["گمشو", "خر", "فحش", "کثافت", "بی‌شرف", "کونی", "جاکش", "حرومزاده"]
strict_banned_words = ["جنده", "روسپی", "خائن", "نامرد", "بی‌غیرت", "بیکار", "بی‌سواد", "بی‌شعور"]

# ======================
# محدودیت‌ها
# ======================
last_reply_time = {}
COOLDOWN = 0.5

# ======================
# توابع کمکی
# ======================
def is_master_admin(user_id):
    return user_id in MASTER_ADMINS

def is_persian(text):
    persian_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(persian_pattern.search(text))

def is_english(text):
    english_pattern = re.compile(r'[a-zA-Z]')
    return bool(english_pattern.search(text))

def has_hashtag(text):
    return '#' in text

def has_link(text):
    if not text:
        return False
    text = text.lower()
    for pattern in LINK_PATTERNS:
        if re.search(pattern, text):
            return True
    words = text.split()
    for word in words:
        if '.' in word and len(word) > 4:
            if not word.replace('.', '').isalnum():
                parts = word.split('.')
                if len(parts) >= 2 and len(parts[-1]) >= 2:
                    return True
    return False

def is_allowed_link(text):
    if not LINK_FILTER:
        return True
    text = text.lower()
    for domain in ALLOWED_DOMAINS:
        if domain in text:
            return True
    for link in ALLOWED_LINKS:
        if link.lower() in text:
            return True
    return False

def is_admin(chat_id, user_id):
    try:
        response = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": chat_id,
            "user_id": user_id
        })
        if response.status_code == 200:
            data = response.json()
            status = data.get("result", {}).get("status", "")
            return status in ["administrator", "creator"]
    except:
        pass
    return False

def is_creator(chat_id, user_id):
    try:
        response = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": chat_id,
            "user_id": user_id
        })
        if response.status_code == 200:
            data = response.json()
            status = data.get("result", {}).get("status", "")
            return status == "creator"
    except:
        pass
    return False

def get_user_info(user):
    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")
    username = user.get("username", "")

    if username:
        return f"@{username}"
    elif first_name or last_name:
        return f"{first_name} {last_name}".strip()
    else:
        return f"کاربر {user['id']}"

def get_user_name_by_id(chat_id, user_id):
    try:
        response = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": chat_id,
            "user_id": user_id
        })
        if response.status_code == 200:
            data = response.json().get("result", {})
            user = data.get("user", {})
            first_name = user.get("first_name", "")
            last_name = user.get("last_name", "")
            username = user.get("username", "")
            
            if username:
                return f"@{username}"
            elif first_name or last_name:
                return f"{first_name} {last_name}".strip()
            else:
                return f"کاربر {user_id}"
    except:
        pass
    return f"کاربر {user_id}"

def update_stats(chat_id, user_id, stat_type):
    global group_stats
    today = datetime.now().date().isoformat()
    if group_stats["last_reset"] != today:
        group_stats["today_messages"] = 0
        group_stats["last_reset"] = today

    if stat_type == "message":
        group_stats["total_messages"] += 1
        group_stats["today_messages"] += 1
        if user_id not in group_stats["active_users"]:
            group_stats["active_users"][user_id] = 0
        group_stats["active_users"][user_id] += 1
    elif stat_type == "spam":
        group_stats["spam_detected"] += 1
    elif stat_type == "warning":
        group_stats["warnings_issued"] += 1
    elif stat_type == "kick":
        group_stats["kicks_performed"] += 1
    elif stat_type == "alert":
        group_stats["security_alerts"] += 1

def add_security_log(event_type, user_id, details):
    log_entry = {
        "time": datetime.now().isoformat(),
        "type": event_type,
        "user_id": user_id,
        "details": details
    }
    security_log.append(log_entry)
    if len(security_log) > MAX_LOG_SIZE:
        security_log.pop(0)

def check_group_active(chat_id):
    return chat_id in active_groups

def send_activation_message(chat_id):
    msg = """
⚠️ **بات یاور در این گروه فعال نیست!**

برای فعالسازی بات، لطفاً مراحل زیر را انجام دهید:

1️⃣ مطمئن شوید بات ادمین گروه است
2️⃣ دستور زیر را ارسال کنید:
`فعالسازی`

📌 توجه: فقط ادمین‌های گروه می‌توانند بات را فعال کنند.
    """
    send_message_simple(chat_id, msg)

def send_support_message(user_id):
    msg = f"""
💝 **حمایت مالی از بات یاور**

اگر از بات یاور راضی هستید و می‌خواهید از توسعه‌دهنده حمایت کنید، می‌توانید از طریق لینک زیر اقدام کنید:

🔗 **لینک حمایت مالی:**
{SUPPORT_LINK}

💰 **مبالغ حمایت:**
• ۱۰,۰۰۰ تومان
• ۲۵,۰۰۰ تومان
• ۵۰,۰۰۰ تومان
• مبلغ دلخواه

❤️ حمایت شما باعث دلگرمی و ادامه توسعه بات می‌شود.

🙏 با تشکر از شما
    """
    send_message_simple(user_id, msg)

def send_ads_message(user_id):
    msg = f"""
📢 **تبلیغات و همکاری**

برای تبلیغات و همکاری با بات یاور، می‌توانید از طریق لینک زیر اقدام کنید:

🔗 **لینک ارتباط با ما:**
{ADS_LINK}

💼 **امکانات تبلیغاتی:**
• ارسال پیام همگانی
• تبلیغ در گروه‌های فعال
• استیکر اختصاصی
• پین شدن در بات

📞 برای همکاری و اطلاعات بیشتر با ما در ارتباط باشید.

🤝 منتظر همکاری شما هستیم
    """
    send_message_simple(user_id, msg)

def get_help_text():
    return """
🤖 **راهنمای کامل بات یاور**

📋 **دستورات عمومی:**
• سلام، خوبی، خداحافظ، چه خبر، بیا، دوس داری، باحالی
• قوانین - نمایش قوانین گروه
• تیکت [متن] - ارسال تیکت به ادمین
• آمار - نمایش آمار گروه
• امتیاز من - نمایش امتیاز و سطح شما
• امتیازها - نمایش برترین‌ها
• راهنما - دریافت این راهنما در پی وی
• بگو [متن] - تکرار متن بدون نوشته بگو

🎮 **بخش سرگرمی:**
• رپ - رپ اختصاصی یاور
• عشق - اس ام اس عاشقانه
• فال - فال حافظ
• انگیزه - پیام انگیزشی
• نقل قول - نقل قول از بزرگان
• معما - معمای جالب

🕌 **اوقات شرعی:**
• اوقات شرعی - نمایش اوقات شرعی تهران
• اوقات [شهر] - نمایش اوقات شرعی شهر مورد نظر

🎮 **بازی‌های گروهی (فقط ادمین):**
• بازی کلمات - شروع بازی حدس کلمه
• چیستان - شروع چیستان
• مافیا - شروع بازی مافیا (حداقل ۶ نفر)
• کلمات زنجیره‌ای - شروع بازی زنجیره کلمات
• مسابقه - شروع مسابقه دانش‌آموزی
• بازی عدد - شروع بازی حدس عدد
• اسم فامیل - شروع بازی اسم فامیل

🛡️ **مجازات کاربران (روی پیام ریپلای کن):**
• بن پالس [مدت] - بن موقت
• بن - بن دائمی
• اخطار [دلیل] - دادن اخطار
• سکوت [مدت] - سکوت موقت
• سکوت موفقیت - سکوت ۲۴ ساعته
• حذف سکوت - برداشتن سکوت
• اخطارها - نمایش اخطارها
• پاک کردن اخطار - پاک کردن اخطارها

🎯 **بخش کاربردی:**
• تاریخ - نمایش تاریخ امروز
• ساعت - نمایش ساعت فعلی
• فایل [متن] - ساخت فایل متنی
• ایکو [متن] - ساخت QR code
• اصل [متن] - تشخیص اصل یا کپی بودن متن
• اطلاعات [آیدی] - اطلاعات کاربر
• متن کامنت [متن] - ساخت متن فانتزی
• سیجاق [متن] - سیجاق کردن متن
• گزارش [کاربر] - گزارش کاربر به ادمین
• یاد دادن کلمه [کلمه] = [معنی] - ثبت کلمه جدید
• کلمه [کلمه] - معنی کلمه
• لیست ادمین ها - نمایش لیست ادمین‌ها

🔗 **بخش مدیریت گروه:**
• لینک دعوت - ساخت لینک دعوت گروه
• باطل لینک - باطل کردن لینک دعوت (فقط ادمین)

⚙️ **تنظیمات گروه (فقط ادمین):**
• تنظیم توضیحات [متن] - تنظیم توضیحات گروه
• تنظیم اسم [نام] - تغییر نام گروه
• قفل/باز کردن [مورد] - قفل کردن موارد مختلف
• قفل خودکار - فعال/غیرفعال
• قفل گروه - فعال/غیرفعال
• سختگیرانه - فعال/غیرفعال
• فیلتر لینک - فعال/غیرفعال
• خوشامدگویی - فعال/غیرفعال
• آنتی اسپم - فعال/غیرفعال
• سیستم امتیاز - فعال/غیرفعال
• مشاهده تنظیمات - نمایش همه تنظیمات
• لاگ امنیتی - نمایش لاگ
    """

def get_user_help_text():
    return """
🤖 **راهنمای سریع بات یاور**

📋 **دستورات پرکاربرد:**
• سلام، خوبی، خداحافظ، چه خبر
• قوانین - نمایش قوانین گروه
• تیکت [متن] - ارسال تیکت به ادمین
• آمار - نمایش آمار گروه
• راهنما - دریافت راهنمای کامل

🎮 **بخش سرگرمی:**
• رپ - رپ اختصاصی یاور
• عشق - اس ام اس عاشقانه
• فال - فال حافظ
• انگیزه - پیام انگیزشی
• نقل قول - نقل قول از بزرگان
• معما - معمای جالب

🕌 **اوقات شرعی:**
• اوقات شرعی - اوقات شرعی تهران
• اوقات [شهر] - اوقات شرعی شهر مورد نظر

🎯 **بخش کاربردی:**
• تاریخ - تاریخ امروز
• ساعت - ساعت فعلی
• فایل [متن] - ساخت فایل متنی
• ایکو [متن] - ساخت QR code
• کلمه [کلمه] - معنی کلمه

📌 برای اطلاعات بیشتر، دستور `راهنما کامل` را ارسال کنید.
    """

def get_game_help():
    return """
🎮 **راهنمای بازی‌ها**

**۱. بازی کلمات:**
• هدف: حدس زدن کلمه
• هر کاربر ۳ بار فرصت
• زمان: ۶۰ ثانیه
• جایزه: ۵۰ امتیاز + ۱۰ امتیاز سرعت

**۲. چیستان:**
• هدف: پاسخ به سوال
• اولین نفر برنده می‌شود
• جایزه: ۱۰-۳۰ امتیاز

**۳. مافیا:**
• نقش‌ها: مافیا، شهروند، دکتر، کارآگاه
• حداقل ۶ نفر نیاز است
• فاز شب و روز
• مافیاها باید شهروندان را بکشند

**۴. کلمات زنجیره‌ای:**
• هر کس باید کلمه‌ای بگوید که با حرف آخر کلمه قبلی شروع شود
• کلمات تکراری مجاز نیست
• زمان هر نوبت: ۳۰ ثانیه
• برنده آخرین نفری که کلمه می‌گوید

**۵. مسابقه دانش‌آموزی:**
• سوالات چهارگزینه‌ای
• زمان پاسخ: ۳۰ ثانیه
• امتیاز: ۱۰ برای پاسخ صحیح

**۶. بازی حدس عدد:**
• هدف: حدس زدن عدد تصادفی
• هر کاربر می‌تواند حدس خود را تغییر دهد
• نزدیک‌ترین حدس برنده می‌شود
• جایزه: ۵۰ امتیاز برای حدس دقیق، ۳۰ امتیاز برای نزدیک‌ترین

**۷. بازی اسم فامیل:**
• هدف: پر کردن دسته‌بندی‌ها با حرف مشخص
• هر پاسخ صحیح ۱۰ امتیاز دارد
• زمان: ۶۰ ثانیه
    """

# ======================
# توابع اوقات شرعی
# ======================
def get_prayer_times(city="tehran"):
    try:
        cities = {
            "تهران": "tehran", "مشهد": "mashhad", "اصفهان": "isfahan", "شیراز": "shiraz",
            "تبریز": "tabriz", "کرج": "karaj", "قم": "qom", "اهواز": "ahvaz",
            "رشت": "rasht", "کرمانشاه": "kermanshah", "زاهدان": "zahedan", "همدان": "hamadan",
            "یزد": "yazd", "اردبیل": "ardabil", "بندرعباس": "bandar-abbas", "خرم‌آباد": "khorramabad",
            "سنندج": "sanandaj", "گرگان": "gorgan", "ساری": "sari", "ارومیه": "urmia", "بوشهر": "bushehr",
        }

        city_code = cities.get(city, city)
        today = datetime.now().strftime("%Y-%m-%d")
        url = f"https://api.aladhan.com/v1/timingsByCity/{today}"
        params = {"city": city_code, "country": "Iran", "method": 8}

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            timings = data["data"]["timings"]
            date = data["data"]["date"]["readable"]

            prayer_text = f"""
🕌 **اوقات شرعی {city}**
📅 تاریخ: {date}

🌅 اذان صبح: {timings['Fajr']}
☀️ طلوع آفتاب: {timings['Sunrise']}
🕐 اذان ظهر: {timings['Dhuhr']}
🌆 غروب آفتاب: {timings['Sunset']}
🌃 اذان مغرب: {timings['Maghrib']}
🌙 اذان عشاء: {timings['Isha']}
🕛 نیمه شب شرعی: {timings['Midnight']}

📿 التماس دعا
            """
            return prayer_text
        else:
            return None

    except Exception as e:
        logger.error(f"خطا در دریافت اوقات شرعی: {e}")
        return None

# ======================
# توابع بخش سرگرمی و کاربردی
# ======================

def get_current_time():
    tz = pytz.timezone('Asia/Tehran')
    now = datetime.now(tz)
    return now.strftime("%H:%M:%S")

def get_current_date():
    tz = pytz.timezone('Asia/Tehran')
    now = datetime.now(tz)
    return now.strftime("%Y/%m/%d")

def create_text_file(text, filename="file.txt"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    except:
        return False

def get_fun_fact():
    return random.choice(fun_facts)

def create_qr_code(text):
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("qrcode.png")
        return True
    except Exception as e:
        logger.error(f"خطا در ساخت QR code: {e}")
        return False

def detect_original(text):
    if len(text) < 10:
        return "✅ این متن به نظر اصلی می‌رسد!"
    else:
        return "⚠️ این متن ممکن است کپی شده باشد (برای دقت بیشتر به منابع دیگر مراجعه کنید)"

def get_user_info_by_id(chat_id, user_id):
    try:
        response = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": chat_id,
            "user_id": user_id
        })
        if response.status_code == 200:
            data = response.json().get("result", {})
            if not data:
                return "❌ کاربری با این آیدی پیدا نشد!"

            user = data.get("user", {})
            status = data.get("status", "")

            status_fa = {
                "creator": "👑 مالک",
                "administrator": "👮 ادمین",
                "member": "👤 عضو",
                "restricted": "🔇 محدود شده",
                "left": "🚪 ترک کرده",
                "kicked": "⛔️ بن شده"
            }.get(status, status)

            info = f"👤 **اطلاعات کاربر**\n\n"
            info += f"🆔 آیدی: {user.get('id')}\n"
            info += f"📛 نام: {user.get('first_name', '')} {user.get('last_name', '')}\n"
            if user.get('username'):
                info += f"🔰 نام کاربری: @{user.get('username')}\n"
            info += f"📊 وضعیت: {status_fa}\n"

            if data.get("until_date"):
                until_date = datetime.fromtimestamp(data['until_date']).strftime('%Y-%m-%d %H:%M')
                info += f"⏰ تا تاریخ: {until_date}"

            return info
        else:
            return "❌ خطا در دریافت اطلاعات کاربر!"
    except Exception as e:
        logger.error(f"خطا در دریافت اطلاعات کاربر: {e}")
        return "❌ خطا در دریافت اطلاعات کاربر!"

def create_fancy_text(text):
    fancy_map = {
        'ا': 'آ', 'ب': 'ب', 'پ': 'پ', 'ت': 'ت', 'ث': 'ث',
        'ج': 'ج', 'چ': 'چ', 'ح': 'ح', 'خ': 'خ', 'د': 'د',
        'ذ': 'ذ', 'ر': 'ر', 'ز': 'ز', 'ژ': 'ژ', 'س': 'س',
        'ش': 'ش', 'ص': 'ص', 'ض': 'ض', 'ط': 'ط', 'ظ': 'ظ',
        'ع': 'ع', 'غ': 'غ', 'ف': 'ف', 'ق': 'ق', 'ک': 'ک',
        'گ': 'گ', 'ل': 'ل', 'م': 'م', 'ن': 'ن', 'و': 'و',
        'ه': 'ه', 'ی': 'ی'
    }

    fancy = ""
    for char in text:
        if char in fancy_map:
            fancy += fancy_map[char]
        else:
            fancy += char
    return f"✨ **متن فانتزی:**\n\n{fancy}"

def siag(text):
    words = text.split()
    if len(words) < 2:
        return text
    random.shuffle(words)
    return " ".join(words)

def report_user(chat_id, reporter_id, reported_id, reason):
    reporter_name = "کاربر"
    reported_name = "کاربر"
    try:
        reporter = requests.get(BASE_URL + "getChatMember", params={"chat_id": chat_id, "user_id": reporter_id})
        if reporter.status_code == 200:
            user_data = reporter.json().get("result", {}).get("user", {})
            if user_data:
                reporter_name = user_data.get('first_name', '') + ' ' + user_data.get('last_name', '')

        reported = requests.get(BASE_URL + "getChatMember", params={"chat_id": chat_id, "user_id": reported_id})
        if reported.status_code == 200:
            user_data = reported.json().get("result", {}).get("user", {})
            if user_data:
                reported_name = user_data.get('first_name', '') + ' ' + user_data.get('last_name', '')
    except:
        pass

    report_msg = f"🚨 **گزارش جدید**\n\n"
    report_msg += f"👤 گزارش‌دهنده: {reporter_name} (ID: {reporter_id})\n"
    report_msg += f"👥 کاربر گزارش شده: {reported_name} (ID: {reported_id})\n"
    report_msg += f"📝 دلیل: {reason}\n"
    report_msg += f"⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    sent = False
    try:
        admins = requests.get(BASE_URL + "getChatAdministrators", params={"chat_id": chat_id})
        if admins.status_code == 200:
            for admin in admins.json().get("result", []):
                admin_id = admin["user"]["id"]
                if admin_id != reporter_id:
                    send_message_simple(admin_id, report_msg)
                    sent = True
    except:
        pass
    return sent

def learn_word(word, meaning):
    word_database[word] = meaning
    return f"✅ کلمه '{word}' با معنی '{meaning}' ثبت شد!"

def get_word_meaning(word):
    if word in word_database:
        return f"📖 **معنی کلمه {word}:**\n\n{word_database[word]}"
    else:
        return f"❌ کلمه '{word}' در دیتابیس وجود ندارد. می‌توانید با دستور `یاد دادن کلمه {word} = [معنی]` آن را ثبت کنید."

def set_group_description(chat_id, description):
    try:
        response = requests.post(BASE_URL + "setChatDescription", json={
            "chat_id": chat_id,
            "description": description
        })
        if response.status_code == 200:
            return "✅ توضیحات گروه با موفقیت تنظیم شد!"
        else:
            return "❌ خطا در تنظیم توضیحات! (بات ادمین نیست)"
    except Exception as e:
        logger.error(f"خطا در تنظیم توضیحات: {e}")
        return "❌ خطا در تنظیم توضیحات!"

def set_group_name(chat_id, name):
    try:
        response = requests.post(BASE_URL + "setChatTitle", json={
            "chat_id": chat_id,
            "title": name
        })
        if response.status_code == 200:
            return f"✅ نام گروه به '{name}' تغییر یافت!"
        else:
            return "❌ خطا در تغییر نام! (بات ادمین نیست)"
    except Exception as e:
        logger.error(f"خطا در تغییر نام: {e}")
        return "❌ خطا در تغییر نام!"

def get_admins_list(chat_id):
    try:
        response = requests.get(BASE_URL + "getChatAdministrators", params={"chat_id": chat_id})
        if response.status_code == 200:
            admins = response.json().get("result", [])
            if not admins:
                return "👮 هیچ ادمینی در گروه وجود ندارد!"

            admin_list = "👮 **لیست ادمین‌ها**\n\n"
            for i, admin in enumerate(admins, 1):
                user = admin["user"]
                status = "👑 مالک" if admin["status"] == "creator" else "👮 ادمین"

                full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                if not full_name:
                    full_name = "بدون نام"

                admin_list += f"{i}. {full_name}\n"
                admin_list += f"   🆔 آیدی: {user['id']}\n"
                if user.get('username'):
                    admin_list += f"   🔰 یوزرنیم: @{user['username']}\n"
                admin_list += f"   📊 {status}\n\n"

            return admin_list
        else:
            return "❌ خطا در دریافت لیست ادمین‌ها!"
    except Exception as e:
        logger.error(f"خطا در دریافت لیست ادمین‌ها: {e}")
        return "❌ خطا در دریافت لیست ادمین‌ها!"

# ======================
# توابع بازی حدس عدد
# ======================
def start_number_game(chat_id, min_num=0, max_num=100):
    number_game["active"] = True
    number_game["number"] = random.randint(min_num, max_num)
    number_game["min"] = min_num
    number_game["max"] = max_num
    number_game["players"] = {}
    number_game["guesses"] = {}
    number_game["start_time"] = time.time()
    number_game["end_time"] = time.time() + 120
    number_game["chat_id"] = chat_id
    
    send_message_simple(chat_id, f"🎲 **بازی حدس عدد شروع شد!**\n\n🔢 محدوده: {min_num} تا {max_num}\n⏱️ زمان: ۲ دقیقه\n\n💡 هر کسی نزدیک‌ترین عدد رو حدس بزنه برنده میشه!\n🔢 عدد خود را ارسال کنید:")
    
    def timer():
        time.sleep(120)
        if number_game["active"]:
            end_number_game(number_game["chat_id"])
    
    threading.Thread(target=timer, daemon=True).start()
    return True

def check_number_guess(chat_id, user_id, user_name, text, message_id):
    if not number_game["active"]:
        return False
    
    try:
        guess = int(text)
        if guess < number_game["min"] or guess > number_game["max"]:
            send_message_simple(chat_id, f"⚠️ {user_name} عدد باید بین {number_game['min']} تا {number_game['max']} باشه!")
            return False
        
        if user_id not in number_game["players"]:
            number_game["players"][user_id] = user_name
            number_game["guesses"][user_id] = guess
            send_message_simple(chat_id, f"✅ {user_name} عدد {guess} رو حدس زد!")
        else:
            number_game["guesses"][user_id] = guess
            send_message_simple(chat_id, f"🔄 {user_name} حدس خود رو به {guess} تغییر داد!")
        
        if guess == number_game["number"]:
            number_game["active"] = False
            send_message_simple(chat_id, f"🎉 **برنده: {user_name}** 🎉\n\n✅ عدد دقیق {number_game['number']} رو حدس زدید!\n🏆 جایزه: ۵۰ امتیاز")
            add_score(chat_id, user_id, 50, "برنده بازی حدس عدد")
            return True
        
        return False
        
    except ValueError:
        return False

def end_number_game(chat_id):
    if not number_game["active"]:
        return
    
    number_game["active"] = False
    
    if not number_game["guesses"]:
        send_message_simple(chat_id, f"⏰ زمان بازی تموم شد!\n\nعدد درست: {number_game['number']}\n\nهیچکس شرکت نکرد!")
        return
    
    target = number_game["number"]
    closest_user = None
    closest_diff = float('inf')
    
    for user_id, guess in number_game["guesses"].items():
        diff = abs(guess - target)
        if diff < closest_diff:
            closest_diff = diff
            closest_user = user_id
    
    if closest_user:
        winner_name = number_game["players"][closest_user]
        winner_guess = number_game["guesses"][closest_user]
        
        msg = f"⏰ **زمان بازی تموم شد!**\n\n"
        msg += f"🔢 عدد درست: {target}\n"
        msg += f"🏆 **برنده: {winner_name}**\n"
        msg += f"📊 حدس شما: {winner_guess} (فاصله: {closest_diff})\n"
        msg += f"💎 جایزه: ۳۰ امتیاز"
        
        send_message_simple(chat_id, msg)
        add_score(chat_id, closest_user, 30, "نزدیک‌ترین حدس در بازی عدد")
    
    if number_game["guesses"]:
        msg = "\n📋 **لیست حدس‌ها:**\n"
        for user_id, guess in number_game["guesses"].items():
            player_name = number_game["players"][user_id]
            diff = abs(guess - target)
            msg += f"• {player_name}: {guess} (فاصله: {diff})\n"
        send_message_simple(chat_id, msg)

# ======================
# توابع بازی اسم فامیل
# ======================
def start_name_family(chat_id):
    letters = "ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"
    letter = random.choice(letters)
    
    name_family_game["active"] = True
    name_family_game["letter"] = letter
    name_family_game["answers"] = {}
    name_family_game["players"] = set()
    name_family_game["start_time"] = time.time()
    
    categories_text = "، ".join(name_family_game["categories"])
    
    msg = f"📚 **بازی اسم فامیل شروع شد!**\n\n"
    msg += f"🔤 حرف: **{letter}**\n"
    msg += f"📋 دسته‌بندی‌ها:\n{categories_text}\n\n"
    msg += f"⏱️ زمان: {name_family_game['time_limit']} ثانیه\n"
    msg += f"💡 هر کدوم از دسته‌ها رو با حرف {letter} بنویسید:\n"
    msg += f"مثال: اسم: علی، فامیل: محمدی، شهر: اصفهان، ...\n\n"
    msg += f"✅ برای ثبت پاسخ ها، هر خط یک دسته رو بنویسید:\n"
    msg += f"`اسم: علی`\n`فامیل: محمدی`\n`شهر: اصفهان`"
    
    send_message_simple(chat_id, msg)
    
    def end_game_timer():
        time.sleep(name_family_game["time_limit"])
        if name_family_game["active"]:
            end_name_family_game(chat_id)
    
    timer_thread = threading.Thread(target=end_game_timer, daemon=True)
    timer_thread.start()

def check_name_family_answer(chat_id, user_id, user_name, text, message_id):
    if not name_family_game["active"]:
        return False
    
    if ":" not in text:
        return False
    
    parts = text.split(":", 1)
    if len(parts) != 2:
        return False
    
    category = parts[0].strip()
    answer = parts[1].strip()
    
    if category not in name_family_game["categories"]:
        send_message_simple(chat_id, f"⚠️ {user_name} دسته '{category}' معتبر نیست!")
        return False
    
    if not answer.startswith(name_family_game["letter"]):
        send_message_simple(chat_id, f"⚠️ {user_name} پاسخ باید با حرف '{name_family_game['letter']}' شروع بشه!")
        return False
    
    name_family_game["players"].add(user_id)
    
    if user_id not in name_family_game["answers"]:
        name_family_game["answers"][user_id] = {"name": user_name, "answers": {}}
    
    if category in name_family_game["answers"][user_id]["answers"]:
        send_message_simple(chat_id, f"⚠️ {user_name} قبلاً برای دسته '{category}' پاسخ دادید!")
        return False
    
    name_family_game["answers"][user_id]["answers"][category] = answer
    send_message_simple(chat_id, f"✅ {user_name} - {category}: {answer} ثبت شد!")
    return True

def end_name_family_game(chat_id):
    if not name_family_game["active"]:
        return
    
    name_family_game["active"] = False
    letter = name_family_game["letter"]
    answers = name_family_game["answers"]
    
    if not answers:
        send_message_simple(chat_id, f"⏰ زمان بازی تموم شد!\n\nهیچکس شرکت نکرد!")
        return
    
    scores = {}
    for user_id, data in answers.items():
        user_name = data["name"]
        user_answers = data["answers"]
        score = len(user_answers) * 10
        scores[user_id] = score
        add_score(chat_id, user_id, score, f"بازی اسم فامیل - حرف {letter}")
    
    msg = f"📊 **نتایج بازی اسم فامیل**\n"
    msg += f"🔤 حرف: {letter}\n\n"
    
    for user_id, data in answers.items():
        user_name = data["name"]
        user_answers = data["answers"]
        score = len(user_answers) * 10
        msg += f"👤 {user_name}: {score} امتیاز\n"
        for cat, ans in user_answers.items():
            msg += f"   • {cat}: {ans}\n"
        msg += "\n"
    
    send_message_simple(chat_id, msg)

# ======================
# توابع لینک دعوت
# ======================
def get_group_invite_link(chat_id, user_id, user_name):
    if not is_admin(chat_id, user_id):
        send_message_simple(chat_id, "❌ فقط ادمین‌ها می‌توانند لینک دعوت بسازند!")
        return
    
    try:
        response = requests.post(BASE_URL + "createChatInviteLink", json={
            "chat_id": chat_id,
            "member_limit": 50,
            "expire_date": int(time.time()) + 86400
        })
        
        if response.status_code == 200:
            data = response.json()
            invite_link = data.get("result", {}).get("invite_link")
            
            if invite_link:
                msg = f"🔗 **لینک دعوت گروه**\n\n"
                msg += f"📎 {invite_link}\n\n"
                msg += f"⏰ اعتبار: ۲۴ ساعت\n"
                msg += f"👥 حداکثر عضو: ۵۰ نفر\n"
                msg += f"👤 ساخته شده توسط: {user_name}\n\n"
                msg += f"💡 می‌توانید این لینک را با دیگران به اشتراک بگذارید."
                
                send_message_simple(chat_id, msg)
            else:
                send_message_simple(chat_id, "❌ خطا در ساخت لینک دعوت!")
        else:
            send_message_simple(chat_id, "❌ خطا! مطمئن شوید بات ادمین گروه است.")
            
    except Exception as e:
        logger.error(f"خطا در ساخت لینک دعوت: {e}")
        send_message_simple(chat_id, "❌ خطا در ساخت لینک دعوت!")

def revoke_invite_link(chat_id, user_id):
    if not is_admin(chat_id, user_id):
        send_message_simple(chat_id, "❌ فقط ادمین‌ها می‌توانند لینک را باطل کنند!")
        return
    
    try:
        response = requests.post(BASE_URL + "revokeChatInviteLink", json={
            "chat_id": chat_id
        })
        
        if response.status_code == 200:
            data = response.json()
            new_link = data.get("result", {}).get("invite_link")
            send_message_simple(chat_id, f"✅ لینک دعوت قبلی باطل شد!\n\n🔗 لینک جدید: {new_link}")
        else:
            send_message_simple(chat_id, "❌ خطا در باطل کردن لینک!")
    except:
        send_message_simple(chat_id, "❌ خطا در باطل کردن لینک!")

# ======================
# توابع ارسال همگانی با قابلیت عکس و فیلم
# ======================

def send_with_keyboard(chat_id, text, buttons):
    try:
        keyboard = {
            "keyboard": buttons,
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": json.dumps(keyboard)
        }
        requests.post(BASE_URL + "sendMessage", json=payload, timeout=5)
    except Exception as e:
        logger.error(f"خطا در ارسال کیبورد: {e}")

def remove_keyboard(chat_id, text):
    try:
        keyboard = {"remove_keyboard": True}
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": json.dumps(keyboard)
        }
        requests.post(BASE_URL + "sendMessage", json=payload, timeout=5)
    except Exception as e:
        logger.error(f"خطا در حذف کیبورد: {e}")

def send_message_simple(chat_id, text):
    try:
        payload = {"chat_id": chat_id, "text": text}
        requests.post(BASE_URL + "sendMessage", json=payload, timeout=3)
        return True
    except Exception as e:
        return False

def send_photo(chat_id, photo_path, caption=""):
    try:
        with open(photo_path, 'rb') as f:
            files = {'photo': f}
            data = {'chat_id': chat_id, 'caption': caption}
            response = requests.post(BASE_URL + 'sendPhoto', data=data, files=files, timeout=30)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"خطا در ارسال عکس: {e}")
        return False

def send_video(chat_id, video_path, caption=""):
    try:
        with open(video_path, 'rb') as f:
            files = {'video': f}
            data = {'chat_id': chat_id, 'caption': caption}
            response = requests.post(BASE_URL + 'sendVideo', data=data, files=files, timeout=30)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"خطا در ارسال فیلم: {e}")
        return False

def send_document(chat_id, document_path, caption=""):
    try:
        with open(document_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': chat_id, 'caption': caption}
            response = requests.post(BASE_URL + 'sendDocument', data=data, files=files, timeout=30)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"خطا در ارسال فایل: {e}")
        return False

def delete_message(chat_id, message_id):
    try:
        url = BASE_URL + "deleteMessage"
        payload = {"chat_id": chat_id, "message_id": message_id}
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except:
        return False

def ban_user(chat_id, user_id, permanent=True, duration=None):
    try:
        if permanent:
            response = requests.post(BASE_URL + "banChatMember", json={
                "chat_id": chat_id,
                "user_id": user_id
            })
            if response.status_code == 200:
                return True, "دائمی"
            return False, None
        else:
            until_date = int(time.time() + duration)
            response = requests.post(BASE_URL + "banChatMember", json={
                "chat_id": chat_id,
                "user_id": user_id,
                "until_date": until_date
            })
            if response.status_code == 200:
                return True, f"{duration} ثانیه"
            return False, None
    except Exception as e:
        logger.error(f"خطا در بن کاربر: {e}")
        return False, None

def restrict_user(chat_id, user_id, duration):
    try:
        until_date = int(time.time() + duration)
        payload = {
            "chat_id": chat_id,
            "user_id": user_id,
            "permissions": {
                "can_send_messages": False,
                "can_send_media_messages": False,
                "can_send_polls": False,
                "can_send_other_messages": False,
                "can_add_web_page_previews": False,
                "can_change_info": False,
                "can_invite_users": False,
                "can_pin_messages": False
            },
            "until_date": until_date
        }
        response = requests.post(BASE_URL + "restrictChatMember", json=payload)
        return response.status_code == 200
    except:
        return False

def unrestrict_user(chat_id, user_id):
    try:
        payload = {
            "chat_id": chat_id,
            "user_id": user_id,
            "permissions": {
                "can_send_messages": True,
                "can_send_media_messages": True,
                "can_send_polls": True,
                "can_send_other_messages": True,
                "can_add_web_page_previews": True,
                "can_change_info": False,
                "can_invite_users": True,
                "can_pin_messages": False
            }
        }
        response = requests.post(BASE_URL + "restrictChatMember", json=payload)
        return response.status_code == 200
    except:
        return False

def update_groups(chat_id, chat_type, chat_title=None):
    global all_groups, group_names
    if chat_type in ["group", "supergroup"]:
        all_groups.add(chat_id)
        if chat_title:
            group_names[chat_id] = chat_title
        else:
            group_names[chat_id] = f"گروه {chat_id}"

def update_contacts(user_id, user_name=None):
    global user_contacts
    if user_id not in user_contacts:
        user_contacts[user_id] = {
            "name": user_name or f"کاربر {user_id}",
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
    else:
        user_contacts[user_id]["last_seen"] = datetime.now().isoformat()
        if user_name:
            user_contacts[user_id]["name"] = user_name

def show_main_menu(user_id):
    menu_text = f"""
👋 **خوش آمدید ادمین بازو!**

📊 **آمار فعلی:**
• تعداد مخاطبین: {len(user_contacts)}
• تعداد گروه‌ها: {len(all_groups)}

لطفاً یکی از گزینه‌ها را انتخاب کنید:
    """

    buttons = [
        ["📢 ارسال همگانی", "📊 آمار همگانی"],
        ["👥 لیست مخاطبین", "👥 لیست گروه‌ها"],
        ["🚪 لفت از گروه", "⚙️ تنظیمات"],
        ["❓ راهنما", "🔙 خروج"]
    ]

    send_with_keyboard(user_id, menu_text, buttons)

def show_user_menu(user_id):
    menu_text = f"""
👋 **به بات یاور خوش آمدید!**

🤖 **بات یاور** یک ربات مدیریت گروه با امکانات کامل است.

📌 **دستورات سریع:**
• `راهنما` - مشاهده راهنمای کامل
• `آمار` - نمایش آمار گروه
• `قوانین` - نمایش قوانین
• `تیکت [متن]` - ارسال تیکت به ادمین

🎮 **بخش سرگرمی:**
• `رپ` - رپ اختصاصی
• `عشق` - اس ام اس عاشقانه
• `فال` - فال حافظ
• `انگیزه` - پیام انگیزشی

💝 **حمایت از ما:**
اگر از بات یاور راضی هستید، می‌توانید از ما حمایت کنید.

📢 **تبلیغات:**
برای همکاری و تبلیغات با ما در ارتباط باشید.

لطفاً گزینه مورد نظر را انتخاب کنید:
    """

    buttons = [
        ["📖 راهنما", "💝 حمایت مالی"],
        ["📢 تبلیغات", "🔙 خروج"]
    ]

    send_with_keyboard(user_id, menu_text, buttons)

def show_broadcast_menu(user_id):
    menu_text = f"""
📢 **منوی ارسال همگانی**

لطفاً نوع ارسال را انتخاب کنید:

👤 تعداد مخاطبین: {len(user_contacts)}
👥 تعداد گروه‌ها: {len(all_groups)}

📎 **نوع محتوا:**
• متن ساده
• عکس
• فیلم
• فایل
    """

    buttons = [
        ["👤 ارسال به مخاطبین", "👥 ارسال به گروه‌ها"],
        ["📷 ارسال عکس", "🎬 ارسال فیلم", "📄 ارسال فایل"],
        ["📊 آمار ارسال‌ها", "🔙 بازگشت به منوی اصلی"]
    ]

    send_with_keyboard(user_id, menu_text, buttons)

def show_broadcast_confirmation(user_id, broadcast_type, message, media_type=None, media_path=None):
    target_count = len(user_contacts) if broadcast_type == "contacts" else len(all_groups)

    if media_type and media_path:
        media_names = {"photo": "عکس", "video": "فیلم", "document": "فایل"}
        media_name = media_names.get(media_type, "رسانه")
        confirm_text = f"""
📋 **تأیید ارسال همگانی**

نوع: {'مخاطبین' if broadcast_type == 'contacts' else 'گروه‌ها'}
نوع رسانه: {media_name}
تعداد گیرندگان: {target_count}
کپشن: {message if message else 'بدون کپشن'}

آیا مطمئن هستید؟
    """
    else:
        confirm_text = f"""
📋 **تأیید ارسال همگانی**

نوع: {'مخاطبین' if broadcast_type == 'contacts' else 'گروه‌ها'}
تعداد گیرندگان: {target_count}
متن پیام:
------------------------
{message}
------------------------

آیا مطمئن هستید؟
    """

    buttons = [
        ["✅ بله، ارسال کن", "❌ خیر، لغو کن"]
    ]

    send_with_keyboard(user_id, confirm_text, buttons)

def handle_broadcast_selection(user_id, text):
    global broadcast_status
    
    if text == "👤 ارسال به مخاطبین":
        broadcast_status[user_id] = {"type": "contacts", "step": "waiting_for_message", "media_type": "text"}
        remove_keyboard(user_id, "📝 لطفاً متن پیام همگانی را ارسال کنید:")
        return True
    
    elif text == "👥 ارسال به گروه‌ها":
        broadcast_status[user_id] = {"type": "groups", "step": "waiting_for_message", "media_type": "text"}
        remove_keyboard(user_id, "📝 لطفاً متن پیام همگانی را ارسال کنید:")
        return True
    
    elif text == "📷 ارسال عکس":
        broadcast_status[user_id] = {"step": "waiting_for_photo", "media_type": "photo"}
        remove_keyboard(user_id, "📸 لطفاً عکس مورد نظر را ارسال کنید:")
        return True
    
    elif text == "🎬 ارسال فیلم":
        broadcast_status[user_id] = {"step": "waiting_for_video", "media_type": "video"}
        remove_keyboard(user_id, "🎬 لطفاً فیلم مورد نظر را ارسال کنید:")
        return True
    
    elif text == "📄 ارسال فایل":
        broadcast_status[user_id] = {"step": "waiting_for_document", "media_type": "document"}
        remove_keyboard(user_id, "📄 لطفاً فایل مورد نظر را ارسال کنید:")
        return True
    
    elif text == "📊 آمار ارسال‌ها":
        stats = get_broadcast_stats()
        send_message_simple(user_id, stats)
        show_broadcast_menu(user_id)
        return True
    
    elif text == "🔙 بازگشت به منوی اصلی":
        if user_id in broadcast_status:
            del broadcast_status[user_id]
        show_main_menu(user_id)
        return True
    
    return False

def handle_broadcast_media(user_id, message):
    global broadcast_status
    
    if user_id not in broadcast_status:
        return False
    
    status = broadcast_status[user_id]
    
    if status.get("step") == "waiting_for_photo" and message.get("photo"):
        file_id = message["photo"][-1]["file_id"]
        file_path = f"broadcast_photo_{int(time.time())}.jpg"
        
        try:
            file_info = requests.get(BASE_URL + "getFile", params={"file_id": file_id})
            if file_info.status_code == 200:
                file_data = file_info.json()
                file_url = f"https://tapi.bale.ai/file/bot{BOT_TOKEN}/{file_data['result']['file_path']}"
                response = requests.get(file_url)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    status["media_path"] = file_path
                    status["step"] = "waiting_for_caption"
                    send_message_simple(user_id, "📝 لطفاً کپشن عکس را ارسال کنید (یا 'بدون کپشن'):")
                    return True
        except Exception as e:
            logger.error(f"خطا در دریافت عکس: {e}")
            send_message_simple(user_id, "❌ خطا در دریافت عکس!")
            del broadcast_status[user_id]
            show_broadcast_menu(user_id)
        return True
    
    elif status.get("step") == "waiting_for_video" and message.get("video"):
        file_id = message["video"]["file_id"]
        file_path = f"broadcast_video_{int(time.time())}.mp4"
        
        try:
            file_info = requests.get(BASE_URL + "getFile", params={"file_id": file_id})
            if file_info.status_code == 200:
                file_data = file_info.json()
                file_url = f"https://tapi.bale.ai/file/bot{BOT_TOKEN}/{file_data['result']['file_path']}"
                response = requests.get(file_url)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    status["media_path"] = file_path
                    status["step"] = "waiting_for_caption"
                    send_message_simple(user_id, "📝 لطفاً کپشن فیلم را ارسال کنید (یا 'بدون کپشن'):")
                    return True
        except Exception as e:
            logger.error(f"خطا در دریافت فیلم: {e}")
            send_message_simple(user_id, "❌ خطا در دریافت فیلم!")
            del broadcast_status[user_id]
            show_broadcast_menu(user_id)
        return True
    
    elif status.get("step") == "waiting_for_document" and message.get("document"):
        file_id = message["document"]["file_id"]
        file_name = message["document"].get("file_name", f"broadcast_file_{int(time.time())}")
        file_path = f"broadcast_{int(time.time())}_{file_name}"
        
        try:
            file_info = requests.get(BASE_URL + "getFile", params={"file_id": file_id})
            if file_info.status_code == 200:
                file_data = file_info.json()
                file_url = f"https://tapi.bale.ai/file/bot{BOT_TOKEN}/{file_data['result']['file_path']}"
                response = requests.get(file_url)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    status["media_path"] = file_path
                    status["step"] = "waiting_for_caption"
                    send_message_simple(user_id, "📝 لطفاً کپشن فایل را ارسال کنید (یا 'بدون کپشن'):")
                    return True
        except Exception as e:
            logger.error(f"خطا در دریافت فایل: {e}")
            send_message_simple(user_id, "❌ خطا در دریافت فایل!")
            del broadcast_status[user_id]
            show_broadcast_menu(user_id)
        return True
    
    elif status.get("step") == "waiting_for_caption":
        caption_text = message.get("text", "")
        if caption_text:
            caption = caption_text if caption_text != "بدون کپشن" else ""
        else:
            caption = ""
        status["message"] = caption
        status["step"] = "waiting_for_confirmation"
        
        broadcast_type = status.get("type", "contacts")
        media_type = status.get("media_type")
        media_path = status.get("media_path")
        
        show_broadcast_confirmation(user_id, broadcast_type, caption, media_type, media_path)
        return True
    
    return False

def handle_broadcast_message(user_id, text):
    global broadcast_status

    if user_id not in broadcast_status:
        return False

    status = broadcast_status[user_id]

    if status.get("step") == "waiting_for_message":
        broadcast_type = status.get("type")
        status["message"] = text
        status["step"] = "waiting_for_confirmation"
        show_broadcast_confirmation(user_id, broadcast_type, text)
        return True

    elif status.get("step") == "waiting_for_confirmation":
        if text == "✅ بله، ارسال کن":
            broadcast_type = status.get("type")
            message_text = status.get("message")
            media_type = status.get("media_type", "text")
            media_path = status.get("media_path")

            if user_id in broadcast_status:
                del broadcast_status[user_id]

            send_message_simple(user_id, f"📨 در حال ارسال به {'مخاطبین' if broadcast_type == 'contacts' else 'گروه‌ها'}...")

            def broadcast_worker():
                try:
                    if media_type == "text":
                        if broadcast_type == "contacts":
                            success, fail = broadcast_to_contacts(message_text, user_id)
                        else:
                            success, fail = broadcast_to_groups(message_text, user_id)
                    else:
                        if broadcast_type == "contacts":
                            success, fail = broadcast_media_to_contacts(media_type, media_path, message_text, user_id)
                        else:
                            success, fail = broadcast_media_to_groups(media_type, media_path, message_text, user_id)
                        
                        try:
                            if media_path and os.path.exists(media_path):
                                os.remove(media_path)
                        except:
                            pass

                    result_msg = f"✅ ارسال {'همگانی' if broadcast_type == 'contacts' else 'به گروه‌ها'} کامل شد!\nموفق: {success}\nناموفق: {fail}"
                    send_message_simple(user_id, result_msg)

                except Exception as e:
                    logger.error(f"❌ خطا در ارسال: {e}")
                    send_message_simple(user_id, f"❌ خطا در ارسال: {e}")

                finally:
                    time.sleep(1)
                    show_main_menu(user_id)

            thread = threading.Thread(target=broadcast_worker, daemon=True)
            thread.start()

            return True

        elif text == "❌ خیر، لغو کن":
            send_message_simple(user_id, "❌ ارسال همگانی لغو شد.")
            if user_id in broadcast_status:
                del broadcast_status[user_id]
            show_broadcast_menu(user_id)
            return True

    return False

def broadcast_to_contacts(message, sender_id):
    success_count = 0
    fail_count = 0

    for user_id in list(user_contacts.keys()):
        if user_id != sender_id:
            try:
                if send_message_simple(user_id, f"📢 **پیام همگانی**\n\n{message}"):
                    success_count += 1
                else:
                    fail_count += 1
                time.sleep(0.1)
            except:
                fail_count += 1

    broadcast_stats["total_broadcasts"] += 1
    broadcast_stats["total_messages_sent"] += success_count
    broadcast_stats["last_broadcast"] = datetime.now().isoformat()

    return success_count, fail_count

def broadcast_to_groups(message, sender_id):
    success_count = 0
    fail_count = 0

    for group_id in list(all_groups):
        try:
            if send_message_simple(group_id, f"📢 **پیام همگانی**\n\n{message}"):
                success_count += 1
            else:
                fail_count += 1
            time.sleep(0.2)
        except:
            fail_count += 1

    broadcast_stats["total_broadcasts"] += 1
    broadcast_stats["total_messages_sent"] += success_count
    broadcast_stats["last_broadcast"] = datetime.now().isoformat()

    return success_count, fail_count

def send_broadcast_media(chat_id, media_type, media_path, caption=""):
    try:
        if media_type == "photo":
            with open(media_path, 'rb') as f:
                files = {'photo': f}
                data = {'chat_id': chat_id, 'caption': caption}
                response = requests.post(BASE_URL + 'sendPhoto', data=data, files=files, timeout=30)
        elif media_type == "video":
            with open(media_path, 'rb') as f:
                files = {'video': f}
                data = {'chat_id': chat_id, 'caption': caption}
                response = requests.post(BASE_URL + 'sendVideo', data=data, files=files, timeout=30)
        elif media_type == "document":
            with open(media_path, 'rb') as f:
                files = {'document': f}
                data = {'chat_id': chat_id, 'caption': caption}
                response = requests.post(BASE_URL + 'sendDocument', data=data, files=files, timeout=30)
        else:
            return False
        return response.status_code == 200
    except Exception as e:
        logger.error(f"خطا در ارسال رسانه: {e}")
        return False

def broadcast_media_to_contacts(media_type, media_path, caption, sender_id):
    success_count = 0
    fail_count = 0

    for user_id in list(user_contacts.keys()):
        if user_id != sender_id:
            try:
                if send_broadcast_media(user_id, media_type, media_path, caption):
                    success_count += 1
                else:
                    fail_count += 1
                time.sleep(0.1)
            except:
                fail_count += 1

    broadcast_stats["total_broadcasts"] += 1
    broadcast_stats["total_messages_sent"] += success_count
    broadcast_stats["last_broadcast"] = datetime.now().isoformat()

    return success_count, fail_count

def broadcast_media_to_groups(media_type, media_path, caption, sender_id):
    success_count = 0
    fail_count = 0

    for group_id in list(all_groups):
        try:
            if send_broadcast_media(group_id, media_type, media_path, caption):
                success_count += 1
            else:
                fail_count += 1
            time.sleep(0.2)
        except:
            fail_count += 1

    broadcast_stats["total_broadcasts"] += 1
    broadcast_stats["total_messages_sent"] += success_count
    broadcast_stats["last_broadcast"] = datetime.now().isoformat()

    return success_count, fail_count

def get_broadcast_stats():
    stats = "📊 **آمار ارسال همگانی**\n\n"
    stats += f"📨 تعداد کل ارسال‌ها: {broadcast_stats['total_broadcasts']}\n"
    stats += f"📬 مجموع پیام‌های ارسال شده: {broadcast_stats['total_messages_sent']}\n"

    if broadcast_stats['last_broadcast']:
        stats += f"⏰ آخرین ارسال: {broadcast_stats['last_broadcast'][:16]}\n"

    stats += f"\n👥 تعداد مخاطبین: {len(user_contacts)}\n"
    stats += f"👥 تعداد گروه‌ها: {len(all_groups)}"

    return stats

def show_contacts(user_id):
    if not user_contacts:
        send_message_simple(user_id, "📭 هیچ مخاطبی یافت نشد.")
        show_main_menu(user_id)
        return

    contacts_list = "👥 **لیست مخاطبین**\n\n"
    for i, (uid, data) in enumerate(list(user_contacts.items())[:20], 1):
        contacts_list += f"{i}. {data.get('name', f'کاربر {uid}')}\n"
        contacts_list += f"   🆔 آیدی: {uid}\n"
        contacts_list += f"   🕐 اولین حضور: {data['first_seen'][:16]}\n"
        contacts_list += f"   🕐 آخرین حضور: {data['last_seen'][:16]}\n\n"

    if len(user_contacts) > 20:
        contacts_list += f"... و {len(user_contacts) - 20} کاربر دیگر"

    send_message_simple(user_id, contacts_list)
    show_main_menu(user_id)

def show_groups(user_id):
    if not all_groups:
        send_message_simple(user_id, "📭 هیچ گروهی یافت نشد.")
        show_main_menu(user_id)
        return

    groups_list = "👥 **لیست گروه‌ها**\n\n"
    groups_list += f"تعداد کل گروه‌ها: {len(all_groups)}\n\n"

    for i, gid in enumerate(list(all_groups)[:20], 1):
        group_name = group_names.get(gid, f"گروه {gid}")
        groups_list += f"{i}. {group_name}\n"
        groups_list += f"   🆔 آیدی گروه: {gid}\n\n"

    if len(all_groups) > 20:
        groups_list += f"... و {len(all_groups) - 20} گروه دیگر"

    send_message_simple(user_id, groups_list)
    show_main_menu(user_id)

def leave_group_by_name(admin_id, group_name):
    found = []
    for gid, gname in group_names.items():
        if group_name.lower() in gname.lower():
            found.append((gid, gname))
    if not found:
        send_message_simple(admin_id, f"❌ گروهی با نام «{group_name}» پیدا نشد.")
        return
    if len(found) == 1:
        gid, gname = found[0]
        try:
            r = requests.post(BASE_URL + "leaveChat", json={"chat_id": gid})
            if r.status_code == 200:
                all_groups.discard(gid)
                if gid in group_names:
                    del group_names[gid]
                if gid in active_groups:
                    active_groups.discard(gid)
                send_message_simple(admin_id, f"✅ از گروه «{gname}» خارج شدم.")
            else:
                send_message_simple(admin_id, f"❌ خطا در خروج از گروه!")
        except Exception as e:
            send_message_simple(admin_id, f"❌ خطا: {e}")
    else:
        res = f"🔍 چند گروه با نام «{group_name}» پیدا شد:\n\n"
        for i, (gid, gname) in enumerate(found[:10], 1):
            res += f"{i}. {gname}\n   آیدی: {gid}\n\n"
        res += "برای خروج دقیق: `لفت با آیدی [آیدی]`"
        send_message_simple(admin_id, res)

def leave_group_by_id(admin_id, group_id):
    try:
        gid = int(group_id)
        if gid not in all_groups:
            send_message_simple(admin_id, f"❌ گروه با آیدی {gid} در لیست نیست.")
            return
        gname = group_names.get(gid, f"گروه {gid}")
        r = requests.post(BASE_URL + "leaveChat", json={"chat_id": gid})
        if r.status_code == 200:
            all_groups.discard(gid)
            if gid in group_names:
                del group_names[gid]
            if gid in active_groups:
                active_groups.discard(gid)
            send_message_simple(admin_id, f"✅ از گروه «{gname}» خارج شدم.")
        else:
            send_message_simple(admin_id, f"❌ خطا در خروج!")
    except:
        send_message_simple(admin_id, "❌ آیدی نامعتبر!")

def get_updates(offset=None):
    url = BASE_URL + "getUpdates"
    params = {"offset": offset, "timeout": 10}
    max_retries = 2

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                return response.json().get("result", [])
        except:
            pass
        time.sleep(1)
    return []

def start_word_game(chat_id):
    category = random.choice(list(word_categories.keys()))
    word = random.choice(word_categories[category])
    hint = "🔤 " + " ".join(["?" for _ in word])

    games["word_game"] = {
        "active": True,
        "word": word,
        "hint": hint,
        "players": {},
        "start_time": time.time(),
        "duration": 60,
        "category": category,
        "attempts": {}
    }

    send_message_simple(chat_id, f"🎮 **بازی کلمات شروع شد!**\n\n📚 **دسته‌بندی:** {category}\n🔤 **کلمه:** {hint}")

def check_word_game(chat_id, text, user_id, user_name, message_id):
    if not games["word_game"]["active"]:
        return False

    if time.time() - games["word_game"]["start_time"] > games["word_game"]["duration"]:
        word = games["word_game"]["word"]
        send_message_simple(chat_id, f"⏰ **زمان بازی تمام شد!**\nکلمه صحیح: {word}")
        games["word_game"]["active"] = False
        return False

    if user_id not in games["word_game"]["attempts"]:
        games["word_game"]["attempts"][user_id] = 0

    if games["word_game"]["attempts"][user_id] >= 3:
        send_message_simple(chat_id, f"⚠️ {user_name} شما ۳ بار حدس زدید و از بازی حذف شدید!")
        return False

    if text == games["word_game"]["word"]:
        games["word_game"]["active"] = False
        send_message_simple(chat_id, f"🎉 **برنده: {user_name}**\n\n✅ کلمه درست: {games['word_game']['word']}")
        return True
    else:
        games["word_game"]["attempts"][user_id] += 1
        games["word_game"]["players"][user_id] = user_name
        if games["word_game"]["attempts"][user_id] < 3:
            send_message_simple(chat_id, f"❌ {user_name} پاسخ اشتباه! {3 - games['word_game']['attempts'][user_id]} فرصت دیگر دارید.")
        return False

def start_riddle(chat_id):
    riddle = random.choice(riddles_cool)
    games["riddle"] = {
        "active": True,
        "question": riddle["q"],
        "answer": riddle["a"],
        "hint": riddle["hint"],
        "prize": random.randint(10, 30),
        "start_time": time.time()
    }
    send_message_simple(chat_id, f"🧩 **چیستان:**\n\n{riddle['q']}\n\n💡 راهنمایی: {riddle['hint']}\n🎁 جایزه: {games['riddle']['prize']} امتیاز")

def check_riddle(chat_id, text, user_id, user_name, message_id):
    if not games["riddle"]["active"]:
        return False

    if text.lower() == games["riddle"]["answer"].lower():
        games["riddle"]["active"] = False
        send_message_simple(chat_id, f"🎉 **برنده: {user_name}**\n\n✅ جواب درست بود!\n💎 {games['riddle']['prize']} امتیاز")
        return True
    return False

def start_mafia(chat_id):
    games["mafia"] = {
        "active": True,
        "players": {},
        "roles": {},
        "phase": "night",
        "day": 1,
        "votes": {},
        "mafia_kill": None,
        "detective_check": None,
        "doctor_save": None,
        "start_time": time.time()
    }
    send_message_simple(chat_id, "🔪 **بازی مافیا شروع شد!**\nبرای پیوستن بنویسید: `پیوستن به مافیا`")

def join_mafia(chat_id, user_id, user_name):
    if not games["mafia"]["active"]:
        return False
    if user_id in games["mafia"]["players"]:
        send_message_simple(chat_id, f"❌ {user_name} شما قبلاً پیوسته‌اید!")
        return False
    games["mafia"]["players"][user_id] = user_name
    player_count = len(games["mafia"]["players"])
    if player_count >= 6:
        send_message_simple(chat_id, "🎭 بازی شروع شد!")
    else:
        send_message_simple(chat_id, f"✅ {user_name} به بازی پیوست! ({player_count}/۶ نفر)")
    return True

def start_word_chain(chat_id):
    games["word_chain"] = {
        "active": True,
        "last_word": "",
        "last_char": "",
        "players": [],
        "current_player": None,
        "used_words": set(),
        "scores": {},
        "start_time": time.time()
    }
    send_message_simple(chat_id, "🔤 **بازی کلمات زنجیره‌ای شروع شد!**\nبرای پیوستن بنویسید: `پیوستن به کلمات زنجیره‌ای`")

def join_word_chain(chat_id, user_id, user_name):
    if not games["word_chain"]["active"]:
        return False
    if user_id in games["word_chain"]["players"]:
        return False
    games["word_chain"]["players"].append(user_id)
    games["word_chain"]["scores"][user_id] = 0
    player_count = len(games["word_chain"]["players"])
    if player_count >= 2:
        start_word_chain_game(chat_id)
    else:
        send_message_simple(chat_id, f"✅ {user_name} پیوست! ({player_count}/۲ نفر)")
    return True

def start_word_chain_game(chat_id):
    random.shuffle(games["word_chain"]["players"])
    games["word_chain"]["current_player"] = 0
    start_words = ["سیب", "کتاب", "مدرسه", "خانه", "ماشین"]
    first_word = random.choice(start_words)
    games["word_chain"]["last_word"] = first_word
    games["word_chain"]["last_char"] = first_word[-1]
    games["word_chain"]["used_words"].add(first_word)
    first_player_id = games["word_chain"]["players"][0]
    first_player_name = get_user_info({"id": first_player_id})
    send_message_simple(chat_id, f"🎮 **بازی شروع شد!**\nکلمه اول: {first_word}\nنوبت: {first_player_name}\nباید با حرف '{games['word_chain']['last_char']}' شروع شود.")

def check_word_chain(chat_id, user_id, text, message_id):
    if not games["word_chain"]["active"]:
        return False
    current_index = games["word_chain"]["current_player"]
    if user_id != games["word_chain"]["players"][current_index]:
        send_message_simple(chat_id, f"❌ الان نوبت شما نیست!")
        return False
    if not text or text[0] != games["word_chain"]["last_char"]:
        send_message_simple(chat_id, f"❌ کلمه باید با حرف '{games['word_chain']['last_char']}' شروع شود!")
        return False
    if text in games["word_chain"]["used_words"]:
        send_message_simple(chat_id, f"❌ این کلمه قبلاً استفاده شده!")
        return False
    games["word_chain"]["used_words"].add(text)
    games["word_chain"]["last_word"] = text
    games["word_chain"]["last_char"] = text[-1]
    games["word_chain"]["scores"][user_id] += 10
    games["word_chain"]["current_player"] = (current_index + 1) % len(games["word_chain"]["players"])
    next_player_id = games["word_chain"]["players"][games["word_chain"]["current_player"]]
    next_player_name = get_user_info({"id": next_player_id})
    send_message_simple(chat_id, f"✅ کلمه قبول شد!\n🔤 کلمه جدید: {text}\n🎯 حرف بعدی: '{text[-1]}'\n👤 نوبت: {next_player_name}")
    return True

def start_quiz(chat_id):
    question = random.choice(quiz_questions)
    games["quiz"] = {
        "active": True,
        "question": question,
        "answers": {},
        "correct_answer": question["a"],
        "points": 10,
        "time_left": 30,
        "start_time": time.time()
    }
    options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(question["options"])])
    send_message_simple(chat_id, f"📚 **مسابقه!**\n\n❓ {question['q']}\n\n{options_text}")

def check_quiz_answer(chat_id, user_id, text, message_id):
    if not games["quiz"]["active"]:
        return False
    if user_id in games["quiz"]["answers"]:
        send_message_simple(chat_id, f"❌ شما قبلاً پاسخ داده‌اید!")
        return False
    correct = games["quiz"]["correct_answer"]
    options = games["quiz"]["question"]["options"]
    is_correct = False
    if text.isdigit():
        idx = int(text) - 1
        if 0 <= idx < len(options):
            is_correct = options[idx] == correct
    else:
        is_correct = text == correct
    if is_correct:
        games["quiz"]["answers"][user_id] = True
        send_message_simple(chat_id, f"✅ {get_user_info({'id': user_id})} پاسخ صحیح داد!")
        games["quiz"]["active"] = False
        return True
    else:
        games["quiz"]["answers"][user_id] = False
        send_message_simple(chat_id, f"❌ {get_user_info({'id': user_id})} پاسخ اشتباه!")
        return False

def add_warning(chat_id, user_id, admin_name, reason):
    global warnings, warning_reasons
    key = f"{chat_id}_{user_id}"

    if key not in warnings:
        warnings[key] = 0
        warning_reasons[key] = []

    warnings[key] += 1
    warning_reasons[key].append({
        "time": datetime.now().isoformat(),
        "admin": admin_name,
        "reason": reason
    })

    update_stats(chat_id, user_id, "warning")
    add_security_log("warning", user_id, f"اخطار {warnings[key]}: {reason} توسط {admin_name}")

    warning_count = warnings[key]

    warning_msg = f"⚠️ **اخطار {warning_count} از {MAX_WARNINGS}**\n"
    warning_msg += f"توسط: {admin_name}\n"
    warning_msg += f"دلیل: {reason}\n"

    if warning_count >= MAX_WARNINGS:
        success, duration = ban_user(chat_id, user_id, permanent=True)
        if success:
            banned_users.add(user_id)
            warning_msg += f"⛔️ **نتیجه: کاربر بن دائمی شد!**\n"
            warning_msg += f"📌 دلیل: رسیدن به {MAX_WARNINGS} اخطار"
            warnings[key] = 0
    else:
        warning_msg += f"📌 {MAX_WARNINGS - warning_count} اخطار تا بن باقی مانده"

    send_message_simple(chat_id, warning_msg)
    return warning_count

def clear_warnings(chat_id, user_id, admin_name):
    key = f"{chat_id}_{user_id}"

    if key in warnings:
        old_count = warnings[key]
        del warnings[key]
        if key in warning_reasons:
            del warning_reasons[key]
        send_message_simple(chat_id, f"✅ اخطارهای کاربر (تعداد: {old_count}) توسط {admin_name} پاک شد.")
        add_security_log("clear_warnings", user_id, f"پاک کردن {old_count} اخطار توسط {admin_name}")
    else:
        send_message_simple(chat_id, "❌ این کاربر هیچ اخطاری ندارد!")

def show_warnings(chat_id, user_id, user_name):
    key = f"{chat_id}_{user_id}"
    count = warnings.get(key, 0)
    reasons = warning_reasons.get(key, [])

    msg = f"📋 **اخطارهای {user_name}**\n\n"
    msg += f"تعداد کل: {count} از {MAX_WARNINGS}\n\n"

    if reasons:
        msg += "**تاریخچه اخطارها:**\n"
        for i, warn in enumerate(reasons, 1):
            msg += f"{i}. {warn['time'][:16]} - توسط {warn['admin']}: {warn['reason']}\n"
    else:
        msg += "هیچ اخطاری ثبت نشده است."

    send_message_simple(chat_id, msg)

def create_ticket(chat_id, user_id, user_name, message):
    global ticket_counter
    ticket_counter += 1
    ticket_id = ticket_counter

    tickets[ticket_id] = {
        "user_id": user_id,
        "chat_id": chat_id,
        "user_name": user_name,
        "message": message,
        "status": "open",
        "time": time.time()
    }

    try:
        admins = requests.get(BASE_URL + "getChatAdministrators", params={"chat_id": chat_id})
        if admins.status_code == 200:
            for admin in admins.json().get("result", []):
                admin_id = admin["user"]["id"]
                if admin_id != user_id:
                    send_message_simple(admin_id,
                        f"🎫 **تیکت جدید #{ticket_id}**\n"
                        f"از: {user_name}\n"
                        f"پیام: {message}\n\n"
                        f"برای پاسخ، ریپلای کن و بنویس: پاسخ {ticket_id} [متن]")
    except:
        pass

    send_message_simple(chat_id, f"✅ تیکت شما با شماره #{ticket_id} ثبت شد.")

def reply_ticket(admin_id, ticket_id, reply_text):
    if ticket_id in tickets:
        ticket = tickets[ticket_id]
        if ticket["status"] == "open":
            send_message_simple(ticket["user_id"],
                f"📬 **پاسخ به تیکت #{ticket_id}**\n\n{reply_text}\n\n- از طرف ادمین")
            ticket["status"] = "answered"
            send_message_simple(admin_id, f"✅ پاسخ شما به تیکت #{ticket_id} ارسال شد.")
        else:
            send_message_simple(admin_id, f"❌ تیکت #{ticket_id} قبلاً بسته شده.")

def handle_new_members(update):
    global welcomed_users
    message = update.get("message")
    if not message:
        return

    new_members = message.get("new_chat_members", [])
    if not new_members:
        return

    chat_id = message["chat"]["id"]

    for member in new_members:
        user_id = member["id"]
        if user_id == int(BOT_TOKEN.split(":")[0]):
            if not check_group_active(chat_id):
                send_message_simple(chat_id, "⚠️ بات یاور اضافه شد.\nبرای فعالسازی، دستور `فعالسازی` را ارسال کنید.")
            continue
            
        if user_id in welcomed_users:
            continue
        
        if not check_group_active(chat_id):
            continue
            
        if WELCOME_ENABLED:
            user_name = get_user_info(member)
            welcome_text = WELCOME_MESSAGE.format(user=user_name, rules=GROUP_RULES)
            send_message_simple(chat_id, welcome_text)
            welcomed_users.add(user_id)

def show_stats(chat_id):
    today = datetime.now().date().isoformat()
    if group_stats["last_reset"] != today:
        group_stats["today_messages"] = 0
        group_stats["last_reset"] = today

    total_users = len(group_stats["active_users"])
    active_today = len([u for u, c in group_stats["active_users"].items() if c > 0])

    stats = "📊 **آمار گروه**\n\n"

    stats += "💬 **پیام‌ها:**\n"
    stats += f"• کل پیام‌ها: {group_stats['total_messages']:,}\n"
    stats += f"• پیام‌های امروز: {group_stats['today_messages']}\n\n"

    stats += "👥 **کاربران:**\n"
    stats += f"• کل کاربران فعال: {total_users}\n"
    stats += f"• کاربران فعال امروز: {active_today}\n\n"

    stats += "🛡️ **آمار مجازات‌ها:**\n"
    stats += f"• بن دائمی: {group_stats['punishments']['ban']}\n"
    stats += f"• بن موقت: {group_stats['punishments']['ban_pulse']}\n"
    stats += f"• سکوت: {group_stats['punishments']['mute']}\n"
    stats += f"• سکوت موفقیت: {group_stats['punishments']['success_mute']}\n\n"

    stats += "⚠️ **امنیت:**\n"
    stats += f"• اسپم تشخیص داده شده: {group_stats['spam_detected']}\n"
    stats += f"• اخطارهای صادر شده: {group_stats['warnings_issued']}\n"
    stats += f"• اخراج‌ها: {group_stats['kicks_performed']}\n\n"

    if group_stats['active_users']:
        stats += "🔥 **پرتکرارترین کاربران:**\n"
        sorted_users = sorted(group_stats['active_users'].items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (user_id, count) in enumerate(sorted_users, 1):
            user_name = get_user_name_by_id(chat_id, user_id)
            stats += f"{i}. {user_name}: {count} پیام\n"

    send_message_simple(chat_id, stats)

def show_security_log(chat_id, count=10):
    log_text = "🔐 **لاگ امنیتی**\n\n"

    if not security_log:
        log_text += "هیچ رویدادی ثبت نشده."
    else:
        for log in security_log[-count:]:
            log_text += f"[{log['time'][:19]}] {log['type']}: {log['details']}\n"

    send_message_simple(chat_id, log_text)

def check_auto_lock(chat_id, user_id, violation_type):
    if not AUTO_LOCK:
        return False

    key = f"{chat_id}_{user_id}"

    if key not in auto_lock_count:
        auto_lock_count[key] = 0
    auto_lock_count[key] += 1

    if auto_lock_count[key] >= 3:
        restrict_user(chat_id, user_id, 3600)
        send_message_simple(chat_id, f"🔇 کاربر {get_user_info({'id': user_id})} به دلیل {auto_lock_count[key]} تخلف، ۱ ساعت سکوت شد.")
        auto_lock_count[key] = 0
        return True

    return False

def check_locks(message, chat_id, user_id, user_name, message_id):
    global LOCK_GIF, LOCK_STICKER, LOCK_PHOTO, LOCK_VIDEO, LOCK_VOICE, LOCK_FILE
    global LOCK_FORWARD, LOCK_CONTACT, LOCK_LOCATION, LOCK_COMMAND, LOCK_BOT
    global LOCK_PERSIAN, LOCK_ENGLISH, LOCK_HASHTAG, LOCK_REPLY, LOCK_SWEAR
    global LOCK_ADVANCED, GROUP_LOCK, STRICT_MODE, LINK_FILTER

    text = message.get("text", "").strip()

    if LINK_FILTER and text and has_link(text):
        if not is_allowed_link(text):
            if not is_admin(chat_id, user_id) or STRICT_MODE:
                delete_message(chat_id, message_id)
                send_message_simple(chat_id, f"🔒 {user_name} ارسال لینک تبلیغاتی ممنوع!")
                update_stats(chat_id, user_id, "lock")
                check_auto_lock(chat_id, user_id, "link")
                return True

    if STRICT_MODE:
        if is_creator(chat_id, user_id):
            pass
        else:
            pass
    else:
        if is_admin(chat_id, user_id):
            return False

    if GROUP_LOCK:
        if STRICT_MODE:
            delete_message(chat_id, message_id)
            send_message_simple(chat_id, f"🔒 {user_name} گروه قفل است! (حالت سختگیرانه)")
            return True
        else:
            if not is_admin(chat_id, user_id):
                delete_message(chat_id, message_id)
                send_message_simple(chat_id, f"🔒 {user_name} گروه قفل است! فقط ادمین‌ها می‌تونن پیام بدن.")
                return True

    if LOCK_ADVANCED:
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} قفل پیشرفته فعال است! همه چیز قفل است.")
        return True

    violation = False
    violation_type = ""

    if LOCK_GIF and message.get("animation"):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} ارسال گیف قفل است!")
        violation = True
        violation_type = "gif"

    elif LOCK_STICKER and message.get("sticker"):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} ارسال استیکر قفل است!")
        violation = True
        violation_type = "sticker"

    elif LOCK_PHOTO and message.get("photo"):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} ارسال عکس قفل است!")
        violation = True
        violation_type = "photo"

    elif LOCK_VIDEO and message.get("video"):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} ارسال فیلم قفل است!")
        violation = True
        violation_type = "video"

    elif LOCK_VOICE and message.get("voice"):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} ارسال ویس قفل است!")
        violation = True
        violation_type = "voice"

    elif LOCK_FILE and message.get("document"):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} ارسال فایل قفل است!")
        violation = True
        violation_type = "file"

    elif LOCK_CONTACT and message.get("contact"):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} ارسال مخاطب قفل است!")
        violation = True
        violation_type = "contact"

    elif LOCK_LOCATION and message.get("location"):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} ارسال مکان قفل است!")
        violation = True
        violation_type = "location"

    elif LOCK_FORWARD and message.get("forward_from"):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} فوروارد قفل است!")
        violation = True
        violation_type = "forward"

    elif LOCK_COMMAND and text.startswith('/'):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} ارسال کامند قفل است!")
        violation = True
        violation_type = "command"

    elif LOCK_BOT and message.get("via_bot"):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} ارسال از طریق ربات قفل است!")
        violation = True
        violation_type = "bot"

    elif text:
        if LOCK_PERSIAN and is_persian(text):
            delete_message(chat_id, message_id)
            send_message_simple(chat_id, f"🔒 {user_name} ارسال متن فارسی قفل است!")
            violation = True
            violation_type = "persian"

        elif LOCK_ENGLISH and is_english(text):
            delete_message(chat_id, message_id)
            send_message_simple(chat_id, f"🔒 {user_name} ارسال متن انگلیسی قفل است!")
            violation = True
            violation_type = "english"

        elif LOCK_HASHTAG and has_hashtag(text):
            delete_message(chat_id, message_id)
            send_message_simple(chat_id, f"🔒 {user_name} ارسال هشتگ قفل است!")
            violation = True
            violation_type = "hashtag"

    elif LOCK_REPLY and message.get("reply_to_message"):
        delete_message(chat_id, message_id)
        send_message_simple(chat_id, f"🔒 {user_name} ریپلای زدن قفل است!")
        violation = True
        violation_type = "reply"

    if not violation and LOCK_SWEAR and text:
        current_banned = banned_words.copy()
        if STRICT_MODE:
            current_banned.extend(strict_banned_words)

        for word in current_banned:
            if word in text:
                delete_message(chat_id, message_id)
                send_message_simple(chat_id, f"🔒 {user_name} کلمات نامناسب ممنوع است!")
                violation = True
                violation_type = "swear"
                break

    if violation:
        update_stats(chat_id, user_id, "lock")
        check_auto_lock(chat_id, user_id, violation_type)
        return True

    return False

def get_joke_from_api():
    apis = [
        {
            "name": "CodeBazan",
            "url": "https://api.codebazan.ir/joke/",
            "parser": lambda data: data.get("result", "") if isinstance(data, dict) else data
        },
        {
            "name": "JokeAPI",
            "url": "https://v2.jokeapi.dev/joke/Any?lang=fa&type=twopart",
            "parser": lambda data: f"{data.get('setup', '')}\n\n{data.get('delivery', '')}" if isinstance(data, dict) else ""
        }
    ]

    for api in apis:
        try:
            response = requests.get(api["url"], timeout=3)
            if response.status_code == 200:
                try:
                    data = response.json()
                    joke = api["parser"](data)
                    if joke and len(joke) > 10:
                        return f"😂 **جوک لحظه‌ای:**\n\n{joke}\n\n🤣 نوش‌جان!"
                except:
                    text = response.text.strip()
                    if text and len(text) > 10:
                        return f"😂 **جوک لحظه‌ای:**\n\n{text}\n\n🤣 نوش‌جان!"
        except:
            continue

    fallback_jokes = [
        "😂 یه بابایی میره دکتر میگه: دکتر! من هر چی می‌خورم چاق نمی‌شم! دکتر میگه: اشکال از ژنتیکه! میگه: نه بابا، اشکال از زنه، هر چی درست می‌کنه می‌خورم چاق نمی‌شم!",
        "😂 به یه بچه میگن اون چه حیوونیه که به ما گوشت، شیر، ماست، کفش، لباس میده؟ بچه میگه: بابام!",
    ]
    return f"😂 **جوک تصادفی:**\n\n{random.choice(fallback_jokes)}\n\n🤣 (از جوک‌های آفلاین استفاده شد)"

def mafia_night_action(chat_id, user_id, action, target_id):
    if not games["mafia"]["active"] or games["mafia"]["phase"] != "night":
        return False

    role = games["mafia"]["roles"].get(user_id)

    if role == "mafia" and action == "کشتن":
        games["mafia"]["mafia_kill"] = target_id
        send_message_simple(chat_id, f"🔪 مافیا هدف خود را انتخاب کرد.")
        return True

    elif role == "doctor" and action == "نجات":
        games["mafia"]["doctor_save"] = target_id
        send_message_simple(chat_id, f"💊 دکتر هدف خود را انتخاب کرد.")
        return True

    elif role == "detective" and action == "بررسی":
        games["mafia"]["detective_check"] = target_id
        target_role = games["mafia"]["roles"].get(target_id)
        is_mafia = target_role == "mafia"
        result = "🔍 این نفر **مافیا است**!" if is_mafia else "🔍 این نفر **مافیا نیست**."
        send_message_simple(user_id, result)
        return True

    return False

def get_user_level(chat_id, user_id):
    key = f"{chat_id}_{user_id}"
    if key not in user_levels:
        user_levels[key] = 1
    return user_levels[key]

def get_user_score(chat_id, user_id):
    key = f"{chat_id}_{user_id}"
    if key not in user_scores:
        user_scores[key] = 0
    return user_scores[key]

def add_score(chat_id, user_id, points, reason=""):
    global SCORE_SYSTEM_ENABLED

    if not SCORE_SYSTEM_ENABLED:
        return

    key = f"{chat_id}_{user_id}"

    if key not in user_scores:
        user_scores[key] = 0

    user_scores[key] += points

    old_level = get_user_level(chat_id, user_id)
    new_level = calculate_level(user_scores[key])

    if new_level > old_level:
        user_levels[key] = new_level
        send_message_simple(chat_id, f"🎉 **تبریک!**\nشما به سطح {new_level} ({level_titles[new_level]}) ارتقا یافتید!")
        add_security_log("level_up", user_id, f"ارتقا به سطح {new_level}")

    return user_scores[key]

def calculate_level(score):
    for level, threshold in sorted(level_thresholds.items(), reverse=True):
        if score >= threshold:
            return level
    return 1

def show_user_score(chat_id, user_id, user_name):
    score = get_user_score(chat_id, user_id)
    level = get_user_level(chat_id, user_id)
    next_level = level + 1 if level < 10 else 10
    next_threshold = level_thresholds.get(next_level, level_thresholds[10])
    progress = score - level_thresholds[level]
    total_needed = next_threshold - level_thresholds[level]
    percent = int((progress / total_needed) * 100) if total_needed > 0 else 100

    score_msg = f"📊 **امتیازات {user_name}**\n\n"
    score_msg += f"⭐ سطح {level}: {level_titles[level]}\n"
    score_msg += f"💎 امتیاز کل: {score}\n"

    if level < 10:
        score_msg += f"🎯 پیشرفت به سطح بعد: {progress}/{total_needed} ({percent}%)\n"
        bar = "█" * (percent // 10) + "░" * (10 - (percent // 10))
        score_msg += f"📈 {bar}\n"

    send_message_simple(chat_id, score_msg)

def show_leaderboard(chat_id):
    group_scores = {}
    for key, score in user_scores.items():
        if key.startswith(str(chat_id)):
            user_id = int(key.split("_")[1])
            group_scores[user_id] = score

    sorted_users = sorted(group_scores.items(), key=lambda x: x[1], reverse=True)[:10]

    leaderboard = "🏆 **جدول برترین‌ها**\n\n"

    if not sorted_users:
        leaderboard += "هنوز کسی امتیازی کسب نکرده!"
    else:
        for i, (user_id, score) in enumerate(sorted_users, 1):
            level = get_user_level(chat_id, user_id)
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            leaderboard += f"{medal} کاربر {user_id} - سطح {level} - {score} امتیاز\n"

    send_message_simple(chat_id, leaderboard)

def check_spam(chat_id, user_id, text, message_id, user_name):
    if not ANTI_SPAM_ENABLED:
        return False

    current_time = time.time()
    key = f"{chat_id}_{user_id}"

    msg_key = f"{chat_id}_{text}"
    if text and len(text) > 10:
        if msg_key not in duplicate_messages:
            duplicate_messages[msg_key] = {
                "time": current_time,
                "count": 1,
                "users": {user_id}
            }
        else:
            duplicate_messages[msg_key]["count"] += 1
            duplicate_messages[msg_key]["users"].add(user_id)

            if duplicate_messages[msg_key]["count"] > MAX_SPAM_COUNT:
                delete_message(chat_id, message_id)
                send_message_simple(chat_id, f"⚠️ {user_name} پیام تکراری ممنوع!")
                update_stats(chat_id, user_id, "spam")
                add_security_log("spam", user_id, f"پیام تکراری: {text[:50]}")
                return True

    if key in spam_time:
        time_diff = current_time - spam_time[key]
        if time_diff < 1:
            if key not in spam_count:
                spam_count[key] = 0
            spam_count[key] += 1

            if spam_count[key] > 3:
                delete_message(chat_id, message_id)
                send_message_simple(chat_id, f"⚠️ {user_name} سرعت ارسال پیام بالاست!")
                update_stats(chat_id, user_id, "spam")
                return True
        else:
            spam_count[key] = 0

    spam_time[key] = current_time
    return False

def handle_message(update):
    global LOCK_GIF, LOCK_STICKER, LOCK_PHOTO, LOCK_VIDEO, LOCK_VOICE, LOCK_FILE
    global LOCK_FORWARD, LOCK_CONTACT, LOCK_LOCATION, LOCK_COMMAND, LOCK_BOT
    global LOCK_PERSIAN, LOCK_ENGLISH, LOCK_HASHTAG, LOCK_REPLY, LOCK_SWEAR
    global LOCK_ADVANCED, AUTO_LOCK, GROUP_LOCK, STRICT_MODE, GROUP_RULES
    global WELCOME_ENABLED, LINK_FILTER, ANTI_SPAM_ENABLED, AUTO_KICK_ENABLED
    global SCORE_SYSTEM_ENABLED, broadcast_status, group_names, active_groups, activation_time, ignored_messages
    global number_game, name_family_game

    message = update.get("message")
    if not message:
        return

    sender = message.get("from")
    if not sender:
        return

    chat_id = message["chat"]["id"]
    user_id = sender["id"]
    user_name = get_user_info(sender)
    text = message.get("text", "").strip()
    message_id = message.get("message_id")
    is_group = message["chat"]["type"] in ["group", "supergroup"]

    chat_title = message["chat"].get("title") if is_group else None

    reply_to = message.get("reply_to_message")
    reply_to_user = None
    reply_to_message_id = None

    if reply_to:
        reply_to_user = reply_to.get("from")
        reply_to_message_id = reply_to.get("message_id")

    # لاگ دستور بگو
    if text and text.startswith("بگو "):
        msg_to_send = text[4:].strip()
        if msg_to_send:
            print(f"\n📢 [{user_name}] گفت: بگو {msg_to_send}")

    if is_group:
        update_groups(chat_id, "group", chat_title)
    update_contacts(user_id, user_name)

    # ===== پی وی =====
    if not is_group:
        if is_master_admin(user_id):
            if user_id in broadcast_status:
                if handle_broadcast_media(user_id, message):
                    return
                if handle_broadcast_message(user_id, text):
                    return
            if handle_broadcast_selection(user_id, text):
                return
            if text == "📢 ارسال همگانی":
                show_broadcast_menu(user_id)
            elif text == "📊 آمار همگانی":
                stats = get_broadcast_stats()
                send_message_simple(user_id, stats)
                show_main_menu(user_id)
            elif text == "👥 لیست مخاطبین":
                show_contacts(user_id)
            elif text == "👥 لیست گروه‌ها":
                show_groups(user_id)
            elif text == "🚪 لفت از گروه":
                send_message_simple(user_id, "🔍 لطفاً نام گروه را وارد کنید:\nمثال: `لفت اسم گروه`")
            elif text and text.startswith("لفت "):
                leave_group_by_name(user_id, text[4:].strip())
            elif text and text.startswith("لفت با آیدی "):
                leave_group_by_id(user_id, text[11:].strip())
            elif text == "⚙️ تنظیمات":
                send_message_simple(user_id, "⚙️ تنظیمات در حال توسعه...")
            elif text == "❓ راهنما":
                send_message_simple(user_id, get_help_text())
                show_main_menu(user_id)
            elif text == "🔙 خروج":
                remove_keyboard(user_id, "✅ از منوی ادمین خارج شدید.")
            elif text == "💝 حمایت مالی":
                send_support_message(user_id)
            elif text == "📢 تبلیغات":
                send_ads_message(user_id)
            elif text == "📖 راهنما":
                send_message_simple(user_id, get_user_help_text())
                show_user_menu(user_id)
            else:
                show_main_menu(user_id)
        else:
            if text == "💝 حمایت مالی":
                send_support_message(user_id)
            elif text == "📢 تبلیغات":
                send_ads_message(user_id)
            elif text == "📖 راهنما":
                send_message_simple(user_id, get_user_help_text())
                show_user_menu(user_id)
            elif text == "🔙 خروج":
                remove_keyboard(user_id, "✅ خارج شدید.")
            else:
                show_user_menu(user_id)
        return

    # ===== گروه - بررسی فعال بودن =====
    if is_group and not check_group_active(chat_id):
        ignored_messages.add((chat_id, message_id))
        
        if text == "فعالسازی":
            if is_admin(chat_id, user_id):
                now_time = datetime.now()
                active_groups.add(chat_id)
                activation_time[chat_id] = now_time
                send_message_simple(chat_id, f"✅ **بات یاور با موفقیت فعال شد!**\n\n⏰ زمان فعالسازی: {now_time.strftime('%Y-%m-%d %H:%M:%S')}\n\nحالا می‌توانید از تمام دستورات استفاده کنید.\nبرای مشاهده دستورات، `راهنما` را ارسال کنید.")
                logger.info(f"✅ بات در گروه {chat_id} فعال شد")
            else:
                send_message_simple(chat_id, "❌ فقط ادمین‌های گروه می‌توانند بات را فعال کنند!")
        return

    if is_group and check_group_active(chat_id):
        if (chat_id, message_id) in ignored_messages:
            return

    if text == "غیرفعالسازی" and is_admin(chat_id, user_id):
        if chat_id in active_groups:
            active_groups.remove(chat_id)
            if chat_id in activation_time:
                del activation_time[chat_id]
            send_message_simple(chat_id, "✅ بات با موفقیت غیرفعال شد.\nبرای فعالسازی مجدد، دستور `فعالسازی` را ارسال کنید.")
            logger.info(f"❌ بات در گروه {chat_id} غیرفعال شد")
        else:
            send_message_simple(chat_id, "❌ بات در این گروه فعال نیست!")
        return

    if text == "راهنما" or text == "help":
        send_message_simple(user_id, get_help_text())
        send_message_simple(chat_id, f"📬 {user_name} راهنمای بات در پی وی شما ارسال شد.")
        return

    if text and text.startswith("بگو "):
        msg_to_send = text[4:].strip()
        if msg_to_send:
            delete_message(chat_id, message_id)
            send_message_simple(chat_id, msg_to_send)
            print(f"✅ ارسال شد: {msg_to_send}")
        else:
            send_message_simple(chat_id, "❌ لطفاً بعد از بگو یه چیزی بنویس!")
        return

    # ===== بازی حدس عدد =====
    if text == "بازی عدد":
        if is_admin(chat_id, user_id):
            start_number_game(chat_id)
        else:
            send_message_simple(chat_id, "❌ فقط ادمین می‌تواند بازی را شروع کند!")
        return
    
    if text and text.startswith("بازی عدد ") and is_admin(chat_id, user_id):
        try:
            parts = text.split()
            if len(parts) == 3:
                min_num = int(parts[1])
                max_num = int(parts[2])
                if min_num < max_num:
                    start_number_game(chat_id, min_num, max_num)
                else:
                    send_message_simple(chat_id, "❌ عدد اول باید کوچکتر از عدد دوم باشد!")
            else:
                start_number_game(chat_id)
        except:
            send_message_simple(chat_id, "❌ فرمت صحیح: `بازی عدد [حداقل] [حداکثر]`")
        return
    
    # بررسی حدس عدد
    if number_game["active"] and text and text.isdigit():
        if check_number_guess(chat_id, user_id, user_name, text, message_id):
            return
    
    # ===== بازی اسم فامیل =====
    if text == "اسم فامیل" and is_admin(chat_id, user_id):
        start_name_family(chat_id)
        return
    
    # بررسی پاسخ اسم فامیل
    if name_family_game["active"] and text and ":" in text:
        if check_name_family_answer(chat_id, user_id, user_name, text, message_id):
            return
    
    # ===== لینک دعوت =====
    if text == "لینک دعوت":
        get_group_invite_link(chat_id, user_id, user_name)
        return
    
    if text == "باطل لینک" and is_admin(chat_id, user_id):
        revoke_invite_link(chat_id, user_id)
        return

    if text == "اوقات شرعی":
        prayer_times = get_prayer_times("تهران")
        if prayer_times:
            send_message_simple(chat_id, prayer_times)
        else:
            send_message_simple(chat_id, "❌ خطا در دریافت اوقات شرعی. لطفاً دوباره تلاش کنید.")
        return

    if text and text.startswith("اوقات "):
        city = text[6:].strip()
        if city:
            prayer_times = get_prayer_times(city)
            if prayer_times:
                send_message_simple(chat_id, prayer_times)
            else:
                send_message_simple(chat_id, f"❌ خطا در دریافت اوقات شرعی برای {city}. لطفاً نام شهر را درست وارد کنید.")
        else:
            send_message_simple(chat_id, "❌ لطفاً نام شهر را وارد کنید. مثال: اوقات تهران")
        return

    if text == "رپ":
        rap = random.choice(raps)
        send_message_simple(chat_id, rap)
        return

    if text == "عشق":
        love = random.choice(love_sms)
        send_message_simple(chat_id, love)
        return

    if text == "فال":
        fal = random.choice(hafez_fal)
        send_message_simple(chat_id, fal)
        return

    if text == "انگیزه":
        motivate = random.choice(motivation)
        send_message_simple(chat_id, motivate)
        return

    if text == "نقل قول":
        quote = random.choice(quotes)
        send_message_simple(chat_id, quote)
        return

    if text == "معما":
        riddle = random.choice(riddles_cool)
        games["riddle"] = {
            "active": True,
            "question": riddle["q"],
            "answer": riddle["a"],
            "hint": riddle["hint"],
            "prize": random.randint(10, 30),
            "start_time": time.time()
        }
        send_message_simple(chat_id, f"🧩 **معما:**\n\n{riddle['q']}\n\n💡 راهنمایی: {riddle['hint']}\n🎁 جایزه: {games['riddle']['prize']} امتیاز")
        return

    if text == "راهنمای بازی" or text == "راهنمای بازی کلمات":
        send_message_simple(chat_id, get_game_help())
        return

    update_stats(chat_id, user_id, "message")

    if check_spam(chat_id, user_id, text, message_id, user_name):
        return

    if check_locks(message, chat_id, user_id, user_name, message_id):
        return

    if games["word_game"]["active"]:
        if check_word_game(chat_id, text, user_id, user_name, message_id):
            return

    if games["riddle"]["active"]:
        if check_riddle(chat_id, text, user_id, user_name, message_id):
            return

    if games["mafia"]["active"]:
        if text and text.startswith("پیوستن به مافیا"):
            join_mafia(chat_id, user_id, user_name)
            return

        if games["mafia"]["phase"] == "night":
            if text and text.startswith("کشتن "):
                try:
                    target_id = int(text[5:].strip())
                    mafia_night_action(chat_id, user_id, "کشتن", target_id)
                except:
                    pass
                return
            elif text and text.startswith("نجات "):
                try:
                    target_id = int(text[5:].strip())
                    mafia_night_action(chat_id, user_id, "نجات", target_id)
                except:
                    pass
                return
            elif text and text.startswith("بررسی "):
                try:
                    target_id = int(text[6:].strip())
                    mafia_night_action(chat_id, user_id, "بررسی", target_id)
                except:
                    pass
                return

    if games["word_chain"]["active"]:
        if text and text.startswith("پیوستن به کلمات زنجیره‌ای"):
            join_word_chain(chat_id, user_id, user_name)
            return

        if check_word_chain(chat_id, user_id, text, message_id):
            return

    if games["quiz"]["active"]:
        if check_quiz_answer(chat_id, user_id, text, message_id):
            return

    if text == "تاریخ":
        send_message_simple(chat_id, f"📅 **تاریخ امروز:**\n\n{get_current_date()}")
        return

    if text == "ساعت" or text == "ساعتی":
        send_message_simple(chat_id, f"🕐 **ساعت فعلی:**\n\n{get_current_time()}")
        return

    if text and text.startswith("فایل "):
        content = text[5:].strip()
        if content:
            filename = f"file_{int(time.time())}.txt"
            if create_text_file(content, filename):
                send_document(chat_id, filename)
                os.remove(filename)
            else:
                send_message_simple(chat_id, "❌ خطا در ساخت فایل!")
        else:
            send_message_simple(chat_id, "❌ لطفاً متن فایل را وارد کنید!")
        return

    if text == "دانستنی":
        send_message_simple(chat_id, f"🧠 **دانستنی جالب:**\n\n{get_fun_fact()}")
        return

    if text and text.startswith("ایکو "):
        content = text[5:].strip()
        if content:
            if create_qr_code(content):
                send_photo(chat_id, "qrcode.png", caption="📱 QR code شما")
                os.remove("qrcode.png")
            else:
                send_message_simple(chat_id, "❌ خطا در ساخت QR code!")
        else:
            send_message_simple(chat_id, "❌ لطفاً متن را وارد کنید!")
        return

    if text and text.startswith("اصل "):
        content = text[4:].strip()
        if content:
            result = detect_original(content)
            send_message_simple(chat_id, result)
        else:
            send_message_simple(chat_id, "❌ لطفاً متن را وارد کنید!")
        return

    if text and text.startswith("اطلاعات "):
        try:
            target_id = int(text[8:].strip())
            info = get_user_info_by_id(chat_id, target_id)
            send_message_simple(chat_id, info)
        except:
            send_message_simple(chat_id, "❌ آیدی نامعتبر است!")
        return

    if text and text.startswith("متن کامنت "):
        content = text[10:].strip()
        if content:
            result = create_fancy_text(content)
            send_message_simple(chat_id, result)
        else:
            send_message_simple(chat_id, "❌ لطفاً متن را وارد کنید!")
        return

    if text and text.startswith("سیجاق "):
        content = text[6:].strip()
        if content:
            result = siag(content)
            send_message_simple(chat_id, f"🔄 **متن سیجاق شده:**\n\n{result}")
        else:
            send_message_simple(chat_id, "❌ لطفاً متن را وارد کنید!")
        return

    if text and text.startswith("گزارش ") and reply_to_user:
        reason = text[7:].strip()
        if reason:
            if report_user(chat_id, user_id, reply_to_user["id"], reason):
                send_message_simple(chat_id, f"✅ گزارش شما با موفقیت ثبت شد.")
            else:
                send_message_simple(chat_id, "❌ خطا در ثبت گزارش!")
        else:
            send_message_simple(chat_id, "❌ لطفاً دلیل گزارش را بنویسید!")
        return

    if text and text.startswith("یاد دادن کلمه "):
        try:
            parts = text[13:].split("=")
            if len(parts) == 2:
                word = parts[0].strip()
                meaning = parts[1].strip()
                result = learn_word(word, meaning)
                send_message_simple(chat_id, result)
            else:
                send_message_simple(chat_id, "❌ فرمت درست نیست!\nمثال: `یاد دادن کلمه سلام = Hello`")
        except:
            send_message_simple(chat_id, "❌ خطا در ثبت کلمه!")
        return

    if text and text.startswith("کلمه "):
        word = text[5:].strip()
        if word:
            result = get_word_meaning(word)
            send_message_simple(chat_id, result)
        else:
            send_message_simple(chat_id, "❌ لطفاً کلمه را وارد کنید!")
        return

    if text == "لیست ادمین ها":
        admins = get_admins_list(chat_id)
        send_message_simple(chat_id, admins)
        return

    if is_admin(chat_id, user_id):
        if text and text.startswith("تنظیم توضیحات "):
            description = text[15:].strip()
            if description:
                result = set_group_description(chat_id, description)
                send_message_simple(chat_id, result)
            else:
                send_message_simple(chat_id, "❌ لطفاً توضیحات را وارد کنید!")
            return

        if text and text.startswith("تنظیم اسم "):
            name = text[10:].strip()
            if name:
                result = set_group_name(chat_id, name)
                send_message_simple(chat_id, result)
            else:
                send_message_simple(chat_id, "❌ لطفاً نام جدید را وارد کنید!")
            return

    if is_admin(chat_id, user_id) and reply_to_user:
        if text and text.startswith("بن پالس "):
            try:
                duration = int(text[8:].strip())
                target_id = reply_to_user["id"]
                target_name = get_user_info(reply_to_user)
                success, duration_str = ban_user(chat_id, target_id, permanent=False, duration=duration)
                if success:
                    send_message_simple(chat_id, f"⛔️ **بن موقت**\nکاربر: {target_name}\nمدت: {duration_str}\nتوسط: {user_name}")
                    group_stats["punishments"]["ban_pulse"] += 1
                else:
                    send_message_simple(chat_id, "❌ خطا در بن کاربر!")
            except:
                send_message_simple(chat_id, "❌ فرمت درست نیست!\nمثال: `بن پالس 60`")
            return

        elif text == "بن":
            target_id = reply_to_user["id"]
            target_name = get_user_info(reply_to_user)
            success, duration_str = ban_user(chat_id, target_id, permanent=True)
            if success:
                send_message_simple(chat_id, f"⛔️ **بن دائمی**\nکاربر: {target_name}\nتوسط: {user_name}")
                group_stats["punishments"]["ban"] += 1
            else:
                send_message_simple(chat_id, "❌ خطا در بن کاربر!")
            return

        elif text and text.startswith("اخطار "):
            reason = text[6:].strip()
            if reason:
                target_id = reply_to_user["id"]
                add_warning(chat_id, target_id, user_name, reason)
            else:
                send_message_simple(chat_id, "❌ لطفاً دلیل اخطار را بنویسید!\nمثال: `اخطار تبلیغ`")
            return

        elif text and text.startswith("سکوت "):
            try:
                duration = int(text[5:].strip())
                target_id = reply_to_user["id"]
                target_name = get_user_info(reply_to_user)
                if restrict_user(chat_id, target_id, duration):
                    send_message_simple(chat_id, f"🔇 **سکوت**\nکاربر: {target_name}\nمدت: {duration} ثانیه\nتوسط: {user_name}")
                else:
                    send_message_simple(chat_id, "❌ خطا در سکوت کاربر!")
            except:
                send_message_simple(chat_id, "❌ فرمت درست نیست!\nمثال: `سکوت 30`")
            return

        elif text == "سکوت موفقیت":
            target_id = reply_to_user["id"]
            target_name = get_user_info(reply_to_user)
            if restrict_user(chat_id, target_id, 86400):
                send_message_simple(chat_id, f"🔇 **سکوت موفقیت (۲۴ ساعت)**\nکاربر: {target_name}\nتوسط: {user_name}")
                group_stats["punishments"]["success_mute"] += 1
            else:
                send_message_simple(chat_id, "❌ خطا در سکوت کاربر!")
            return

        elif text == "حذف سکوت":
            target_id = reply_to_user["id"]
            target_name = get_user_info(reply_to_user)
            if unrestrict_user(chat_id, target_id):
                send_message_simple(chat_id, f"🔊 **سکوت برداشته شد**\nکاربر: {target_name}\nتوسط: {user_name}")
            else:
                send_message_simple(chat_id, "❌ خطا در برداشتن سکوت!")
            return

        elif text == "اخطارها":
            target_id = reply_to_user["id"]
            target_name = get_user_info(reply_to_user)
            show_warnings(chat_id, target_id, target_name)
            return

        elif text == "پاک کردن اخطار":
            target_id = reply_to_user["id"]
            clear_warnings(chat_id, target_id, user_name)
            return

    if is_admin(chat_id, user_id):
        if text == "مشاهده تنظیمات":
            show_settings(chat_id)
            return
        elif text == "قفل خودکار":
            AUTO_LOCK = not AUTO_LOCK
            status = "فعال" if AUTO_LOCK else "غیرفعال"
            send_message_simple(chat_id, f"✅ قفل خودکار {status} شد!")
            return
        elif text == "قفل گروه":
            GROUP_LOCK = not GROUP_LOCK
            status = "فعال" if GROUP_LOCK else "غیرفعال"
            send_message_simple(chat_id, f"✅ قفل گروه {status} شد!")
            return
        elif text == "سختگیرانه":
            STRICT_MODE = not STRICT_MODE
            status = "فعال" if STRICT_MODE else "غیرفعال"
            send_message_simple(chat_id, f"✅ حالت سختگیرانه {status} شد!")
            return
        elif text and text.startswith("قوانین"):
            if text == "قوانین":
                send_message_simple(chat_id, GROUP_RULES)
            elif text and text.startswith("قوانین "):
                new_rules = text[7:].strip()
                if new_rules:
                    GROUP_RULES = new_rules
                    send_message_simple(chat_id, "✅ قوانین گروه به‌روزرسانی شد!")
                else:
                    send_message_simple(chat_id, "❌ لطفاً متن قوانین رو وارد کن!")
            return
        elif text == "فیلتر لینک":
            LINK_FILTER = not LINK_FILTER
            status = "فعال" if LINK_FILTER else "غیرفعال"
            send_message_simple(chat_id, f"✅ فیلتر لینک {status} شد!")
            return
        elif text == "خوشامدگویی":
            WELCOME_ENABLED = not WELCOME_ENABLED
            status = "فعال" if WELCOME_ENABLED else "غیرفعال"
            send_message_simple(chat_id, f"✅ خوشامدگویی {status} شد!")
            return
        elif text == "آنتی اسپم":
            ANTI_SPAM_ENABLED = not ANTI_SPAM_ENABLED
            status = "فعال" if ANTI_SPAM_ENABLED else "غیرفعال"
            send_message_simple(chat_id, f"✅ آنتی اسپم {status} شد!")
            return
        elif text == "سیستم امتیاز":
            SCORE_SYSTEM_ENABLED = not SCORE_SYSTEM_ENABLED
            status = "فعال" if SCORE_SYSTEM_ENABLED else "غیرفعال"
            send_message_simple(chat_id, f"✅ سیستم امتیاز {status} شد!")
            return
        elif text == "آمار":
            show_stats(chat_id)
            return
        elif text == "لاگ امنیتی":
            show_security_log(chat_id)
            return
        elif text == "بازی کلمات":
            start_word_game(chat_id)
            return
        elif text == "چیستان":
            start_riddle(chat_id)
            return
        elif text == "مافیا":
            start_mafia(chat_id)
            return
        elif text == "کلمات زنجیره‌ای":
            start_word_chain(chat_id)
            return
        elif text == "مسابقه":
            start_quiz(chat_id)
            return
        elif text and text.startswith("لینک مجاز "):
            link = text[10:].strip()
            if link:
                ALLOWED_LINKS.append(link)
                send_message_simple(chat_id, f"✅ لینک {link} به لیست سفید اضافه شد!")
            return

    if text == "امتیاز من":
        show_user_score(chat_id, user_id, user_name)
        return

    if text == "امتیازها" or text == "برترین‌ها":
        show_leaderboard(chat_id)
        return

    if text and text.startswith("تیکت "):
        ticket_text = text[5:].strip()
        if ticket_text:
            create_ticket(chat_id, user_id, user_name, ticket_text)
        else:
            send_message_simple(chat_id, "❌ لطفاً متن تیکت رو وارد کن!")
        return

    if text and text.startswith("پاسخ ") and is_admin(chat_id, user_id):
        try:
            parts = text.split()
            ticket_id = int(parts[1])
            reply_text = " ".join(parts[2:])
            if reply_text:
                reply_ticket(user_id, ticket_id, reply_text)
            else:
                send_message_simple(chat_id, "❌ لطفاً متن پاسخ رو وارد کن!")
        except:
            send_message_simple(chat_id, "❌ فرمت درست نیست. بنویس: پاسخ [شماره تیکت] [متن]")
        return

    if is_admin(chat_id, user_id):
        locks = {
            "قفل گیف": "LOCK_GIF",
            "باز کردن گیف": "LOCK_GIF",
            "قفل استیکر": "LOCK_STICKER",
            "باز کردن استیکر": "LOCK_STICKER",
            "قفل عکس": "LOCK_PHOTO",
            "باز کردن عکس": "LOCK_PHOTO",
            "قفل فیلم": "LOCK_VIDEO",
            "باز کردن فیلم": "LOCK_VIDEO",
            "قفل ویس": "LOCK_VOICE",
            "باز کردن ویس": "LOCK_VOICE",
            "قفل فایل": "LOCK_FILE",
            "باز کردن فایل": "LOCK_FILE",
            "قفل فوروارد": "LOCK_FORWARD",
            "باز کردن فوروارد": "LOCK_FORWARD",
            "قفل مخاطب": "LOCK_CONTACT",
            "باز کردن مخاطب": "LOCK_CONTACT",
            "قفل مکان": "LOCK_LOCATION",
            "باز کردن مکان": "LOCK_LOCATION",
            "قفل کامند": "LOCK_COMMAND",
            "باز کردن کامند": "LOCK_COMMAND",
            "قفل ربات": "LOCK_BOT",
            "باز کردن ربات": "LOCK_BOT",
            "قفل فارسی": "LOCK_PERSIAN",
            "باز کردن فارسی": "LOCK_PERSIAN",
            "قفل انگلیسی": "LOCK_ENGLISH",
            "باز کردن انگلیسی": "LOCK_ENGLISH",
            "قفل هشتگ": "LOCK_HASHTAG",
            "باز کردن هشتگ": "LOCK_HASHTAG",
            "قفل ریپلای": "LOCK_REPLY",
            "باز کردن ریپلای": "LOCK_REPLY",
            "قفل فحش": "LOCK_SWEAR",
            "باز کردن فحش": "LOCK_SWEAR",
            "قفل پیشرفته": "LOCK_ADVANCED",
            "باز کردن پیشرفته": "LOCK_ADVANCED",
        }

        if text in locks:
            lock_var = locks[text]
            is_lock = "قفل" in text and "باز" not in text
            globals()[lock_var] = is_lock

            if lock_var == "LOCK_ADVANCED":
                if is_lock:
                    LOCK_GIF = LOCK_STICKER = LOCK_PHOTO = LOCK_VIDEO = LOCK_VOICE = True
                    LOCK_FILE = LOCK_FORWARD = LOCK_CONTACT = LOCK_LOCATION = True
                    LOCK_COMMAND = LOCK_BOT = LOCK_PERSIAN = LOCK_ENGLISH = LOCK_HASHTAG = True
                    LOCK_REPLY = LOCK_SWEAR = True
                    send_message_simple(chat_id, "🔒 قفل پیشرفته فعال شد! همه چیز قفل است.")
                else:
                    LOCK_GIF = LOCK_STICKER = LOCK_PHOTO = LOCK_VIDEO = LOCK_VOICE = False
                    LOCK_FILE = LOCK_FORWARD = LOCK_CONTACT = LOCK_LOCATION = False
                    LOCK_COMMAND = LOCK_BOT = LOCK_PERSIAN = LOCK_ENGLISH = LOCK_HASHTAG = False
                    LOCK_REPLY = LOCK_SWEAR = False
                    send_message_simple(chat_id, "🔓 قفل پیشرفته غیرفعال شد! همه قفل‌ها باز شد.")
            else:
                status = "قفل" if is_lock else "باز"
                send_message_simple(chat_id, f"✅ {text} شد!")
            return

        if text == "وضعیت":
            show_settings(chat_id)
            return

    current_time = time.time()
    if user_id in last_reply_time and current_time - last_reply_time[user_id] < COOLDOWN:
        return

    if text == "جوک":
        joke = get_joke_from_api()
        send_message_simple(chat_id, joke)
        last_reply_time[user_id] = current_time
        return

    if text in responses:
        reply = random.choice(responses[text])
        send_message_simple(chat_id, reply)
        last_reply_time[user_id] = current_time

def show_settings(chat_id):
    settings = "⚙️ **تنظیمات بات**\n\n"

    settings += "🔒 **وضعیت قفل‌ها:**\n"
    settings += f"• گیف: {'✅' if LOCK_GIF else '❌'}\n"
    settings += f"• استیکر: {'✅' if LOCK_STICKER else '❌'}\n"
    settings += f"• عکس: {'✅' if LOCK_PHOTO else '❌'}\n"
    settings += f"• فیلم: {'✅' if LOCK_VIDEO else '❌'}\n"
    settings += f"• ویس: {'✅' if LOCK_VOICE else '❌'}\n"
    settings += f"• فایل: {'✅' if LOCK_FILE else '❌'}\n"
    settings += f"• فوروارد: {'✅' if LOCK_FORWARD else '❌'}\n"
    settings += f"• مخاطب: {'✅' if LOCK_CONTACT else '❌'}\n"
    settings += f"• مکان: {'✅' if LOCK_LOCATION else '❌'}\n"
    settings += f"• کامند: {'✅' if LOCK_COMMAND else '❌'}\n"
    settings += f"• ربات: {'✅' if LOCK_BOT else '❌'}\n"
    settings += f"• فارسی: {'✅' if LOCK_PERSIAN else '❌'}\n"
    settings += f"• انگلیسی: {'✅' if LOCK_ENGLISH else '❌'}\n"
    settings += f"• هشتگ: {'✅' if LOCK_HASHTAG else '❌'}\n"
    settings += f"• ریپلای: {'✅' if LOCK_REPLY else '❌'}\n"
    settings += f"• فحش: {'✅' if LOCK_SWEAR else '❌'}\n\n"

    settings += "⚙️ **تنظیمات پیشرفته:**\n"
    settings += f"• قفل خودکار: {'✅' if AUTO_LOCK else '❌'}\n"
    settings += f"• قفل گروه: {'✅' if GROUP_LOCK else '❌'}\n"
    settings += f"• حالت سختگیرانه: {'✅' if STRICT_MODE else '❌'}\n"
    settings += f"• فیلتر لینک: {'✅' if LINK_FILTER else '❌'}\n"
    settings += f"• خوشامدگویی: {'✅' if WELCOME_ENABLED else '❌'}\n"
    settings += f"• آنتی اسپم: {'✅' if ANTI_SPAM_ENABLED else '❌'}\n"
    settings += f"• سیستم امتیاز: {'✅' if SCORE_SYSTEM_ENABLED else '❌'}\n\n"

    settings += "🚫 **کلمات ممنوعه:**\n"
    all_banned = banned_words.copy()
    if STRICT_MODE:
        all_banned.extend(strict_banned_words)
    settings += "• " + "، ".join(all_banned) + "\n\n"

    settings += f"📜 **قوانین:**\n{GROUP_RULES}\n"

    send_message_simple(chat_id, settings)

def main():
    global active_groups, activation_time, ignored_messages
    
    offset = None
    
    active_groups = set()
    activation_time = {}
    ignored_messages = set()
    
    print("\n" + "="*60)
    print("🤖 بات یاور با قابلیت ارسال همگانی عکس و فیلم در حال اجراست...")
    print("="*60)

    print("\n👑 **ادمین‌های بازو:**")
    for admin_id in MASTER_ADMINS:
        print(f"   • {admin_id}")

    print("\n✨ **قابلیت‌های جدید:**")
    print("📸 **ارسال همگانی عکس**")
    print("🎬 **ارسال همگانی فیلم**")
    print("📄 **ارسال همگانی فایل**")
    print("🎮 **بازی‌ها:** بازی عدد، اسم فامیل، بازی کلمات، چیستان، مافیا، کلمات زنجیره‌ای، مسابقه")
    print("🔗 **مدیریت:** لینک دعوت، باطل لینک")
    print("🛡️ **امنیتی:** قفل‌های مختلف، آنتی اسپم، مجازات کاربران")

    print("\n📢 **ارسال همگانی:**")
    print("• به بات پی وی بدید")
    print("• از منو گزینه مورد نظر رو انتخاب کنید")
    print("• می‌توانید عکس، فیلم و فایل ارسال کنید")

    print("\n🎮 **بازی‌ها:**")
    print("• بازی عدد - بازی حدس عدد گروهی")
    print("• اسم فامیل - بازی اسم فامیل کلاسیک")

    print("\n🎯 **دستورات اصلی:**")
    print("• فعالسازی - فعالسازی بات در گروه (فقط ادمین)")
    print("• غیرفعالسازی - غیرفعالسازی بات در گروه (فقط ادمین)")
    print("• راهنما - دریافت راهنمای کامل")
    print("• بگو [متن] - تکرار متن")
    print("• لینک دعوت - ساخت لینک دعوت گروه")

    print("\n✅ **نکته مهم:** پیام‌های قبل از فعالسازی حتی بعد از فعالسازی هم جواب داده نمی‌شوند!")
    print("✅ **نکته مهم:** در آمار گروه، به جای آیدی عددی، نام کاربری یا اسم کاربر نمایش داده می‌شود!")
    print("✅ **نکته مهم:** کاربران عادی منوی متفاوتی نسبت به ادمین‌ها دارند!")
    print("\n✅ برای توقف: Ctrl + C")

    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                handle_new_members(update)
                handle_message(update)
                offset = update["update_id"] + 1
            time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n\n👋 بات متوقف شد!")
            break
        except Exception as e:
            logger.error(f"❌ خطا: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()