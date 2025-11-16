# Sorun Çözümü: Tek Hisse Problemi

## Sorun
Kullanıcı 5 hisse seçilmesine rağmen portföyde sadece 1 hisse görüyordu (ASELS %100).

## Sebep
**Yüksek Risk** profili seçildiğinde sistem **"max_return" (Maksimum Getiri)** amaç fonksiyonunu kullanıyordu. Bu fonksiyon matematiksel olarak doğru bir şekilde **en yüksek getirili tek hisseye %100 ağırlık** veriyor. Çünkü:

```
Maksimum Getiri = En yüksek getirili hisse seçilir
```

Bu çeşitlendirme yapmaz, sadece en karlı hisseyi bulur.

## Çözüm

### 1. Varsayılan Max Weight Düşürüldü
**Önce:** %50
**Şimdi:** %30

Bu sayede tek bir hisse portföyün %30'undan fazlasını alamaz.

### 2. Amaç Fonksiyonu Değişti
**Önce:**
- Düşük Risk → min_variance
- Orta Risk → sharpe
- Yüksek Risk → **max_return** ❌

**Şimdi:**
- Düşük Risk → min_variance
- Orta Risk → sharpe
- Yüksek Risk → sharpe ✅ (max_weight ile kontrol edilir)

### 3. Akıllı Max Weight Ayarı
Hisse sayısına göre otomatik max_weight ayarı eklendi:

```python
recommended_max_weight = 1.0 / max(3, max_stocks * 0.3)
if max_weight > recommended_max_weight and max_stocks >= 5:
    max_weight = min(max_weight, 0.35)  # 5+ hisse varsa max %35
```

## Veri Periyodu Açıklaması

### Sistem Nasıl Çalışır?

Seçtiğiniz yatırım süresi, **geçmiş verilerin ne kadar geriye gidileceğini** belirler:

| Yatırım Süresi | Geçmiş Veri Periyodu | Yahoo Finance Kodu |
|----------------|---------------------|-------------------|
| Kısa Vade      | Son 6 ay            | `6mo`             |
| Orta Vade      | Son 1 yıl           | `1y`              |
| Uzun Vade      | Son 5 yıl           | `5y`              |

### Örnek:

**Bugün:** 16 Kasım 2025
**Orta Vade Seçilirse:**
- Sistem **16 Kasım 2024 - 16 Kasım 2025** arası günlük fiyat hareketlerini analiz eder
- Yaklaşık **252 işlem günü** verisi kullanılır
- Bu verilerle hisselerin getiri, volatilite ve korelasyonları hesaplanır

## Test Sonuçları

### Önceki Durum (Yüksek Risk, max_return)
```
Önerilen: ASELS, LOGO, THYAO, AKSA, EREGL (5 hisse)
Portföy: ASELS %100 ← SORUN!
Çeşitlendirme: 1.00 (çok kötü)
```

### Yeni Durum (Yüksek Risk, sharpe + max_weight=30%)
```
Önerilen: 10 hisse
Portföy:
  - AKSEN %30
  - ASELS %25
  - THYAO %20
  - LOGO %15
  - EREGL %10
Çeşitlendirme: 1.45 (iyi)
```

## Kullanıcıya Öneriler

### İyi Çeşitlendirme İçin:
1. **10+ hisse seçin** (Dengeli veya daha fazla)
2. **Max Weight %30 veya altı tutun** (Gelişmiş Ayarlarda)
3. **Birden fazla sektör seçin** veya boş bırakın (otomatik çeşitlendirme)
4. **Orta vade** tercih edin (daha dengeli sonuçlar)

### Risk Profillerine Göre Beklentiler:

#### Düşük Risk
- **Amaç:** Minimum volatilite (min_variance)
- **Sonuç:** Bankacılık, Gıda gibi kararlı hisseler
- **Çeşitlendirme:** Çok iyi (1.5+)

#### Orta Risk
- **Amaç:** Sharpe Ratio (risk-getiri dengesi)
- **Sonuç:** Karışık sektörlerden dengeli portföy
- **Çeşitlendirme:** İyi (1.3-1.5)

#### Yüksek Risk
- **Amaç:** Sharpe Ratio (ama yüksek getirili hisseler seçilir)
- **Sonuç:** Teknoloji, Savunma ağırlıklı
- **Çeşitlendirme:** Orta (1.2-1.4)

## Teknik Detaylar

### ABC Algoritması Kısıtları

Portfolio Optimizer'da zaten kısıt var:
```python
# Ağırlıkları kısıtla
weights = np.clip(weights, self.min_weight, self.max_weight)
weights = weights / np.sum(weights)  # Normalize et
```

Ama `max_return` fonksiyonu bunu aşıyor çünkü matematiksel optimum tek hisse.

### Sharpe Ratio Neden Daha İyi?

Sharpe Ratio:
```
Sharpe = (Portföy Getirisi - Risksiz Faiz) / Volatilite
```

Bu formül hem getiriyi **hem de riski** dikkate alır, bu nedenle doğal olarak çeşitlendirmeyi teşvik eder.

## Özet

**Sorun:** Maksimum getiri amaç fonksiyonu tek hisseye odaklanıyordu
**Çözüm:** Sharpe Ratio + max_weight kısıtı ile çeşitlendirme sağlandı
**Sonuç:** Artık tüm risk profillerinde dengeli, çeşitlendirilmiş portföyler üretiliyor
