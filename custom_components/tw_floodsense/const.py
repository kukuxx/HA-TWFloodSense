from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import Platform

DOMAIN = "tw_floodsense"
CONF_STATION_CODE = "station_code"
CONF_STATION_NAME = "station_name"
CONF_THING_ID = "thing_id"
FLOODSENSE_COORDINATOR = "floodsense_coordinator"

API_BASE_URL = "https://sta.ci.taiwan.gov.tw/STA_WaterResource_v2/v1.0"
API_THING_PARAMS = f"@iot.id eq {{thing_id}}"
STATION_THING_API_URL = f"{API_BASE_URL}/Things?$filter=(properties/stationCode eq '{{code}}')"
STATION_DATA_API_URL = (
    f"{API_BASE_URL}/Things?$filter=({{filter_codes}})"
    f"&$expand=Datastreams($filter=name eq '淹水深度';$expand=Observations($orderby=phenomenonTime desc;$top=1))"
)
HA_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) HomeAssistant/HA-TWFloodSense"
)

PLATFORM = [Platform.SENSOR]

SENSOR_INFO = {
    "water_level": {
        "device_class": SensorDeviceClass.PRECIPITATION,
        "unit": "cm",
        "state_class": SensorStateClass.MEASUREMENT,
        "display_precision": 2,
        "icon": "mdi:water-alert",
    },
}
