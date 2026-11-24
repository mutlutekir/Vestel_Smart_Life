"""Constants for the Vestel Smart Life integration."""

DOMAIN = "vestel_smart_life"

AUTH_ENDPOINT = "https://hosted-kimlik.vestel.com.tr/oauth2/authorize"
TOKEN_ENDPOINT = "https://hosted-kimlik.vestel.com.tr/oauth2/token"
API_BASE = "https://sh-native-api.homevsmart.com"

# --- Sabit uygulama kimlik bilgileri -----------------------------------
# amplifyconfiguration.json (Vestel Akilli Yasam APK) icinden dogrulandi.
# Vestel bu degerleri degistirirse (Cognito App Client rotate edilirse):
#   1. Bu iki sabiti guncelle (yeni degerleri ayni yontemle - APK/mitmproxy - bul)
#   2. Home Assistant'ta entegrasyonu kaldirip yeniden ekle (yeni refresh_token gerekir)
APP_CLIENT_ID = "6tl8koi5fis9j7i3u3jnv15vr7"
APP_CLIENT_SECRET = "mc4j2r13mctk8u46poaic9snm83khk458c8a1uupk6sqoqar90c"
# -------------------------------------------------------------------------

DEFAULT_REDIRECT_URI = "evinakli://signin"
DEFAULT_SCAN_INTERVAL = 60  # seconds

# Confirmed from the app's own amplifyconfiguration.json (AWS Amplify Auth config).
DEFAULT_SCOPES = "profile phone openid email aws.cognito.signin.user.admin"

CONF_REDIRECT_URI = "redirect_uri"
CONF_REFRESH_TOKEN = "refresh_token"

# Vestel's ACGENSI code packs mode (bits 0-2) and fan (bits 3-5) together:
#   ACGENSI = ACCMODE + FanSpeed * 8
# Confirmed against the app's own APK-derived docs AND real device captures.
MODE_MAP = {"auto": 0, "cool": 1, "dry": 2, "fan": 3, "heat": 4, "off": 5}
MODE_NAME = {0: "auto", 1: "cool", 2: "dry", 3: "fan", 4: "heat", 5: "off"}

FAN_MAP = {"auto": 0, "fan1": 1, "fan2": 2, "fan3": 3, "fan4": 4, "fan5": 5}
FAN_NAME = {0: "auto", 1: "fan1", 2: "fan2", 3: "fan3", 4: "fan4", 5: "fan5"}

# ACTEMOT encodes target temperature as temp + 32736
TEMP_OFFSET = 32736
MIN_TEMP = 18
MAX_TEMP = 30

# --- ACFANPO: packed toggles + louver positions -------------------------
# Confirmed bit-for-bit against real device captures (see README "Deşifre
# edilen kodlar" table):
#   bit 0    = Turbo            (+1)
#   bits 1-3 = Vertical louver  (0=durdur, 1-5=sabit kademe, 6=salınım)
#   bits 4-6 = Horizontal louver - encoding NOT confirmed on a real unit,
#              so these bits are only read and preserved, never written.
#   bit 7    = Sleep            (+128)
#   bit 8    = Ionizer          (+256)
#   bit 9    = Eco / Tasarruf   (+512)
FANPO_TURBO_BIT = 1
FANPO_VERTICAL_SHIFT = 1
FANPO_HORIZONTAL_SHIFT = 4
FANPO_LOUVER_MASK = 0x7
FANPO_SLEEP_BIT = 128
FANPO_IONIZER_BIT = 256
FANPO_ECO_BIT = 512

LOUVER_OPTIONS = {
    "durdur": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "salinim": 6,
}
LOUVER_OPTION_NAMES = {v: k for k, v in LOUVER_OPTIONS.items()}

# --- ACOFFTV: auto-off (delayed shutdown) target clock time -------------
# bits 0-4 = Hour (5 bits), bits 5-10 = Minute (6 bits), 2047 ("02047") = disabled.
# Confirmed against a real capture: 14:18 -> 00590.
OFFTV_DISABLED = 2047

# AWS IoT live updates. Public values from the Smart Life app's own configuration
# (res/raw/amplifyconfiguration.json); see docs/protocol.md.
AWS_REGION = "eu-west-1"
AWS_IDENTITY_POOL_ID = "eu-west-1:bb1ff9a2-6db0-4f3f-b630-62a9fc3bfbda"
AWS_USER_POOL_PROVIDER = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_EgDdXOayO"
AWS_IOT_HOST = "aa8u5ipzaqyfu-ats.iot.eu-west-1.amazonaws.com"

# --- Refrigerators (device type "RF") -------------------------------------
# Packing taken from the Smart Life app (RFCloudEntityToCloudDomain /
# RFCloudDomainToCloudEntity) and its bundled sample documents (demo_rf.json).
DEVICE_TYPE_AC = "AC"
DEVICE_TYPE_FRIDGE = "RF"
# Other families (washing machine, washer-dryer, tumble dryer, dishwasher, oven, fridge-freezer):
# read only, see appliances.py.
APPLIANCE_TYPES = ("WM", "WD", "TD", "DW", "OV", "FD")
LEGACY_DEVICE_TYPES = (DEVICE_TYPE_FRIDGE, *APPLIANCE_TYPES)  # state comes from the register endpoint
SUPPORTED_DEVICE_TYPES = (DEVICE_TYPE_AC, *LEGACY_DEVICE_TYPES)
# Seconds between status requests for devices that are not air conditioners.
LEGACY_POLL_SECONDS = 30

# RFTEMSE = (cooler degrees C << 8) | abs(freezer degrees C). The values below are
# the ones the app's sample document offers; a unit may allow fewer.
FRIDGE_COOLER_TEMPS = (2, 4, 5, 6, 8)
FRIDGE_FREEZER_TEMPS = (-16, -18, -20, -22, -24)

# RFMODEA holds one mode at a time (the app compares for equality). The sample
# document of one model lists only some of them; the app can send all of these.
FRIDGE_MODES = {
    0: "Normal",
    2: "Süper Dondurma",
    4: "Süper Soğutma",
    8: "Tatil",
    16: "Ekonomi",
    32: "Yapay Zeka",
}
FRIDGE_DOOR_CLOSED = 3  # RFDOORA: the app treats every other value as "open"
