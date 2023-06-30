"""samsung Soundbar"""
import logging
import voluptuous as vol

# VERSION
VERSION = '2.1'

# REQUIREMENTS
REQUIREMENTS = ['beautifulsoup4==4.6.3']

# LOGGING
_LOGGER = logging.getLogger(__name__)

# DOMAIN
DOMAIN = 'samsung_soundbar'

# Supported domains
SUPPORTED_DOMAINS = ['media_player','switch']

from homeassistant.const import CONF_DEVICES, CONF_NAME, CONF_API_KEY, CONF_DEVICE_ID
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.entity import Entity

# DEFAULTS
DEFAULT_NAME = "samsung Soundbar Test"
CONF_MAX_VOLUME = "max_volume"

soundbar_CONFIG = vol.Schema(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_MAX_VOLUME, default=1): cv.positive_int,
    }
)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES):
            vol.All(cv.ensure_list, [
                vol.Schema({
                        vol.Required(CONF_API_KEY): cv.string,
                        vol.Required(CONF_DEVICE_ID): cv.string,
                        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                        vol.Optional(CONF_MAX_VOLUME, default=1): cv.positive_int,
                }),
            ]),
        })
}, extra=vol.ALLOW_EXTRA)



async def async_setup(hass, config):
    """Initialize the Smarttings Soundbar device."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = []

    _LOGGER.info("Initializing Samsung Soundbar  devices")

    soundbar_list = []

    configured_devices = config[DOMAIN].get(CONF_DEVICES)
    for device in configured_devices:
        soundbar = SoundbarDevice(
            device.get(CONF_API_KEY),
            device.get(CONF_DEVICE_ID),
            device.get(CONF_NAME),
            device.get(CONF_MAX_VOLUME)
        )
 
        _LOGGER.debug("soundbar device %s configured", device.get(CONF_NAME))
        soundbar_list.append(soundbar)

    hass.data[DOMAIN] = soundbar_list

    if not soundbar_list:
        _LOGGER.info("No soundbar devices configured")
        return False

    _LOGGER.debug("Configured %s soundbars", len(soundbar_list))

    for domain in SUPPORTED_DOMAINS:
        hass.async_create_task(
            discovery.async_load_platform(hass, domain, DOMAIN, {}, config))
    return True

class SoundbarDevice(Entity):
    """Representation of a soundbar device."""

    def __init__(self, api_key, device_id, name, max_volume):
        """Initialize the Soundbar device."""
        self._name = name
        self._device_id = device_id
        self._api_key = api_key
        self._max_volume = max_volume
        self._volume = 1
        self._muted = False
        self._playing = True
        self._state = "on"
        self._source = ""
        self._source_list = []
        self._sound_mode = "standard"
        self._sound_mode_list = []
        self._media_title = ""
        self._opener = aiohttp.ClientSession()
    
#    @property
#    def device_class(self):
#        return DEVICE_CLASS_SPEAKER

#    @property
#    def supported_features(self):
#        return SUPPORT_samsung_SOUNDBAR

    @property
    def name(self):
        return self._name

    @property
    def device_id(self):
        return self._device_id

    @property
    def api_key(self):
        return self._api_key

    @property
    def media_title(self):
        return self._media_title
    
    @property
    def max_volume(self):
        return self._max_volume
    
    @property
    def get_opener(self):
        """Return the socket of the device."""
        return self._opener

    
    








                