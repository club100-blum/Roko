# Available modes:
# - "lazy"           (uses accounts from running telegram.exe proccess on your PC. No configuration needed)
# - "pyrogram"
# - "telethon"
# - "telethon+json"  (uses api_id, api_hash, sdk version, etc. from json file)

MODE = 'telethon'


# api id, hash
# You can get it here: https://my.telegram.org/
# Used only in "telethon", "pyrogram" modes
API_ID: int = 1488
API_HASH: str = 'abc'

DELAYS = {
    'ACCOUNT':    [1, 2],       # delay between connections to accounts (the more accounts, the longer the delay)
    'PLAY':       [5, 15],      # delay between play in seconds
    'ERROR_PLAY': [60, 180],    # delay between errors in the game in seconds
}


# Use proxies or not
# Paste proxies to data/proxy.txt
PROXY = False

# dataimpulse.com proxies (cheap rotating proxies).
# Automatically gets proxy of phone's country
# Works only with mode telethon+json, where session files in format "<phone_number>.session"
DATAIMPULSE = False
DI_LOGIN =    ''
DI_PASSWORD = ''

# Session folder (do not change)
WORKDIR = "sessions/"

# Iteration duration in seconds, 1 hour = 60 * 60
ITERATION_DURATION = 60 * 60

# Threads/Workers count
ACCOUNT_PER_ONCE = 10

REFERRAL_COUNT = 5

# Don't change this, if you don't know what you are doing
DATABASE_URL = "sqlite+aiosqlite:///accounts.db"
APP_VERSION = '1.0.2'
