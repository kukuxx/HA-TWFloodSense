import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv

from .coordinator import FloodSenseCoordinator
from .const import (
    CONF_STATION_NAME,
    CONF_STATION_CODE,
    CONF_STATION_ID,
    CONF_THING_ID,
    DOMAIN,
    FLOODSENSE_COORDINATOR,
    HA_USER_AGENT,
    THING_DATA_API_URL,
    PLATFORM,
)

CONFIG_SCHEMA = cv.removed(DOMAIN, raise_if_present=True)
_LOGGER = logging.getLogger(__name__)


def _get_floodsense_from_entry(entry: ConfigEntry) -> dict[str, Any]:
    """Get flood sense data from config entry subentries."""
    # 確保 subentries 存在且可用
    if not hasattr(entry, 'subentries') or not entry.subentries:
        return {}

    station_codes = [
        subentry.data[CONF_STATION_CODE]
        for subentry in entry.subentries.values() 
        if subentry.data and subentry.data.get(CONF_STATION_CODE)
    ]
    station_ids = [
        subentry.data[CONF_STATION_ID]
        for subentry in entry.subentries.values() 
        if subentry.data and subentry.data.get(CONF_STATION_ID)
    ]
    return station_codes, station_ids


async def _async_setup_subentries(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up subentries for the config entry.

    Returns True if platforms were loaded, False otherwise.
    """
    config_data = hass.data[DOMAIN][entry.entry_id]

    station_codes, station_ids = _get_floodsense_from_entry(entry)

    # 創建 coordinators
    if station_codes and station_ids:
        floodsense_coordinator = FloodSenseCoordinator(hass, station_codes, station_ids)
        # 初始刷新
        await floodsense_coordinator.async_config_entry_first_refresh()
        config_data[FLOODSENSE_COORDINATOR] = floodsense_coordinator
        # 初始化感測器平台
        platforms_loaded = False
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORM)
        platforms_loaded = True

    _LOGGER.debug(
            "Setting up TWFloodSense with stations: %s",
            station_codes,
        )

    return platforms_loaded
    

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up global services for TWFloodSense."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TWFloodSense from a config entry."""
    try:
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
            "platforms_loaded": False,
        }
        platforms_loaded = await _async_setup_subentries(hass, entry)
        hass.data[DOMAIN][entry.entry_id]["platforms_loaded"] = platforms_loaded
        # 註冊更新監聽器
        entry.async_on_unload(entry.add_update_listener(update_listener))
        return True
    except Exception as e:
        _LOGGER.error("async_setup_entry error: %s", e)
        return False


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    try:
        await hass.config_entries.async_reload(entry.entry_id)
    except Exception as e:
        _LOGGER.error("update_listener error: %s", e)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        domain_data = hass.data.get(DOMAIN, {})
        entry_data = domain_data.get(entry.entry_id, {})
        platforms_loaded = entry_data.get("platforms_loaded", False)

        if platforms_loaded:
            unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORM)
            
            if not unload_ok:
                return False

        # 從 hass.data 中移除 entry 相關數據
        if entry.entry_id in domain_data:
            domain_data.pop(entry.entry_id)

        # 如果沒有其他 entry,移除整個 DOMAIN
        if DOMAIN in hass.data and not domain_data:
            hass.data.pop(DOMAIN)
            _LOGGER.debug("Removed %s from hass.data", DOMAIN)

        return True
    except Exception as e:
        _LOGGER.error("async_unload_entry error: %s", e)
        return False


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entry."""
    _LOGGER.debug(
        "Migrating configuration from version %s",
        entry.version,
    )

    # 未來版本無法處理
    if entry.version > 2:
        _LOGGER.error("Cannot migrate from future version")
        return False
    
    try:
        if entry.version == 1:
            from copy import deepcopy
            
            for subentry in entry.subentries.values():
                new_data = deepcopy(dict(subentry.data))
                new_data.pop(CONF_THING_ID, None)

                station_id = await _get_station_id(hass, new_data[CONF_STATION_CODE])
                new_data[CONF_STATION_ID] = station_id
                hass.config_entries.async_update_subentry(
                    entry,
                    subentry, 
                    data=new_data,
                    title=f"{new_data[CONF_STATION_NAME]}({new_data[CONF_STATION_CODE]})",
                    unique_id=new_data[CONF_STATION_CODE],
                )
                _LOGGER.debug(
                    "Migrated subentry %s to version 2",
                    subentry.subentry_id,
                )
            return True
    except Exception as e:
        _LOGGER.error("Migration error: %s", e)
        return False
                    

async def _get_station_id(hass: HomeAssistant, station_code: str) -> str:
    """Get station ID from station code."""
    client = get_async_client(hass, False)
    url = THING_DATA_API_URL.format(station_code=station_code)
    headers = {
        "Accept": "application/json",
        "User-Agent": HA_USER_AGENT,
    }
            
    response = await client.get(url, headers=headers, timeout=10)
    if response.is_success:
        res_data = response.json()
        if res_data.get("@iot.count", 0) > 0:
            return res_data["value"][0]["properties"].get("stationID")
    return None
