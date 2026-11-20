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
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
from .api import SoundbarApi, SmartThingsError

# DEFAULTS
DEFAULT_NAME = "Samsung Soundbar"
CONF_MAX_VOLUME = "max_volume"

soundbar_CONFIG = vol.Schema(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_MAX_VOLUME, default=100): cv.positive_int,
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
                        vol.Optional(CONF_MAX_VOLUME, default=100): cv.positive_int,
                }),
            ]),
        })
}, extra=vol.ALLOW_EXTRA)



async def async_setup(hass, config):
    """Initialize the Smarttings Soundbar device."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = []

    _LOGGER.warning("SOUNDBAR DIAG 01: async_setup entered; configured=%s", DOMAIN in config)

    soundbar_list = []

    configured_devices = config.get(DOMAIN, {}).get(CONF_DEVICES, [])
    for device in configured_devices:
        soundbar = SoundbarDevice(
            device.get(CONF_API_KEY),
            device.get(CONF_DEVICE_ID),
            device.get(CONF_NAME),
            device.get(CONF_MAX_VOLUME)
        )
 
        _LOGGER.debug("soundbar device %s configured", device.get(CONF_NAME))
        soundbar.client = SoundbarApi(async_get_clientsession(hass), soundbar.api_key, soundbar.device_id, soundbar.max_volume)
        soundbar.coordinator = SoundbarCoordinator(hass, soundbar)
        soundbar_list.append(soundbar)

    hass.data[DOMAIN] = soundbar_list

    if not soundbar_list:
        _LOGGER.info("No soundbar devices configured")
        return True

    _LOGGER.warning("SOUNDBAR DIAG 02: configured %s soundbar(s)", len(soundbar_list))

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
        self.client = None
        self.coordinator = None
    
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
    
    








                

class SoundbarCoordinator(DataUpdateCoordinator):
    """Share a single SmartThings update among all soundbar entities."""

    def __init__(self, hass, soundbar):
        super().__init__(
            hass,
            _LOGGER,
            name=f"samsung_soundbar_{soundbar.device_id}",
            update_interval=timedelta(seconds=120),
        )
        self.soundbar = soundbar

    async def _async_update_data(self):
        _LOGGER.warning("SOUNDBAR DIAG 03: coordinator polling started")
        try:
            media = await self.soundbar.client.update_media()
            _LOGGER.warning("SOUNDBAR DIAG 04: media fetched")
            advanced = await self.soundbar.client.update_advanced()
            _LOGGER.warning("SOUNDBAR DIAG 05: advanced audio fetched")
            return {"media": media, "advanced": advanced}
        except Exception as error:
            _LOGGER.exception("Samsung Soundbar: SmartThings update failed for device %s (%s)", self.soundbar.device_id, type(error).__name__)
            raise UpdateFailed(f"{type(error).__name__}: {error}") from error
