# Laporan Implementasi — Day 15: Advanced Forecasting

**Proyek:** LEUIT (Local-First F&B Demand & Inventory Forecasting)
**Tanggal:** 2026-10-02
**PR:** #16 — `feat(day15): advanced forecasting with Prophet integration`
**Status:** ✅ Merged ke `staging` (commit `746b882d`)

---

## 1. Executive Summary

Day 15 menambahkan lapisan forecasting canggih berbasis Facebook Prophet ke backend LEUIT. Model dilatih dari data konsumsi historis bahan, memakai musiman tahunan/mingguan, kalender libur nasional Indonesia 2024–2026, serta penyesuaian prediksi berdasarkan cuaca (hujan, suhu, kelembapan) dari BMKG. Endpoint baru `GET /api/v1/forecast/30-day` mengembalikan forecast 30 hari per bahan lengkap dengan confidence interval (`yhat_lower`/`yhat_upper`), flag `weather_adjusted`, dan `model_info`. Endpoint `GET /api/v1/forecast/restock-sheet` ditingkatkan agar memakai Prophet + weather adjustment. Model dapat di-persist dan di-load kembali (cache per bahan). Deliverable utama: 41 test baru (`test_forecasting_advanced.py`), 1212 baris ditambah, lint/typecheck bersih, CI hijau setelah 1 iterasi perbaikan mypy.

---

## 2. Files Changed

| File | Perubahan |
|------|-----------|
| `backend/app/services/forecaster.py` | Integrasi Prophet: `_prepare_prophet_data`, `_create_prophet_model` (yearly/weekly seasonality, `seasonality_mode="multiplicative"`, holidays DataFrame libur Indonesia), `_train_prophet_model`, `save_model`/`load_model` (persist per `ingredient_id`), `_get_weather_data` (fallback ke `weather_client.get_weather_forecast`), `_apply_weather_adjustment` (rainfall_prob −15% skala, suhu & kelembapan), `forecast_with_prophet` (training → prediksi → weather adjustment → deteksi seasonality), `forecast_30_day`, `forecast_restock_sheet` (ditingkatkan memakai Prophet), daftar `INDONESIAN_HOLIDAYS` 2024–2026 |
| `backend/app/api/v1/forecast.py` | Endpoint baru `GET /forecast/30-day` (`get_30_day_forecast`) — forecast per bahan dengan predictions, `model_info`, `weather_adjusted`; `GET /forecast/restock-sheet` diubah memanggil Prophet path; `GET /forecast/weather` (BMKG) dipertahankan |
| `backend/app/schemas/forecast_schema.py` | Skema baru: `ForecastItemResponse` (date, yhat, yhat_lower, yhat_upper, weather_adjusted) dan `Forecast30DayResponse` (ingredient_id, predictions, model_info, weather_adjusted) |
| `backend/tests/test_forecasting_advanced.py` | File test baru — 41 test (lihat bagian 3) |
| `Sprint_2_plan.md` | Dokumen sprint diperbarui untuk mencerminkan penyelesaian Day 15 |

---

## 3. Test Coverage

**Total: 41 test** — semua lulus (`pytest backend/tests/test_forecasting_advanced.py`).

| Kelas Test | Jumlah | Cakupan |
|------------|--------|---------|
| `TestCalculateAvgDailyUsage` | 3 | rata-rata konsumsi harian (0, 1, banyak record) |
| `TestPredictConsumption` | 4 | prediksi konsumsi N hari, horizon default/kustom, usage nol |
| `TestCalculateSafetyStock` | 3 | safety stock, multiplier kustom, threshold nol |
| `TestCalculateRecommendedOrderQty` | 3 | qty pesan, tidak perlu pesan, stok persis minimum |
| `TestCalculatePriority` | 6 | prioritas high/medium/low, batas tepat 100%/150% |
| `TestPrepareProphetData` | 2 | DataFrame kosong, prep data historis |
| `TestCreateProphetModel` | 2 | model terbentuk, holidays Indonesia terpasang |
| `TestWeatherAdjustment` | 4 | hujan menurunkan prediksi, suhu tinggi menaikkan, no-weather no-op, kelembapan tinggi menurunkan |
| `TestIndonesianHolidays` | 4 | holidays ada untuk 2024, 2025, 2026 |
| `TestSeasonalityDetection` | 1 | deteksi seasonality yearly/weekly |
| `TestWeatherIntegration` | 2 | `_get_weather_data` sukses (mock), weather masuk ke forecast |
| `TestModelPersistence` | 1 | save → load model |
| `TestWeatherParsing` | 2 | parse respons BMKG, respons kosong |
| `TestCache` | 1 | clear cache prediksi |
| `TestForecast30DayEndpoint` | 1 | struktur respons endpoint 30-day |
| `TestRestockSheetWithProphet` | 2 | struktur restock-sheet via Prophet, dengan bahan terisi |

---

## 4. CI Iterations

**Jumlah iterasi: 2** (1 iterasi perbaikan mypy)

1. **Iterasi 1 — Fail (mypy):** jalur PR gagal di step `lint-typecheck` akibat error type pada code Prophet integration (signature/return type yang tidak sesuai).
2. **Iterasi 2 — Pass:** perbaikan mypy diterapkan; lint (ruff), typecheck (mypy), dan seluruh test workflow hijau. PR #16 kemudian merge.

---

## 5. Architecture Compliance

Sesuai Backend Architecture v1.0 dan PRD v1.8:

| Aspek | Implementasi |
|------|----------------|
| **Prophet** | `from prophet import Prophet`; model per bahan dengan training dari data historis ≥ 90 hari; persist/restore via `save_model`/`load_model` |
| **Seasonality** | `yearly_seasonality=True`, `weekly_seasonality=True`, `daily_seasonality=False`, `seasonality_mode="multiplicative"`; `_detect_seasonality` melaporkan year/weekly availability |
| **Indonesian Holidays** | DataFrame holidays internal (libur nasional + cuti 2024–2026) di-inject ke `Prophet(holidays=...)` — tidak bergantung API eksternal |
| **Weather** | Integrasi `weather_client.get_weather_forecast` (BMKG); `_apply_weather_adjustment` menyesuaikan yhat & interval: faktor hujan `1 − (rainfall_prob/100)×0.15`, efek suhu > 30°C, penalti kelembapan > 85%; flag `weather_adjusted` di respons |
| **30-day Forecast** | `GET /api/v1/forecast/30-day` → `forecast_30_day()` → `Forecast30DayResponse` dengan 30 prediksi harian + confidence interval + `model_info` |

Pemisahan concern terjaga: service layer (`forecaster.py`) memegang logika, API layer (`forecast.py`) hanya routing + mapping ke response schema (`forecast_schema.py`).

---

## 6. Commands to Resume

```bash
cd D:\Project\Leuit
git checkout staging && git pull origin staging

# Jalankan test Day 15
python -m pytest backend/tests/test_forecasting_advanced.py -v

# Lint & typecheck backend
cd backend
python -m ruff check app tests
python -m mypy app

# Endpoint 30-day (server lokal jalan dulu)
uvicorn app.main:app --reload
# lalu: GET http://localhost:8000/api/v1/forecast/30-day?ingredient_id=1

# Riwayat PR #16
git show 746b882d --stat
```

---

*Laporan ini mengikuti format laporan harian proyek LEUIT (Bahasa Indonesia).*
