"""samsung Soundbar Switchs    """
import logging
import asyncio
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
MODE_LIST = [ "night_mode", "bass_boost", "voice_amplifier"]

# GLOBALS


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

            devices.append(SoundbarSwitch(device, m))
    
    async_add_entities(devices, update_before_add=True)

class SoundbarSwitch  (SwitchEntity):
    def __init__(self, SoundbarSwitchEntity, mode):
        self._mode = mode
        self._name = SoundbarSwitchEntity.name + "_" + mode
        self._device_id = SoundbarSwitchEntity.device_id
        self._api_key = SoundbarSwitchEntity.api_key
        self._state = "off"

    # Run when added to HASS TO LOAD SOURCES
    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()


    def update(self):
        SoundbarApiSwitch.device_update(self)

    def turn_off(self):
        arg = ""
        cmdtype = "switch_off"
        SoundbarApiSwitch.send_command(self, arg, cmdtype)

    def turn_on(self):
        arg = ""
        cmdtype = "switch_on"
        SoundbarApiSwitch.send_command(self, arg, cmdtype)

    @property
    def name(self):
        return self._name


    @property
    def mode(self):
        return self._mode 
    
    @property
    def is_on(self):
        return self._state == "on"