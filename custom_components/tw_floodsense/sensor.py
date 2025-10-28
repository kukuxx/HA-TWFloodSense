from __future__ import annotations

import logging

from homeassistant.components.sensor import RestoreSensor
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_STATION_CODE,
    CONF_STATION_NAME,
    DOMAIN,
    FLOODSENSE_COORDINATOR,
    SENSOR_INFO,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up TWFloodSense sensors from a config entry."""
    try:
        entry_data = hass.data[DOMAIN][entry.entry_id]

        for subentry_id, subentry in entry.subentries.items():
            if not hasattr(subentry, 'subentry_type'):
                continue

            subentry_entities = []

            # 處理 flood sense subentry
            if subentry.subentry_type == "floodsense":
                station_code = subentry.data.get(CONF_STATION_CODE)
                station_name = subentry.data.get(CONF_STATION_NAME)
                coordinator = entry_data.get(FLOODSENSE_COORDINATOR)
                
                subentry_entities.extend([
                    FloodSenseSensor(
                        coordinator=coordinator,
                        station_code=station_code,
                        station_name=station_name,
                        sensor_type=sensor_type,
                        device_class=config["device_class"],
                        unit_of_measurement=config["unit"],
                        state_class=config["state_class"],
                        display_precision=config["display_precision"],
                        icon=config["icon"]
                    ) for sensor_type, config in SENSOR_INFO.items()
                ])

            # 為這個 subentry 添加實體
            if subentry_entities:
                async_add_entities(subentry_entities, config_subentry_id=subentry_id)
                _LOGGER.debug(
                    "Added %d entities for subentry %s (type: %s)",
                    len(subentry_entities),
                    subentry_id,
                    subentry.subentry_type
                )

    except Exception as e:
        _LOGGER.error("setup sensor error: %s", e, exc_info=True)


class BaseSensor(CoordinatorEntity, RestoreSensor):
    """Representation of a TWFloodSense base sensor."""

    def __init__(
        self,
        coordinator,
        station_code,
        station_name,
        sensor_type,
        device_class,
        unit_of_measurement,
        state_class,
        display_precision,
        icon,
    ):
        """Initialize the TWFloodSense sensor."""
        super().__init__(coordinator)
        self._station_code = station_code
        self._station_name = station_name
        self._sensor_type = sensor_type
        self._device_class = device_class
        self._unit_of_measurement = unit_of_measurement
        self._state_class = state_class
        self._display_precision = display_precision
        self._icon = icon
        self._last_value = None

    async def async_added_to_hass(self):
        """Get the old value"""
        await super().async_added_to_hass()

        if (
            (last_sensor_data := await self.async_get_last_sensor_data())
            and last_sensor_data.native_value is not None
            and self._device_class is not None
        ):
            self._last_value = last_sensor_data.native_value
            _LOGGER.debug(
                "Restored last value: %s for %s", self._last_value, self.name
            )

    @property
    def coordinator_data(self) -> dict:
        return self.coordinator.data
    
    @property
    def _get_value(self):
        return self.coordinator_data.get(self._station_code, {}).get(self._sensor_type)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._station_code)},
            "name": (
                f"TWFloodSense - {self._station_name}"
                f"({self._station_code})"
            ),
            "manufacturer": "Water Resources Dataset of Civil IoT Taiwan",
            "model": "TWFloodSense",
        }

    @property
    def device_class(self):
        return self._device_class  # 設備類型

    @property
    def native_unit_of_measurement(self):
        return self._unit_of_measurement  # 預設單位

    @property
    def state_class(self):
        return self._state_class  # 圖表類型

    @property
    def suggested_display_precision(self):
        return self._display_precision

    @property
    def icon(self):
        return self._icon

    @property
    def has_entity_name(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def name(self):
        sensor_type = (
            self._sensor_type.replace("_", " ") if self._sensor_type else "unknown"
        )

        return f"{self._station_name} {sensor_type}"

    @property
    def unique_id(self):
        sanitized_name = (
            self._sensor_type.replace(" ", "_") if self._sensor_type else "unknown"
        )
        return f"{DOMAIN}_{self._station_code}_{sanitized_name}"

    @property
    def native_value(self):
        if self._is_valid_data() and self.coordinator.last_update_success:
            return self._get_value
        else:
            return None

    def _is_valid_data(self) -> bool:
        """Validate the integrity of the data."""
        if not self.coordinator_data:
            _LOGGER.error(
                "No data available for station %s",
                self._station_code,
            )
            return False

        if self._station_code not in self.coordinator_data:
            _LOGGER.error(
                "The station '%s' is not in the data.\n"
                "Please confirm whether the configuration is correct,\n"
                "then delete the subentry and re-add it.\n"
                "Available stations: %s",
                self._station_code,
                list(self.coordinator_data.keys()),
            )
            return False

        if (value := self._get_value) in [None, ""]:
            if value is None:
                _LOGGER.debug(
                    "The value for '%s' in station '%s' is missing or None.",
                    self._sensor_type,
                    self._station_code,
                )
            elif value == "":
                _LOGGER.debug(
                    "The value for '%s' in station '%s' is empty",
                    self._sensor_type,
                    self._station_code,
                )
            return False

        _LOGGER.debug(
            "Valid data found for station '%s' and type '%s': %s",
            self._station_code,
            self._sensor_type,
            value,
        )
        return True


class FloodSenseSensor(BaseSensor):
    """Representation of a TWFloodSense Sensor."""

    def __init__(
        self,
        coordinator,
        station_code,
        station_name,
        sensor_type,
        device_class,
        unit_of_measurement=None,
        state_class=None,
        display_precision=None,
        icon=None,
    ):
        """Initialize the FloodSense sensor."""
        super().__init__(
            coordinator,
            station_code,
            station_name,
            sensor_type,
            device_class,
            unit_of_measurement,
            state_class,
            display_precision,
            icon,
        )

        self._station_code = station_code
        self._station_name = station_name

        _LOGGER.debug(
            "Initialized FloodSenseSensor for station_id: %s, type: %s",
            self._station_code,
            self._sensor_type,
        )


    @property
    def extra_state_attributes(self):
        if self.coordinator_data and self._station_code in self.coordinator_data:
            thing_data = self.coordinator_data[self._station_code]

            attrs = {
                "station_name": thing_data.get("stationName", "unknown"),
                "station_code": self._station_code,
                "station_id": thing_data.get("stationID", "unknown"),
                "thing_id": thing_data.get("thing_id", "unknown"),
                "longitude": thing_data.get("longitude", "unknown"),
                "latitude": thing_data.get("latitude", "unknown"),
                "authority_type": thing_data.get("authority_type", "unknown"),
                "update_time": thing_data.get("update_time", "unknown"),
            }

            return attrs
        else:
            return {
                "station_code": self._station_code,
            }
