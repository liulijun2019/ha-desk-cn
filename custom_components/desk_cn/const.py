"""Constants for the desk_cn integration."""
from homeassistant.const import Platform

DOMAIN = "desk_cn"
PLATFORMS = [Platform.COVER, Platform.NUMBER]

CONF_BASE_URL = "base_url"
CONF_API_KEY = "api_key"
CONF_ACCOUNT = "account"
CONF_PASSWORD = "password"
CONF_POLL_INTERVAL = "poll_interval"

DEFAULT_POLL_INTERVAL = 10  # seconds

# 升降桌高度范围（厘米）
DESK_HEIGHT_MIN = 72
DESK_HEIGHT_MAX = 120
