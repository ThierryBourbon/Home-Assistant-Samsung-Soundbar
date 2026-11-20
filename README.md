[![HACS Custom][hacs_shield]][hacs]
[![GitHub Latest Release][releases_shield]][latest_release]
[![GitHub All Releases][downloads_total_shield]][releases]
[![Buy me a coffee][buy_me_a_coffee_shield]][buy_me_a_coffee]


[hacs_shield]: https://img.shields.io/static/v1.svg?label=HACS&message=Custom&style=popout&color=orange&labelColor=41bdf5&logo=HomeAssistantCommunityStore&logoColor=white
[hacs]: https://hacs.xyz/docs/faq/custom_repositories

[latest_release]: https://github.com/ThierryBourbon/Home-Assistant-Samsung-Soundbar/releases/latest
[releases_shield]:https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FThierryBourbon%2FHome-Assistant-Samsung-Soundbar%2Fmaster%2Fcustom_components%2Fsamsung_soundbar%2Fmanifest.json&query=%24.version&label=release



[releases]: https://github.com/ThierryBourbon/Home-Assistant-custom-components-samsung-Soundbar/releases/latest
[downloads_total_shield]: https://img.shields.io/github/downloads/ThierryBourbon/Home-Assistant-Samsung-Soundbar/total


[buy_me_a_coffee_shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white
[buy_me_a_coffee]: https://www.buymeacoffee.com/thierrybourbon




> **Development branch (2.2.0-beta.1): not yet validated on physical hardware.**
> This branch replaces blocking SmartThings HTTP calls with asynchronous requests and
> shares one polling coordinator between the media player and the three switches.
> Do not install it over a working setup without first backing up
> `custom_components/samsung_soundbar` and your Home Assistant configuration.
> The existing `samsung_soundbar: devices:` YAML configuration remains supported.
> The integration requires network access to `api.smartthings.com` and a valid SmartThings token.
> It is not a local LAN integration; its functionality depends on the Samsung cloud API.

# samsung Soundbar

Adds support for samsung enabled Soundbar

## Features

- Turn on/off
- Set volume
- Step volume up/down
- Mute/unmute
- Select source
- Select soundmode
- Show current volume level
- Show current state: on/off/playing/paused/idle
- Show if muted/unmuted
- Show current source
- `Extra switchs: Voice_amplifier, Bass Boost, Night Mode`

## Configuration options

| Key          | Type               | Required | Default                | Description                                                                                                                                               |
| -------------- | -------------------- | ---------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`       | `string`           | `False`  | `samsung Soundbar` | Name of soundbar                                                                                                                                          |
| `api_key`    | `string`           | `True`   | -                      | samsung API key (see:[here](https://github.com/PiotrMachowski/Home-Assistant-custom-components-samsung-Soundbar#getting-api-key-and-device-id))   |
| `device_id`  | `string`           | `True`   | -                      | samsung device id (see:[here](https://github.com/PiotrMachowski/Home-Assistant-custom-components-samsung-Soundbar#getting-api-key-and-device-id)) |
| `max_volume` | `positive integer` | `False`  | 100                    | Volume level that will be used as a maximum level in Home Assistant                                                                                       |

## Examples usage

```yaml
samsung_soundbar:
  devices:
    - name: Barre de son
      api_key: b13391c7-8cef-4518-a58e-393b0xxxxxxx
      device_id: da93855b-45cd-6ca0-86d6-2c957xxxxxx
      max_volume: 100
```
If you want you can customise switch names to your language
```yaml
homeassistant:
  customize:
    switch.barre_de_son_night_mode:
      friendly_name: "Mode Nuit"
    switch.barre_de_son_bass_boost:
      friendly_name: "Amélioration des Basses"
    switch.barre_de_son_voice_amplifier:
      friendly_name: "Amélioration Vocale"
```

## Device

this integration creates a device
composed of a media player and 3 switches
- bass_boost
- Night_mode
- voice_amplifier

You can group them on an entities card


![entities_card](https://github.com/ThierryBourbon/Home-Assistant-Samsung-Soundbar/assets/65720627/ca36d296-7669-4fa6-9f3e-7a30757984d4)




## Getting API key and device id

Make sure your device is connected to yout samsung account.

Obtain an API key from https://account.samsung.com/tokens

Go [here](https://graph-eu01-euwest1.api.samsung.com/device/list) for your device id for each device. Click on the name of your device and the device id will be in the URL

> https://graph-eu01-euwest1.api.samsung.com/device/show/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXX

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

This integration can be added to HACS as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories):
* URL: `https://github.com/ThierryBourbon/Home-Assistant-Samsung-Soundbar
* Category: `Integration`

### Manual

To install this integration manually you have to download [*samsung_soundbar.zip*](https://github.com/ThierryBourbon/Home-Assistant-custom-components-samsung-Soundbar/blob/master/samsung_soundbar.zip) and extract its contents to `config/custom_components/samsung_soundbar` directory:

```bash
mkdir -p custom_components/samsung_soundbar
cd custom_components/samsung_soundbar
wget https://github.com/ThierryBourbon/Home-Assistant-custom-components-samsung-Soundbar/blob/master/samsung_soundbar.zip
unzip samsung_soundbar.zip
rm samsung_soundbar.zip
```

### Known problems

* If you have config validation issues after installing this component you have to follow these steps:
  * Install custom component
  * Restart Home Assistant
  * Add configuration
  * Restart Home Assistant again

## Supported devices

This integration was confirmed to work with following devices:

- Samsung HW-N950
- Samsung HW-Q800T
- Samsung HW-Q950T
- Samsung HW-Q990B
- Samsung HW-Q90R
- Samsung HW-Q80R
- Samsung HW-Q70R
- Samsung HW-S60T
- Samsung HW-S61T
- Samsung HW-Q930B