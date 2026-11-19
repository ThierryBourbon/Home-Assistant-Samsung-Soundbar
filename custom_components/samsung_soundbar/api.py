"""Asynchronous SmartThings API client for Samsung soundbars."""
import asyncio
import json
import logging

from aiohttp import ClientError, ClientSession, ClientTimeout
from homeassistant.const import STATE_OFF, STATE_ON, STATE_PAUSED, STATE_PLAYING

_LOGGER = logging.getLogger(__name__)
BASE_URL = "https://api.smartthings.com/v1/devices"
CONTROLLABLE_SOURCES = {"bluetooth", "wifi"}
TIMEOUT = ClientTimeout(total=12)


class SmartThingsError(Exception):
    """Raised when a SmartThings request fails."""


class SoundbarApi:
    """Per-device async SmartThings client."""

    def __init__(self, session: ClientSession, api_key: str, device_id: str, max_volume: int):
        self.session = session
        self.api_key = api_key
        self.device_id = device_id
        self.max_volume = max_volume
        self._command_lock = asyncio.Lock()

    async def _request(self, method: str, path: str, payload=None):
        url = f"{BASE_URL}/{self.device_id}{path}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with self.session.request(
                method, url, headers=headers, json=payload, timeout=TIMEOUT
            ) as response:
                response.raise_for_status()
                if response.status == 204:
                    return {}
                return await response.json(content_type=None)
        except (ClientError, asyncio.TimeoutError, ValueError) as error:
            raise SmartThingsError(f"SmartThings {method} {path}: {error}") from error

    async def command(self, capability: str, command: str, arguments=None):
        body = {"commands": [{
            "component": "main",
            "capability": capability,
            "command": command,
            **({"arguments": arguments} if arguments is not None else {}),
        }]}
        async with self._command_lock:
            return await self._request("POST", "/commands", body)

    async def execute(self, path: str, values=None):
        args = [path] if values is None else [path, values]
        return await self.command("execute", "execute", args)

    async def execute_status(self):
        return await self._request(
            "GET", "/components/main/capabilities/execute/status"
        )

    @staticmethod
    def _payload(data):
        return data["data"]["value"]["payload"]

    async def _execute_payload(self, path):
        # Serialize execute/status pairs: SmartThings exposes one shared status.
        async with self._command_lock:
            await self._request("POST", "/commands", {"commands": [{
                "component": "main", "capability": "execute",
                "command": "execute", "arguments": [path],
            }]})
            await asyncio.sleep(0.2)
            return self._payload(await self.execute_status())

    async def update_media(self):
        await self.command("refresh", "refresh")
        await asyncio.sleep(0.2)
        data = (await self._request("GET", "/states"))["main"]
        value = lambda key: data[key]["value"]
        sources = value("supportedInputSources")
        if isinstance(sources, str):
            sources = json.loads(sources)
        if isinstance(sources, dict):
            sources = sources.get("value", [])
        source = value("inputSource")
        power = value("switch")
        playback = value("playbackStatus")
        state = STATE_OFF if power != "on" else STATE_ON
        if power == "on" and source in CONTROLLABLE_SOURCES:
            if playback == "playing":
                state = STATE_PLAYING
            elif playback == "paused":
                state = STATE_PAUSED
        result = {
            "state": state,
            "volume": min(max(int(value("volume")) / self.max_volume, 0), 1),
            "muted": value("mute") != "unmuted",
            "source": source,
            "sources": sources,
            "title": data.get("trackDescription", {}).get("value")
            if state in (STATE_PLAYING, STATE_PAUSED) else None,
        }
        modes = await self._execute_payload("/sec/networkaudio/soundmode")
        result["sound_mode"] = modes.get("x.com.samsung.networkaudio.soundmode")
        result["sound_modes"] = modes.get("x.com.samsung.networkaudio.supportedSoundmode", [])
        return result

    async def update_advanced(self):
        return await self._execute_payload("/sec/networkaudio/advancedaudio")

    async def set_advanced(self, key: str, enabled: bool):
        await self.execute(
            "/sec/networkaudio/advancedaudio",
            {f"x.com.samsung.networkaudio.{key}": int(enabled)},
        )

    async def send_media_command(self, cmdtype: str, argument=None):
        if cmdtype == "setvolume":
            await self.command("audioVolume", "setVolume", [int(argument * self.max_volume)])
        elif cmdtype == "stepvolume":
            await self.command("audioVolume", "volumeUp" if argument == "up" else "volumeDown")
        elif cmdtype == "audiomute":
            await self.command("audioMute", "mute" if argument else "unmute")
        elif cmdtype == "switch_on":
            await self.command("switch", "on")
        elif cmdtype == "switch_off":
            await self.command("switch", "off")
        elif cmdtype in ("play", "pause"):
            await self.command("mediaPlayback", cmdtype)
        elif cmdtype == "selectsource":
            await self.command("mediaInputSource", "setInputSource", [argument])
        elif cmdtype == "selectsoundmode":
            await self.execute(
                "/sec/networkaudio/soundmode",
                {"x.com.samsung.networkaudio.soundmode": argument},
            )
        else:
            raise ValueError(f"Unknown soundbar command: {cmdtype}")
