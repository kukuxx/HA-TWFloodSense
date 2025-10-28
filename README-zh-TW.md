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

# 💧 台灣淹水感測器

**在 Home Assistant 中即時監控台灣各地的淹水深度**

[English](/README.md) | [繁體中文](/README-zh-TW.md)

---

## 📋 概述

此整合提供台灣各地即時淹水深度監測功能。資料來源為[民生公共物聯網資料服務平台](https://ci.taiwan.gov.tw/dsp/)。

> [!NOTE]
> **無需 API Key**:此整合使用公開資料,不需要申請 API Key。

> [!TIP]
> **尋找感測器**:請前往 [TW-FloodMap](https://kukuxx.github.io/TW-FloodMap) 查詢您所在地區的感測器代碼和名稱。
>
> **除錯模式**:如果使用過程中遇到問題,請在整合設定中啟用**偵錯模式**,重現問題後,開啟 issue 並附上 log 檔案。

---

## ✨ 功能特色

### 💧 即時淹水監測
- 監測台灣各地部署的淹水感測器資料
- 存取民生公共物聯網水資源網路的資料
- 每 5 分鐘自動更新

### 📊 感測器資料

**淹水感測器**提供:
- **淹水深度**:以公分 (cm) 為單位的淹水深度
- **位置資訊**:GPS 座標 (經緯度)
- **站點資訊**:站點名稱、代碼和 ID
- **管理單位**:管理機關類型資訊
- **更新時間**:最後資料更新時間戳記

---

## 📦 安裝方式

### 方法一:HACS (建議)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kukuxx&repository=HA-TWFloodSense&category=Integration)

1. 在 Home Assistant 中開啟 HACS
2. 搜尋 "Taiwan FloodSense"
3. 點擊 "下載"
4. 重新啟動 Home Assistant

### 方法二:手動安裝

1. 從此儲存庫下載 `tw_floodsense` 資料夾
2. 複製到您的 `custom_components` 目錄
3. 重新啟動 Home Assistant

---

## 🚀 設定指南

### 尋找感測器資訊

在新增感測器之前,您需要先找到感測器代碼和名稱:

1. 前往 [TW-FloodMap](https://kukuxx.github.io/TW-FloodMap)
2. 瀏覽或搜尋您所在地區的感測器
3. 記下 **站點代碼 (Station Code)** 和 **站點名稱 (Station Name)**

### 初始設定

1. 前往 **設定** → **裝置與服務**
2. 點擊 **新增整合**
3. 搜尋 **Taiwan FloodSense**
4. 輸入您找到的 **站點代碼** 和 **站點名稱**
5. 點擊 **提交**

感測器實體將會自動建立!

### 新增更多感測器

完成初始設定後,您可以新增更多淹水感測器:

1. 前往您的 **Taiwan FloodSense** 整合
2. 點擊 **新增淹水感測器**
3. 輸入 **站點代碼** 和 **站點名稱**
4. 點擊 **提交**

---

## 🔍 疑難排解

### 新增感測器後實體未出現

1. 等待幾秒鐘讓自動重新載入完成
2. 檢查 Home Assistant 日誌是否有錯誤
3. 嘗試手動重新載入整合
4. 確認站點代碼是否正確

### 找不到感測器錯誤

1. 在 [TW-FloodMap](https://kukuxx.github.io/TW-FloodMap) 重新確認站點代碼
2. 確保您輸入的代碼完全正確 (區分大小寫)
3. 該感測器可能暫時離線或已移除

### 偵錯模式

在 `configuration.yaml` 中新增以下內容以啟用偵錯日誌:

```yaml
logger:
  default: info
  logs:
    custom_components.tw_floodsense: debug
```

---

## 🤝 貢獻

歡迎貢獻!請隨時提交 Pull Request。

---

## 📄 授權

此專案採用 Apache 2.0 授權 - 詳見 [LICENSE](LICENSE) 檔案。

---

## 🙏 致謝

- 資料由[民生公共物聯網資料服務平台](https://ci.taiwan.gov.tw/dsp/)提供
---

## 📞 支援

如果您遇到任何問題或有疑問:

1. 查看 [Issues](https://github.com/kukuxx/HA-TWFloodSense/issues) 頁面
2. 啟用偵錯模式並收集日誌
3. 開啟新的 issue 並提供詳細資訊

---