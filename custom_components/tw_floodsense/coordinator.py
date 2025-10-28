from __future__ import annotations

import asyncio
import functools
import logging
import random
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import (
    Any,
    Callable,
    TypeVar,
)

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import as_local, parse_datetime

from .const import (
    DOMAIN,
    HA_USER_AGENT,
    API_FILTER_PARAMS,
    STATION_DATA_API_URL,
)
from .exceptions import (
    ApiAuthError,
    DataNotFoundError,
    RecordNotFoundError,
    RequestFailedError,
    RequestTimeoutError,
    UnexpectedStatusError,
)

_LOGGER = logging.getLogger(__name__)
F = TypeVar("F", bound=Callable[..., Any])


def retry_on_failure(max_retries: int = 5):
    """Retry decorator for coroutine functions."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            last_error = {"name": "Unknown"}

            for attempt in range(max_retries):
                try:
                    return await func(self, *args, **kwargs)
                except ApiAuthError:
                    raise
                except DataNotFoundError as e:
                    last_error = e
                    _LOGGER.warning(
                        "No valid data found in the %s API response. "
                        "Retrying... (%d/5)",
                        e["name"],
                        attempt + 1,
                    )
                except RecordNotFoundError as e:
                    last_error = e
                    _LOGGER.warning(
                        "No records found in the Site API response. "
                        "Retrying... (%d/5)",
                        attempt + 1,
                    )
                except UnexpectedStatusError as e:
                    last_error = e
                    _LOGGER.warning(
                        "%s API returned unexpected status code: %s. "
                        "Retrying... (%d/5)",
                        e["name"],
                        e["code"],
                        attempt + 1,
                    )
                except RequestTimeoutError as e:
                    last_error = e
                    _LOGGER.warning(
                        "%s API Request timed out: %s. Retrying... (%d/5)",
                        e["name"],
                        e["exception"],
                        attempt + 1,
                    )
                except RequestFailedError as e:
                    last_error = e
                    _LOGGER.warning(
                        "%s API Request failed: %s. Retrying... (%d/5)",
                        e["name"],
                        e["exception"],
                        attempt + 1,
                    )

                if attempt < (max_retries - 1):
                    await asyncio.sleep(random.uniform(5, 15))

            await self.hass.services.async_call(
                "notify",
                "persistent_notification",
                {
                    "message": (
                        f"Failed to fetch data after 5 attempts "
                        f"in the {last_error['name']} API."
                    ),
                    "title": "TWFloodSense Error",
                },
            )
            return None
        return wrapper
    return decorator


class baseCoordinator(DataUpdateCoordinator, ABC):
    """Base class to manage fetching data from the API."""

    def __init__(self, hass, name, update_interval):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )
        self.hass = hass
        self.client = get_async_client(hass, False)

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            data = await self._get_data_with_retry()
            if data:
                return data
            else:
                raise UpdateFailed("No data received from API")
        except ApiAuthError:
            raise ConfigEntryAuthFailed("API key expired or invalid")
        except Exception as e:
            raise UpdateFailed(f"Unexpected error during data update: {e}") from e
    
    @retry_on_failure(max_retries=5)
    async def _get_data_with_retry(self, *args, **kwargs):
        """Fetch data from API with retry."""
        return await self._get_data(*args, **kwargs)
    
    @abstractmethod
    async def _get_data(self, *args, **kwargs):
        """Fetch the data from the API."""


class FloodSenseCoordinator(baseCoordinator):
    """Class to manage fetching data from the flood sense API."""

    def __init__(self, hass, station_codes, station_ids):
        super().__init__(
            hass,
            name=f"{DOMAIN}_floodsense",
            update_interval=timedelta(minutes=5),
        )

        self.station_codes = station_codes
        self.station_ids = station_ids

    async def _get_data(self):
        """Fetch the micro sensor data from the API."""
        filter_params = " or ".join(
            API_FILTER_PARAMS.format(stationID=stationID) 
            for stationID in self.station_ids
        )

        url = STATION_DATA_API_URL.format(filter_params=filter_params)
        headers = {
            "Accept": "application/json",
            "User-Agent": HA_USER_AGENT,
        }

        _LOGGER.debug("Flood sense Station Data API URL: %s", url)

        err = {"name": "TWFloodSense",}

        try:
            response = await self.client.get(
                url,
                headers=headers,
                timeout=15
            )

            if response.is_success:
                res_data = response.json()

                parsed_data = self._parse_data(res_data)
                if parsed_data:
                    _LOGGER.debug(
                        "Successfully fetched data for flood sense stations: %s",
                        self.station_codes,
                    )
                    return parsed_data
                else:
                    raise DataNotFoundError(err)
            else:
                err["code"] = response.status_code
                raise UnexpectedStatusError(err)

        except DataNotFoundError as e:
            raise
        except UnexpectedStatusError as e:
            raise
        except asyncio.TimeoutError as e:
            err["exception"] = str(e)
            raise RequestTimeoutError(err) from e
        except Exception as e:
            err["exception"] = str(e)
            raise RequestFailedError(err) from e

    def _parse_data(self, res_data):
        """Parse flood sense data and extract sensor values."""
        _LOGGER.debug("Flood sense API response: %s", res_data)

        try:
            if (res_data.get("@iot.count", 0) == 0 
            or not (value := res_data.get("value"))):
                raise DataNotFoundError({"name": "TWFloodSense"})
            
            result = {}
            for data in value:
                thing_data = data["Thing"]["properties"]
                if (station_code := thing_data.get("stationCode")) in self.station_codes:
                    
                    result[station_code] = {
                        "thing_id": data["Thing"]["@iot.id"],
                        "stationID": thing_data.get("stationID"),
                        "stationCode": thing_data.get("stationCode"),
                        "stationName": thing_data.get("stationName"),
                        "authority_type": thing_data.get("authority_type"),
                    }

                    
                    coordinates = data["observedArea"].get("coordinates")
                    coords = self._parse_coordinates(coordinates)
                    result[station_code]["latitude"] = coords["lat"]
                    result[station_code]["longitude"] = coords["lon"]

                    observations = data["Observations"]
                    if observations:
                        result[station_code]["water_level"] = observations[0].get("result")
                        result[station_code]["update_time"] = self._parse_datetime(
                            observations[0].get("phenomenonTime")
                        )
                    else:
                        result_data = {
                            "water_level": "",
                            "update_time": "unknown",
                        }
                        
                        result[station_code].update(result_data)

                        _LOGGER.warning(
                            "No Observations found for station %s. "
                            "Skipping...",
                            station_code,
                        )

            return result

        except Exception as e:
            _LOGGER.error("Error parsing flood sense data: %s", e)
            return None

    def _parse_coordinates(self, coords):
        """Parse coordinates and determine latitude and longitude."""
        if not coords:
            return {"lat": "unknown", "lon": "unknown"}

        lat_range = (10.36, 26.40)  # 緯度範圍
        lon_range = (114.35, 122.11)  # 經度範圍

        a, b = coords[0], coords[1]

        if lat_range[0] <= a <= lat_range[1] and lon_range[0] <= b <= lon_range[1]:
            return {"lat": a, "lon": b}
        elif lat_range[0] <= b <= lat_range[1] and lon_range[0] <= a <= lon_range[1]:
            return {"lat": b, "lon": a}
        else:
            return {"lat": "unknown", "lon": "unknown"}

    def _parse_datetime(self, datetime_str):
        """Parse datetime string and return local datetime string."""
        if not datetime_str:
            return "unknown"

        try:
            utc_dt = parse_datetime(datetime_str)
            local_dt = as_local(utc_dt)
            return local_dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            _LOGGER.error("Error parsing datetime: %s", e)
            return "unknown"

