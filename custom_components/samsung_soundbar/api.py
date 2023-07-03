import json
import time
import requests
import aiohttp
import asyncio
from homeassistant.const import (
    STATE_IDLE,
    STATE_OFF,
    STATE_ON,
    STATE_PAUSED,
    STATE_PLAYING,
)

API_BASEURL = "https://api.smartthings.com/v1"
API_DEVICES = API_BASEURL + "/devices/"

COMMAND_POWER_ON = (
    "{'commands': [{'component': 'main','capability': 'switch','command': 'on'}]}"
)
COMMAND_POWER_OFF = (
    "{'commands': [{'component': 'main','capability': 'switch','command': 'off'}]}"
)
COMMAND_REFRESH = (
    "{'commands':[{'component': 'main','capability': 'refresh','command': 'refresh'}]}"
)
COMMAND_PAUSE = "{'commands':[{'component': 'main','capability': 'mediaPlayback','command': 'pause'}]}"
COMMAND_MUTE = (
    "{'commands':[{'component': 'main','capability': 'audioMute','command': 'mute'}]}"
)
COMMAND_UNMUTE = (
    "{'commands':[{'component': 'main','capability': 'audioMute','command': 'unmute'}]}"
)
COMMAND_PLAY = "{'commands':[{'component': 'main','capability': 'mediaPlayback','command': 'play'}]}"
COMMAND_STOP = "{'commands':[{'component': 'main','capability': 'mediaPlayback','command': 'stop'}]}"
COMMAND_REWIND = "{'commands':[{'component': 'main','capability': 'mediaPlayback','command': 'rewind'}]}"
COMMAND_FAST_FORWARD = "{'commands':[{'component': 'main','capability': 'mediaPlayback','command': 'fastForward'}]}"

CONTROLABLE_SOURCES = ["bluetooth", "wifi"]


class SoundbarApi:
    async def async_update(self) -> None:
        #        try:

        await async_get_json(self,"post","commands",COMMAND_REFRESH)
        await async_get_json(self,"get","/states","")

        #        except requests.exceptions.RequestException as e:
        #            self._state = STATE_IDLE
        #            return e

        try:
            
            device_volume = data["main"]["volume"]["value"]
            device_volume = min(int(device_volume) / self._max_volume, 1)
            switch_state = data["main"]["switch"]["value"]
            playback_state = data["main"]["playbackStatus"]["value"]
            device_source = data["main"]["inputSource"]["value"]
            device_all_sources = json.loads(
                data["main"]["supportedInputSources"]["value"]
            )
            device_muted = data["main"]["mute"]["value"] != "unmuted"

            if switch_state == "on":
                if device_source in CONTROLABLE_SOURCES:
                    if playback_state == "playing":
                        self._state = STATE_PLAYING
                    elif playback_state == "paused":
                        self._state = STATE_PAUSED
                    else:
                        self._state = STATE_ON
                else:
                    self._state = STATE_ON
            else:
                self._state = STATE_OFF
            self._volume_level = device_volume
            self._source_list = (
                device_all_sources
                if type(device_all_sources) is list
                else device_all_sources["value"]
            )
            self._muted = device_muted
            self._source = device_source
            if (
                self._state in [STATE_PLAYING, STATE_PAUSED]
                and "trackDescription" in data["main"]
            ):
                self._media_title = data["main"]["trackDescription"]["value"]
            else:
                self._media_title = None


            API_FULL = "{'commands':[{'component': 'main','capability': 'execute','command': 'execute', 'arguments': ['/sec/networkaudio/soundmode']}]}"
        except:
            return

#        try:

        await async_get_json(self,"post","commands",API_FULL)
        await async_get_json(self,"get","components/main/capabilities/execute/status","")

