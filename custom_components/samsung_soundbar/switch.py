"""samsung Soundbar Switchs    """
import logging
import asyncio
import voluptuous as vol
from datetime import timedelta

from .api import SoundbarApi, SmartThingsError
from homeassistant.helpers.update_coordinator import CoordinatorEntity




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
    
    async_add_entities(devices, update_before_add=False)

class SoundbarSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, SoundbarSwitchEntity, mode):
        super().__init__(SoundbarSwitchEntity.coordinator)
        self._client = SoundbarSwitchEntity.client
        self._mode = mode
        self._api_mode = {"night_mode": "nightmode", "bass_boost": "bassboost", "voice_amplifier": "voiceamplifier"}[mode]
        self._name = SoundbarSwitchEntity.name + "_" + mode
        self._device_id = SoundbarSwitchEntity.device_id
        self._api_key = SoundbarSwitchEntity.api_key
        self._state = "off"
        self._attr_unique_id = f"{self._device_id}_{mode}"

    def _handle_coordinator_update(self):
        data = self.coordinator.data
        if data:
            advanced = data["advanced"]
            value = advanced.get(f"x.com.samsung.networkaudio.{self._api_mode}")
            self._state = "on" if value in (1, True, "1", "on") else "off"
        super()._handle_coordinator_update()

    async def async_turn_off(self, **kwargs):
        await self._client.set_advanced(self._api_mode, False)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        await self._client.set_advanced(self._api_mode, True)
        await self.coordinator.async_request_refresh()

    @property
    def name(self):
        return self._name


    @property
    def mode(self):
        return self._mode 
    
    @property
    def is_on(self):
        return self._state == "on"