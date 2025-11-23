# BIST100 Akıllı Portföy Danışmanı - Kullanım Kılavuzu

## Hızlı Başlangıç

### 1. Uygulamayı Başlatın

```bash
python backend/app.py
```

Tarayıcınızda açın: `http://localhost:5000`

## Kullanıcı Tercihleri

### Adım 1: Risk Profilinizi Seçin

#### Düşük Risk
- **Hedef Kitle**: Muhafazakar yatırımcılar, emekliler
- **Beklenen Getiri**: Yıllık %10-15
- **Volatilite**: Düşük (<%30)
- **Önerilen Sektörler**: Bankacılık, Gıda, Perakende, Holding
- **Amaç**: Sermaye koruması ve kararlı gelir

#### Orta Risk
- **Hedef Kitle**: Dengeli yatırımcılar
- **Beklenen Getiri**: Yıllık %15-25
- **Volatilite**: Orta (%30-50)
- **Önerilen Sektörler**: Bankacılık, Enerji, İnşaat, Otomotiv, Teknoloji
- **Amaç**: Risk-getiri dengesi

#### Yüksek Risk
- **Hedef Kitle**: Agresif yatırımcılar
- **Beklenen Getiri**: Yıllık %25+
- **Volatilite**: Yüksek (>%50)
- **Önerilen Sektörler**: Teknoloji, Savunma, Enerji, Havacılık
- **Amaç**: Maksimum getiri potansiyeli

### Adım 2: Yatırım Sürenizi Belirleyin

#### Kısa Vade (6 ay)
- Momentum stratejileri
- Kısa vadeli trendler
- Yüksek likidite ihtiyacı olan yatırımcılar için

#### Orta Vade (1 yıl)
- Dengeli trend analizi
- Çoğu yatırımcı için önerilen
- Risk-getiri dengesi optimal

#### Uzun Vade (5 yıl)
- Uzun vadeli büyüme
- İstikrarlı şirketler
- Birikim amaçlı yatırım

### Adım 3: Sektör Tercihlerinizi Seçin (Opsiyonel)

**Mevcut Sektörler:**
- Bankacılık (AKBNK, GARAN, YKBNK, vb.)
- Teknoloji (ASELS, LOGO, TCELL, vb.)
- Enerji (AKSEN, TUPRS, ZOREN, vb.)
- Perakende (BIMAS, SOKM, MGROS, vb.)
- Gıda (ULKER, CCOLA, AEFES, vb.)
- Otomotiv (FROTO, TOASO, OTKAR, vb.)
- Savunma (ASELS, THYAO, vb.)
- İnşaat ve Gayrimenkul
- Demir-Çelik
- Holding
- Ve daha fazlası...

**Not:** Hiçbir sektör seçmezseniz, risk profilinize uygun tüm sektörler kullanılır.

### Adım 4: Portföy Ayarları

#### Maksimum Hisse Sayısı
- **5 Hisse**: Konsantre portföy, yüksek potansiyel getiri
- **10 Hisse**: Dengeli (Önerilen)
- **15-20 Hisse**: Yüksek çeşitlendirme, düşük risk

#### Yatırım Tutarı
- Portföye yatırmak istediğiniz toplam TL tutarı
- Sistem her hisse için TL bazında öneride bulunur

### Adım 5: Gelişmiş Ayarlar (Opsiyonel)

#### Koloni Büyüklüğü (20-200)
- **20-30**: Hızlı test için
- **50-100**: Dengeli performans (Önerilen)
- **100-200**: En iyi sonuç için (daha uzun süre)

#### Maksimum İterasyon (50-500)
- **50**: Hızlı yakınsama
- **100-200**: Dengeli (Önerilen)
- **300+**: Çok hassas sonuçlar

#### Min/Max Hisse Ağırlığı
- **Min Weight**: Bir hissenin alabileceği minimum ağırlık (genellikle %0)
- **Max Weight**: Bir hissenin alabileceği maksimum ağırlık
  - %30-40: Yüksek çeşitlendirme
  - %50: Dengeli (Önerilen)
  - %60+: Konsantre portföy