#        except requests.exceptions.RequestException as e:
#            return 

        try:
            device_soundmode = data["data"]["value"]["payload"][
                "x.com.samsung.networkaudio.soundmode"
            ]
            device_soundmode_list = data["data"]["value"]["payload"][
                "x.com.samsung.networkaudio.supportedSoundmode"
            ]
            self._sound_mode = device_soundmode
            self._sound_mode_list = device_soundmode_list
        except Exception as error:
            return error

    async def async_send_command(self, argument, cmdtype):

        if cmdtype == "setvolume":  # sets volume
            API_COMMAND_DATA = "{'commands':[{'component': 'main','capability': 'audioVolume','command': 'setVolume','arguments': "
            volume = int(argument * self._max_volume)
            API_COMMAND_ARG = "[{}]}}]}}".format(volume)
            API_FULL = API_COMMAND_DATA + API_COMMAND_ARG
            await async_get_json(self,"post","commands",API_FULL)
        elif cmdtype == "stepvolume":  # steps volume up or down
            if argument == "up":
                API_COMMAND_DATA = "{'commands':[{'component': 'main','capability': 'audioVolume','command': 'volumeUp'}]}"
                await async_get_json(self,"post","commands",API_COMMAND_DATA)
            else:
                API_COMMAND_DATA = "{'commands':[{'component': 'main','capability': 'audioVolume','command': 'volumeDown'}]}"
                await async_get_json(self,"post","commands",API_COMMAND_DATA)
        elif cmdtype == "audiomute":  # mutes audio
            if self._muted == False:
                await async_get_json(self,"post","commands",COMMAND_MUTE)
            else:
                await async_get_json(self,"post","commands",COMMAND_UNMUTE)
        elif cmdtype == "switch_off":  # turns off
            await async_get_json(self,"post","commands",COMMAND_POWER_OFF)
        elif cmdtype == "switch_on":  # turns on
            await async_get_json(self,"post","commands",COMMAND_POWER_ON)
        elif cmdtype == "play":  # play
            await async_get_json(self,"post","commands",COMMAND_PLAY)
        elif cmdtype == "pause":  # pause
            await async_get_json(self,"post","commands",COMMAND_PAUSE)            
        elif cmdtype == "selectsource":  # changes source
            API_COMMAND_DATA = "{'commands':[{'component': 'main','capability': 'mediaInputSource','command': 'setInputSource', 'arguments': "
            API_COMMAND_ARG = "['{}']}}]}}".format(argument)
            API_FULL = API_COMMAND_DATA + API_COMMAND_ARG
            await async_get_json(self,"post","commands",API_FULL)
        elif cmdtype == "selectsoundmode":  # changes sound mode
            API_COMMAND_DATA = "{'commands':[{'component': 'main','capability': 'execute','command': 'execute', 'arguments': ['/sec/networkaudio/soundmode',{'x.com.samsung.networkaudio.soundmode':"
            API_COMMAND_ARG = "'{}'".format(argument)
            API_END = "}]}]}"
            API_FULL = API_COMMAND_DATA + API_COMMAND_ARG + API_END
            await async_get_json(self,"post","commands",API_FULL)

        self.async_schedule_update_ha_state()

################################################################
class SoundbarApiSwitch:
    
    async def async_update(self):
        request_headers = {"Authorization": "Bearer " + self._api_key}
        api_full = "{'commands':[{'component': 'main','capability': 'execute','command': 'execute', 'arguments': ['/sec/networkaudio/advancedaudio']}]}"

        #        try:
        await async_get_json(self,"post","commands",api_full)
        await async_get_json(self,"get","components/main/capabilities/execute/status","")

        #        except requests.exceptions.RequestException as e:
        #            return e
        try:
            
            if (
                data["data"]["value"]["payload"][
                    "x.com.samsung.networkaudio." + self._mode
                ]
                == 1
            ):
                self._state = STATE_ON
            else:
                self._state = STATE_OFF
        except Exception as error:
            return error

    async def async_send_command(self, cmdtype):

        API_COMMAND_DATA = "{'commands':[{'component': 'main','capability': 'execute','command': 'execute','arguments': ['/sec/networkaudio/advancedaudio',"


        if cmdtype == "switch_off":  # turns off self._mode
            API_COMMAND_ARG = "{'x.com.samsung.networkaudio."+ self._mode + "': 0 }]}]}"
            API_FULL = API_COMMAND_DATA + API_COMMAND_ARG
            await async_get_json(self,"post",api_command,API_FULL)

        elif cmdtype == "switch_on":  # turns on self._mode
            API_COMMAND_ARG = "{'x.com.samsung.networkaudio."+ self._mode + ": 1 }]}]}"
            API_FULL = API_COMMAND_DATA + API_COMMAND_ARG

            await async_get_json(self,"post","commands",API_FULL)

        self.async_schedule_update_ha_state()

async def async_get_json(self,method:str,command:str,data:str):
    request_headers = {"Authorization": "Bearer " + self._api_key}
    full_command = API_DEVICES + self._device_id + "/" + command
    

    if method == "post":
        async with self._opener.post(command, data=data, headers=request_headers) as resp:
            assert resp.status == 200
            return await resp.json()
    else:
        async with self._opener.get(command, headers=request_headers) as resp:
            assert resp.status == 200
            return await resp.json()

    



