[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]

[contributors-shield]: https://img.shields.io/github/contributors/kukuxx/HA-TWFloodSense.svg?style=for-the-badge
[contributors-url]: https://github.com/kukuxx/HA-TWFloodSense/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/kukuxx/HA-TWFloodSense.svg?style=for-the-badge
[forks-url]: https://github.com/kukuxx/HA-TWFloodSense/network/members

[stars-shield]: https://img.shields.io/github/stars/kukuxx/HA-TWFloodSense.svg?style=for-the-badge
[stars-url]: https://github.com/kukuxx/HA-TWFloodSense/stargazers

[issues-shield]: https://img.shields.io/github/issues/kukuxx/HA-TWFloodSense.svg?style=for-the-badge
[issues-url]: https://github.com/kukuxx/HA-TWFloodSense/issues

[license-shield]: https://img.shields.io/github/license/kukuxx/HA-TWFloodSense.svg?style=for-the-badge
[license-url]: https://github.com/kukuxx/HA-TWFloodSense/blob/main/LICENSE

# 💧 Taiwan FloodSense

**Monitor Taiwan's flood water levels in real-time with Home Assistant**

[English](/README.md) | [繁體中文](/README-zh-TW.md)

---

## 📋 Overview

This integration provides real-time flood water level monitoring across Taiwan. Data is sourced from the [Water Resources Dataset of Civil IoT Taiwan](https://sta.ci.taiwan.gov.tw/).

> [!NOTE]
> **No API Key Required**: This integration uses public data and does not require an API key.

> [!TIP]
> **Finding Sensors**: Visit [TW-FloodMap](https://kukuxx.github.io/TW-FloodMap) to find sensor codes and names for your area.
>
> **Debugging**: If you encounter any issues, enable **debug mode** in the integration settings, reproduce the problem, then open an issue with the log file.

---

## ✨ Features

### 💧 Real-Time Flood Monitoring
- Monitor flood water levels from sensors deployed across Taiwan
- Access data from the Civil IoT Taiwan water resources network
- Automatic updates every 5 minutes

### 📊 Sensor Data

**FloodSense Sensors** provide:
- **Water Level**: Flood depth in centimeters (cm)
- **Location**: GPS coordinates (latitude/longitude)
- **Station Information**: Station name, code, and ID
- **Authority Type**: Managing authority information
- **Update Time**: Last data update timestamp

---

## 📦 Installation

### Method 1: HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kukuxx&repository=HA-TWFloodSense&category=Integration)

1. Open HACS in your Home Assistant instance
2. Search for "Taiwan FloodSense"
3. Click "Download"
4. Restart Home Assistant

### Method 2: Manual Installation

1. Download the `tw_floodsense` folder from this repository
2. Copy it to your `custom_components` directory
3. Restart Home Assistant

---

## 🚀 Setup Guide

### Finding Sensor Information

Before adding sensors, you need to find the sensor code and name:

1. Visit [TW-FloodMap](https://kukuxx.github.io/TW-FloodMap)
2. Browse or search for sensors in your area
3. Note down the **Station Code** and **Station Name**

### Initial Setup

1. Navigate to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Taiwan FloodSense**
4. Enter the **Station Code** and **Station Name** you found
5. Click **Submit**

The sensor entities will be automatically created!

### Adding More Sensors

After initial setup, you can add more flood sensors:

1. Go to your **Taiwan FloodSense** integration
2. Click **Add FloodSense Sensor**
3. Enter the **Station Code** and **Station Name**
4. Click **Submit**

---

## 🔍 Troubleshooting

### Entities Not Appearing After Adding Sensor

1. Wait a few seconds for the automatic reload to complete
2. Check Home Assistant logs for any errors
3. Try manually reloading the integration
4. Verify the Station Code is correct

### Sensor Not Found Error

1. Double-check the Station Code at [TW-FloodMap](https://kukuxx.github.io/TW-FloodMap)
2. Ensure you're entering the exact code (case-sensitive)
3. The sensor may be temporarily offline or removed

### Debug Mode

Enable debug logging by adding to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.tw_floodsense: debug
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

- Data provided by [Water Resources Dataset of Civil IoT Taiwan](https://sta.ci.taiwan.gov.tw/)

---

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/kukuxx/HA-TWFloodSense/issues) page
2. Enable debug mode and collect logs
3. Open a new issue with detailed information

---