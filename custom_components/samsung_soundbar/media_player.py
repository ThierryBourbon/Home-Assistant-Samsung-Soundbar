"""samsung Soundbar MediaPlayer    """
import logging
import asyncio
import voluptuous as vol
from datetime import timedelta

# vol.Required(CONF_DEVICE_ID): cv.string,

from .api import SoundbarApi, SmartThingsError
from homeassistant.helpers.update_coordinator import CoordinatorEntity

# From homeassistant
from custom_components.samsung_soundbar import _LOGGER, DOMAIN as SOUNDBAR_DOMAIN
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerDeviceClass,
    MediaPlayerEntityFeature,
)

import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

# VERSION
VERSION = "2.1"

# Dependencies


# Return cached results if last scan was less then this time ago.
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=10)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=5)

SUPPORT_samsung_SOUNDBAR = (
    MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.SELECT_SOUND_MODE
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.PLAY
)

# SETUP PLATFORM
async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up platform."""
    """Initialize the Soundbar device."""
    devices = []
    soundbar_list = hass.data[SOUNDBAR_DOMAIN]

    for device in soundbar_list:
        _LOGGER.debug("Configured a new SoundbarMediaPlayer %s", device.name)

        devices.append(SoundbarMediaPlayer(device))

    if soundbar_list:
        await asyncio.gather(*(device.coordinator.async_refresh() for device in soundbar_list))
    async_add_entities(devices, update_before_add=False)


# samsung Soundbar Media Player Devic


class SoundbarMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    def __init__(self, SoundbarMediaPlayerEntity):
        """Initialize the Soundbar device."""
        super().__init__(SoundbarMediaPlayerEntity.coordinator)
        self._client = SoundbarMediaPlayerEntity.client
        self._name = SoundbarMediaPlayerEntity.name
        self._device_id = SoundbarMediaPlayerEntity.device_id
        self._api_key = SoundbarMediaPlayerEntity.api_key
        self._max_volume = SoundbarMediaPlayerEntity.max_volume
        self._volume = 1
        self._muted = False
        self._playing = True
        self._state = "off"
        self._source = ""
        self._source_list = []
        self._sound_mode = "standard"
        self._sound_mode_list = []
        self._media_title = ""
        self._attr_unique_id = f"{self._device_id}_media_player"
        if self.coordinator.data:
            self._apply_media_data(self.coordinator.data["media"])

    def _handle_coordinator_update(self):
        if self.coordinator.data:
            self._apply_media_data(self.coordinator.data["media"])
        super()._handle_coordinator_update()

    def _apply_media_data(self, media):
        self._state = media["state"]
        self._volume = media["volume"]
        self._muted = media["muted"]
        self._source = media["source"]
        self._source_list = media["sources"]
        self._media_title = media["title"]
        self._sound_mode = media["sound_mode"]
        self._sound_mode_list = media["sound_modes"]

    async def _send(self, command, argument=None):
        await self._client.send_media_command(command, argument)
        await self.coordinator.async_request_refresh()

    ################################## Commandes ###############################
    ### arg , cmdtype

    async def async_turn_off(self):
        await self._send("switch_off")

    async def async_turn_on(self):
        await self._send("switch_on")

    async def async_set_volume_level(self, volume_level: float):
        await self._send("setvolume", volume_level)

    async def async_mute_volume(self, mute: bool):
        await self._send("audiomute", mute)

    async def async_volume_up(self):
        await self._send("stepvolume", "up")

    async def async_volume_down(self):
        await self._send("stepvolume", "down")

    async def async_select_source(self, source: str):
        await self._send("selectsource", source)

    async def async_select_sound_mode(self, sound_mode: str):
        await self._send("selectsoundmode", sound_mode)

    async def async_media_play(self):
        await self._send("play")

    async def async_media_pause(self):
        await self._send("pause")

    ################################## Attributs ###############################

    @property
    def device_class(self):
        return MediaPlayerDeviceClass.SPEAKER

    @property
    def supported_features(self):
        return SUPPORT_samsung_SOUNDBAR

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
    def state(self):
        return self._state

    @property
    def is_volume_muted(self):
        return self._muted

    @property
    def volume_level(self):
        return self._volume

    @property
    def source(self):
        return self._source

    @property
    def source_list(self):
        return self._source_list

    @property
    def sound_mode(self):
        return self._sound_mode

    @property
    def sound_mode_list(self):
        return self._sound_mode_list
