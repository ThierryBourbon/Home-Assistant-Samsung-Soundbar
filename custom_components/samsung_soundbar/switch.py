"""samsung Soundbar Switchs    """
import logging
import asyncio
import aiohttp
import voluptuous as vol
from datetime import timedelta

from .api import SoundbarApiSwitch




# From homeassistant
from custom_components.samsung_soundbar import _LOGGER, DOMAIN as SOUNDBAR_DOMAIN
from homeassistant.components.switch import (
    SwitchEntity,
)

import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

# VERSION
VERSION = "2.1"

# Dependencies
DEPENDENCIES = ["soundbar"]

# DEFAULTS
MODE_LIST = [ "nightmode", "bassboost", "voiceamplifier"]

# GLOBALS
mode_courant =""

# Return cached results if last scan was less then this time ago.
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=10)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=5)


# SETUP PLATFORM
async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up platform."""
    """Initialize the Soundbar device."""
    devices = []
    soundbar_list = hass.data[SOUNDBAR_DOMAIN]

    for device in soundbar_list:
        _LOGGER.debug("Configured a new SoundbarSwitch %s", device.name)
        for m in MODE_LIST:

            global mode_courant
            mode_courant = m
            devices.append(SoundbarSwitch (device))
    
    async_add_entities(devices, update_before_add=True)

class SoundbarSwitch  (SwitchEntity):
    def __init__(self, SoundbarSwitchEntity):

        global mode_courant
        self._mode = mode_courant
        self._name = SoundbarSwitchEntity.name + "_" + mode_courant
        self._device_id = SoundbarSwitchEntity.device_id
        self._api_key = SoundbarSwitchEntity.api_key
        self._state = "off"
        self._opener = SoundbarSwitchEntity.get_opener
        

    # Run when added to HASS TO LOAD SOURCES
    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()


    async def async_update(self) -> None:
        await SoundbarApiSwitch.async_update(self)

    async def async_turn_off(self) -> None:
        await SoundbarApiSwitch.async_send_command(self, "switch_off")

    async def async_turn_on(self) -> None:
        await SoundbarApiSwitch.async_send_command(self, "switch_on")

    @property
    def name(self):
        return self._name


    @property
    def mode(self):
        return self._mode 
    
    @property
    def state(self):
        return self._state