#### Risksiz Faiz Oranı
- Türkiye için güncel hazine faiz oranı
- Sharpe Ratio hesaplamasında kullanılır
- Güncel değer: %45 civarı (2024)

## Sonuçları Anlama

### Önerilen Hisseler
- Sistem tercihlerinize göre otomatik olarak hisse seçer
- Sektörel dengeli dağılım sağlar
- Risk profilinize uygun şirketleri önerir

### Portföy Metrikleri

#### Beklenen Getiri
- Yıllık beklenen portföy getirisi (%)
- Pozitif = Kar beklentisi
- Negatif = Zarar riski

#### Volatilite (Risk)
- Portföyün risk seviyesi (%)
- Düşük volatilite = Daha kararlı
- Yüksek volatilite = Daha dalgalı

#### Sharpe Ratio
- Risk-ayarlı getiri metriği
- **< 0**: Kötü
- **0-1**: Kabul edilebilir
- **1-2**: İyi
- **> 2**: Mükemmel

#### Sortino Ratio
- Aşağı yönlü risk-ayarlı getiri
- Sharpe Ratio'ya benzer ama sadece negatif volatiliteyi hesaplar
- Yüksek = Daha iyi

#### Max Drawdown
- Portföyün en büyük değer kaybı yüzdesi
- %-10 = Portföy maksimum %10 değer kaybedebilir
- Düşük = Daha iyi

#### Çeşitlendirme Oranı
- Portföyün ne kadar çeşitlendirildiği
- **> 1**: İyi çeşitlendirme
- **> 1.5**: Mükemmel çeşitlendirme

### Portföy Dağılımı

- **Pasta Grafik**: Her hissenin portföydeki yüzde ağırlığı
- **Detaylı Tablo**: Her hisse için TL bazında yatırım miktarı
- **Yakınsama Grafiği**: Algoritmanın optimizasyon süreci

## Önemli Notlar

1. **Otomatik Hisse Seçimi**: Kullanıcı hisse seçmez, sistem tercihlerinize göre önerir
2. **Sektörel Denge**: Sistem sektörlerden dengeli dağılım sağlar
3. **Risk Profili Uyumluluğu**: Önerilen hisseler risk profilinize uygundur
4. **Dinamik Optimizasyon**: Sistem her defasında farklı piyasa koşullarını analiz eder

## Örnek Kullanım Senaryoları

### Senaryo 1: Muhafazakar Yatırımcı
- **Risk**: Düşük
- **Süre**: Uzun vade
- **Sektörler**: Bankacılık, Gıda, Holding
- **Max Hisse**: 10
- **Tutar**: 100,000 TL

**Beklenen Sonuç**: Kararlı bankacılık hisseleri ve gıda sektörü ağırlıklı portföy

### Senaryo 2: Dengeli Yatırımcı
- **Risk**: Orta
- **Süre**: Orta vade
- **Sektörler**: Seçim yapma (otomatik)
- **Max Hisse**: 10
- **Tutar**: 50,000 TL

**Beklenen Sonuç**: Çeşitli sektörlerden dengeli portföy

### Senaryo 3: Agresif Yatırımcı
- **Risk**: Yüksek
- **Süre**: Kısa vade
- **Sektörler**: Teknoloji, Savunma, Enerji
- **Max Hisse**: 5
- **Tutar**: 200,000 TL

**Beklenen Sonuç**: Yüksek büyüme potansiyeli olan teknoloji ve savunma hisseleri

## Sorun Giderme

### "Veri çekilemedi" Hatası
- İnternet bağlantınızı kontrol edin
- Yahoo Finance servisi erişilebilir durumda mı?
- Farklı bir yatırım süresi deneyin

### "Yeterli veri yok" Hatası
- Bazı hisseler için yeterli geçmiş veri yok
- Daha kısa bir periyot seçin
- Farklı sektörler deneyin

### Optimizasyon Çok Uzun Sürüyor
- Koloni büyüklüğünü azaltın (örn: 30)
- Maksimum iterasyonu azaltın (örn: 50)
- Hisse sayısını azaltın

## İletişim ve Destek

Bu uygulama eğitim amaçlıdır. Gerçek yatırım kararları için profesyonel danışmanlık alınız.
