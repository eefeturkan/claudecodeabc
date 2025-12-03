# BIST100 Portfoy Optimizasyonu - Test Raporu

**Tarih:** 24 Kasim 2025
**Test Sayisi:** 9
**Basari Orani:** 100% (9/9)

---

## 1. TEST OZETI

Tum risk profili ve yatirim suresi kombinasyonlari test edildi:

| # | Risk Profili | Yatirim Suresi | Durum |
|---|--------------|----------------|-------|
| 1 | Dusuk | Kisa (6 ay) | BASARILI |
| 2 | Dusuk | Orta (1 yil) | BASARILI |
| 3 | Dusuk | Uzun (5 yil) | BASARILI |
| 4 | Orta | Kisa (6 ay) | BASARILI |
| 5 | Orta | Orta (1 yil) | BASARILI |
| 6 | Orta | Uzun (5 yil) | BASARILI |
| 7 | Yuksek | Kisa (6 ay) | BASARILI |
| 8 | Yuksek | Orta (1 yil) | BASARILI |
| 9 | Yuksek | Uzun (5 yil) | BASARILI |
    
---

## 2. PERFORMANS SONUCLARI

### 2.1. Detayli Tablo

| Risk | Vade | Getiri% | Volatilite% | Sharpe | Sortino | MaxDD% |
|------|------|---------|-------------|--------|---------|--------|
| Dusuk | Kisa | 101.34 | 17.79 | 5.13 | 9.52 | -4.43 |
| Dusuk | Orta | 66.93 | 20.69 | 2.75 | 3.65 | -11.14 |
| Dusuk | Uzun | 64.81 | 23.56 | 2.33 | 3.12 | -22.28 |
| Orta | Kisa | **148.20** | 19.07 | **7.25** | **14.69** | **-4.20** |
| Orta | Orta | 131.00 | 25.34 | 4.78 | 6.59 | -9.54 |
| Orta | Uzun | 100.90 | 27.70 | 3.28 | 4.62 | -27.52 |
| Yuksek | Kisa | 105.85 | 22.23 | 4.31 | 8.03 | -7.63 |
| Yuksek | Orta | 86.42 | 24.92 | 3.07 | 4.36 | -9.90 |
| Yuksek | Uzun | 72.15 | 31.49 | 1.97 | 3.08 | -21.80 |

### 2.2. En Iyi Performanslar

- **En Yuksek Getiri:** Orta risk + Kisa vade = %148.20
- **En Iyi Sharpe Ratio:** Orta risk + Kisa vade = 7.25
- **En Iyi Sortino Ratio:** Orta risk + Kisa vade = 14.69
- **En Dusuk Volatilite:** Dusuk risk + Kisa vade = %17.79
- **En Dusuk Max Drawdown:** Orta risk + Kisa vade = %-4.20

---

## 3. MANTIK KONTROLLERI

### 3.1. Volatilite - Risk Profili Iliskisi

| Risk Profili | Ortalama Volatilite |
|--------------|---------------------|
| Dusuk | 20.7% |
| Orta | 24.0% |
| Yuksek | 26.2% |

**SONUC:** Yuksek risk profili daha yuksek volatilite uretmektedir. DOGRU

### 3.2. Sharpe Ratio Pozitiflik

Tum 9 testte Sharpe Ratio pozitif. DOGRU

### 3.3. Hisse Secimi

Tum testlerde 10 hisse secildi ve hepsine agirlik verildi. DOGRU

### 3.4. Max Drawdown Degerleri

Degerler negatif (kayip olarak) ve mantikli aralikta:
- En dusuk: -4.20% (Orta + Kisa)
- En yuksek: -27.52% (Orta + Uzun)

**NOT:** Uzun vadeli portfoylerde daha yuksek max drawdown beklenir. DOGRU

---

## 4. ILGINC BULGULAR

### 4.1. Orta Risk En Iyi Performansi Gosterdi

Beklenin aksine, **orta risk profili** en yuksek getiri ve en iyi Sharpe degerlerini uretti:
- Kisa vadede: %148.20 getiri, 7.25 Sharpe
- Bu durum, portfoy teorisine uygundur - asiri risk her zaman daha yuksek getiri saglamaz

### 4.2. Kisa Vade En Yuksek Getiri

Kisa vadeli testler (6 ay) en yuksek yillik getiri oranlarini gosterdi:
- Bunun sebebi: Son 6 ayda BIST100'de guclu bir yükselis trendi olmasi

### 4.3. Uzun Vadede Drawdown Artisi

5 yillik veri kullanan testlerde max drawdown daha yuksek:
- Dusuk + Uzun: -22.28%
- Orta + Uzun: -27.52%
- Yuksek + Uzun: -21.80%

Bu beklenen bir sonuctur - daha uzun sureler daha fazla piyasa dalgalanmasi icerir.

---

## 5. SISTEM STABILITESI

### 5.1. API Yanit Sureleri

| Test | Sure (saniye) |
|------|---------------|
| En hizli | 3.9s (Yuksek + Orta) |
| En yavas | 58.1s (Orta + Kisa) |
| Ortalama | ~25s |

Uzun sureler genellikle cache'de olmayan hisseler icin Yahoo Finance API'den veri cekilmesinden kaynaklanmaktadir.

### 5.2. Hata Orani

- Toplam test: 9
- Basarisiz: 0
- Hata orani: **0%**

---

## 6. SONUC VE ONERILER

### Sistem Durumu: CALISIR DURUMDA

ABC algoritmasi ve portfoy optimizasyonu dogru calisiyor. Tum test kombinasyonlari basariyla tamamlandi.

### Oneriler:

1. **Uzun vadeli portfoyler icin:** Max drawdown yuksek, bu konuda kullaniciya uyari verilebilir

2. **Performans:** Cache sistemi sayesinde tekrarlayan istekler hizli. Ilk calisma 1-2 dakika surebilir.

3. **En iyi strateji (test verilerine gore):** Orta risk + Kisa vade kombinasyonu en yuksek risk-ayarli getiri sagliyor

---

## 7. TEKNIK NOTLAR

- Test ortami: Windows 11, Python 3.11
- Flask sunucusu: localhost:5000
- ABC parametreleri: colony_size=50, max_iterations=100
- Yatirim tutari: 100,000 TL
- Max hisse sayisi: 10

---

**Rapor Sonu**
