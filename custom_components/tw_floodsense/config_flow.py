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
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    DOMAIN,
    CONF_STATION_CODE,
    CONF_STATION_ID,
    CONF_STATION_NAME,
)

_LOGGER = logging.getLogger(__name__)
TEXT_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT))


class TWFloodSenseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TWFloodSense."""

    VERSION = 2

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle the initial configuration step."""
        errors: dict[str, str] = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            station_name = user_input.get(CONF_STATION_NAME)
            station_id = user_input.get(CONF_STATION_ID)
            station_code = user_input.get(CONF_STATION_CODE)
            
            if not station_name:
                errors["base"] = "no_station_name"
            elif not station_id:
                errors["base"] = "no_station_id"
            elif not station_code:
                errors["base"] = "no_station_code"
            else:
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
                vol.Required(CONF_STATION_NAME): TEXT_SELECTOR,
                vol.Required(CONF_STATION_ID): TEXT_SELECTOR,
                vol.Required(CONF_STATION_CODE): TEXT_SELECTOR,
                
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
            station_name = user_input.get(CONF_STATION_NAME)
            station_id = user_input.get(CONF_STATION_ID)
            station_code = user_input.get(CONF_STATION_CODE)
            
            if not station_name:
                errors["base"] = "no_station_name"
            elif not station_id:
                errors["base"] = "no_station_id"
            elif not station_code:
                errors["base"] = "no_station_code"
            else:
                return self.async_create_entry(
                    title=f"{station_name}({station_code})",
                    data=user_input,
                    unique_id=str(station_code),
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_STATION_NAME): TEXT_SELECTOR,
                vol.Required(CONF_STATION_ID): TEXT_SELECTOR,
                vol.Required(CONF_STATION_CODE): TEXT_SELECTOR,
            }
        )

        return self.async_show_form(
            step_id="floodsense",
            data_schema=schema,
            errors=errors,
        )
    
    async_step_user = async_step_floodsense
