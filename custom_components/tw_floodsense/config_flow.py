import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    DOMAIN,
    CONF_STATION_CODE,
    CONF_STATION_NAME,
    CONF_THING_ID,
    STATION_THING_API_URL,
    HA_USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)
TEXT_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT))


@callback
async def _query_thing_id(
    hass: HomeAssistant, station_code: str
) -> tuple[int | None, str | None, str]:
    """Query Thing ID from API. Returns (thing_id,error)."""
    try:
        client = get_async_client(hass, False)
        url = STATION_THING_API_URL.format(code=station_code)
        headers = {
            "Accept": "application/json",
            "User-Agent": HA_USER_AGENT,
        }

        response = await client.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("@iot.count", 0) > 0:
                thing_id = data["value"][0]["@iot.id"]
                return thing_id, ""
            else:
                return None, "station_not_found"
        else:
            return None, "cannot_connect"
    except Exception as e:
        _LOGGER.error("Error querying flood sense API: %s", e)
        return None, "unknown"


class TWFloodSenseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TWFloodSense."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle the initial configuration step."""
        errors: dict[str, str] = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            station_code = user_input.get(CONF_STATION_CODE)
            station_name = user_input.get(CONF_STATION_NAME)
            if not station_code:
                errors["base"] = "no_station_code"
            elif not station_name:
                errors["base"] = "no_station_name"
            else:
                thing_id, error = await _query_thing_id(self.hass, station_code)
                if error:
                    errors["base"] = error
                else:
                    user_input[CONF_THING_ID] = int(thing_id)

                    subentries = [
                        {
                            "title": f"{station_name}({station_code})",
                            "subentry_type": "floodsense",
                            "data": user_input,
                            "unique_id": str(station_code),
                        }
                    ]

                    return self.async_create_entry(
                        title="TWFloodSense",
                        data={},
                        subentries=subentries,
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_STATION_CODE): TEXT_SELECTOR,
                vol.Required(CONF_STATION_NAME): TEXT_SELECTOR,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls,
        config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this integration."""
        return {
            "floodsense": FloodSenseSubentryFlowHandler,
        }


class FloodSenseSubentryFlowHandler(ConfigSubentryFlow):
    """Handle subentry flow for adding flood sense stations."""

    async def async_step_floodsense(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Flood sense flow to add a new flood sense sensor."""
        errors: dict[str, str] = {}

        if user_input is not None:
            station_code = user_input.get(CONF_STATION_CODE)
            station_name = user_input.get(CONF_STATION_NAME)
            if not station_code:
                errors["base"] = "no_station_code"
            elif not station_name:
                errors["base"] = "no_station_name"
            else:
                thing_id, error = await _query_thing_id(self.hass, station_code)
                if error:
                    errors["base"] = error
                else:
                    user_input[CONF_THING_ID] = int(thing_id)

                    return self.async_create_entry(
                        title=f"{station_name}({station_code})",
                        data=user_input,
                        unique_id=str(station_code),
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_STATION_CODE): TEXT_SELECTOR,
                vol.Required(CONF_STATION_NAME): TEXT_SELECTOR,
            }
        )

        return self.async_show_form(
            step_id="floodsense",
            data_schema=schema,
            errors=errors,
        )
    
    async_step_user = async_step_floodsense
