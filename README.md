# BIST100 Akıllı Portföy Danışmanı - Yapay Arı Kolonisi

BIST100 hisse senetleri için Yapay Arı Kolonisi (Artificial Bee Colony - ABC) algoritması kullanarak kişiselleştirilmiş portföy önerileri sunan akıllı yatırım danışmanı.

## Özellikler

### Kişiselleştirilmiş Öneri Sistemi
- **Otomatik Hisse Seçimi**: Risk profilinize ve tercihlerinize göre otomatik hisse önerisi
- **Risk Profilleme**: Düşük, Orta, Yüksek risk seviyeleri
- **Yatırım Süresi Optimizasyonu**: Kısa, Orta, Uzun vade stratejileri
- **Sektörel Filtreleme**: 15+ farklı sektör bazlı tercih sistemi
- **Akıllı Çeşitlendirme**: Sektörel dengeli hisse dağılımı

### Yapay Arı Kolonisi Algoritması
- **Employee Bees (İşçi Arılar)**: Mevcut çözümleri araştırır
- **Onlooker Bees (Gözlemci Arılar)**: İyi çözümleri seçer ve geliştirir
- **Scout Bees (Keşif Arıları)**: Yeni rastgele çözümler üretir
- Sharpe Ratio maksimizasyonu ile risk-getiri optimizasyonu

### Portföy Optimizasyonu
- Sharpe Ratio, Sortino Ratio, Maximum Drawdown hesaplamaları
- Çeşitlendirme metrikleri
- Minimum/Maksimum hisse ağırlık kısıtlamaları
- Yahoo Finance'ten gerçek zamanlı veri çekme

### Modern Web Arayüzü
- Kullanıcı dostu tercih toplama ekranı
- İnteraktif grafikler (Plotly.js)
- Gerçek zamanlı optimizasyon sonuçları
- Pasta grafik ve detaylı tablo görünümleri

## Proje Yapısı

```
bist100-abc-portfolio/
├── backend/
│   ├── __init__.py
│   ├── abc_algorithm.py         # ABC algoritması core
│   ├── app.py                   # Flask web server
│   ├── bist100_stocks.py        # BIST100 hisse listesi
│   ├── data_fetcher.py          # Yahoo Finance veri çekme
│   ├── metrics.py               # Portföy metrikleri
│   ├── portfolio_optimizer.py   # ABC ile portföy optimizasyonu
│   └── stock_classifier.py      # Sektör sınıflandırma ve öneri motoru
├── frontend/
│   ├── static/
│   │   ├── css/style.css        # Stil dosyası
│   │   └── js/main.js           # Frontend JavaScript
│   └── templates/
│       └── index.html           # Ana sayfa (tercih bazlı)
├── requirements.txt             # Python bağımlılıkları
├── test_optimizer.py            # Test scripti
└── README.md
```

## Kurulum

### 1. Python Bağımlılıklarını Yükleyin

```bash
pip install -r requirements.txt
```

### 2. Uygulamayı Başlatın

```bash
python backend/app.py
```

### 3. Web Arayüzünü Açın

Tarayıcınızda şu adresi açın:
```
http://localhost:5000
```

## Kullanım

### Web Arayüzü Üzerinden

1. **Risk Profilinizi Seçin**:
   - Düşük Risk: Kararlı gelir, düşük volatilite
   - Orta Risk: Dengeli risk-getiri yaklaşımı
   - Yüksek Risk: Yüksek getiri potansiyeli

2. **Yatırım Sürenizi Belirleyin**:
   - Kısa Vade: 6 ay
   - Orta Vade: 1 yıl
   - Uzun Vade: 5 yıl

3. **Sektör Tercihlerinizi Seçin** (Opsiyonel):
   - Bankacılık, Teknoloji, Enerji, Perakende vb.
   - Boş bırakırsanız risk profilinize uygun tüm sektörler kullanılır

4. **Portföy Ayarları**:
   - Maksimum hisse sayısı (5/10/15/20)
   - Yatırım tutarı (TL)

5. **Portföy Önerisi Al**: "Portföy Önerisi Al" butonuna tıklayın

6. **Sonuçları İnceleyin**:
   - Sizin için seçilen hisseler
   - Optimal portföy dağılımı
   - Portföy metrikleri
   - Detaylı yatırım planı
   - Algoritma yakınsama grafiği

### Python Scripti ile Test

```bash
python test_optimizer.py
```

## API Endpoints

### GET /api/sectors
Mevcut sektör listesini döndürür.

**Response:**
```json
{
  "success": true,
  "sectors": ["Bankacılık", "Teknoloji", "Enerji", ...]
}
```

### GET /api/preferences
Risk profilleri ve yatırım periyotları hakkında bilgi.

**Response:**
```json
{
  "success": true,
  "risk_profiles": {...},
  "investment_periods": {...}
}
```

### POST /api/recommend
Kullanıcı tercihlerine göre hisse önerir.

**Request:**
```json
{
  "risk_profile": "orta",
  "investment_period": "orta",
  "sectors": ["Teknoloji", "Bankacılık"],
  "max_stocks": 10
}
```

**Response:**
```json
{
  "success": true,
  "recommendation": {
    "recommended_stocks": ["AKBNK", "GARAN", ...],
    "stock_count": 10
  }
}
```

### POST /api/optimize-with-preferences
Kullanıcı tercihlerine göre hisse önerir VE portföy optimizasyonu yapar.

**Request:**
```json
{
  "risk_profile": "orta",
  "investment_period": "orta",
  "sectors": ["Teknoloji", "Bankacılık"],
  "max_stocks": 10,
  "colony_size": 50,
  "max_iterations": 100,
  "min_weight": 0.0,
  "max_weight": 0.5,
  "risk_free_rate": 0.10,
  "investment_amount": 100000
}
```

**Response:**
```json
{
  "success": true,
  "objective": "sharpe",
  "weights": [
    {
      "symbol": "AKBNK",
      "name": "Akbank",
      "weight": 0.35,
      "percentage": 35.0
    },
    ...
  ],
  "metrics": {
    "expected_return": 0.15,
    "volatility": 0.25,
    "sharpe_ratio": 0.20,
    "sortino_ratio": 0.28,
    "max_drawdown": -0.18,
    "diversification_ratio": 1.42
  },
  "history": {
    "best_fitness": [...],
    "mean_fitness": [...]
  }
}
```

### POST /api/validate
Hisse sembollerinin geçerliliğini kontrol eder.

### GET /api/stock-info/<symbol>
Belirli bir hisse hakkında detaylı bilgi.

## Yapay Arı Kolonisi Algoritması

ABC algoritması, bal arılarının yiyecek arama davranışından esinlenmiş bir sürü zekası optimizasyon algoritmasıdır.

### Algoritma Akışı

1. **Başlangıç**: Rastgele portföy çözümleri üret
2. **İşçi Arı Fazı**: Mevcut çözümleri komşulukta araştır
3. **Gözlemci Arı Fazı**: İyi çözümleri olasılıkla seç ve geliştir
4. **Keşif Arısı Fazı**: Başarısız çözümleri yenileriyle değiştir
5. **Tekrarla**: 2-4 adımlarını maksimum iterasyon sayısı kadar tekrarla

### Fitness Fonksiyonu

Portföy optimizasyonu için Sharpe Ratio kullanılır:

```
Sharpe Ratio = (Portföy Getirisi - Risksiz Faiz) / Portföy Volatilitesi
```

## Portföy Metrikleri

- **Beklenen Getiri**: Yıllık beklenen portföy getirisi
- **Volatilite**: Portföy riski (standart sapma)
- **Sharpe Ratio**: Risk-ayarlı getiri
- **Sortino Ratio**: Aşağı yönlü risk-ayarlı getiri
- **Maximum Drawdown**: En büyük değer kaybı yüzdesi
- **Diversification Ratio**: Çeşitlendirme oranı
- **VaR (Value at Risk)**: Belirli güven aralığında maksimum kayıp
- **CVaR (Conditional VaR)**: Koşullu risk değeri

## Teknolojiler

### Backend
- **Python 3.8+**
- **Flask**: Web framework
- **yfinance**: Yahoo Finance API
- **NumPy**: Sayısal hesaplamalar
- **Pandas**: Veri analizi
- **SciPy**: İstatistiksel fonksiyonlar

### Frontend
- **HTML5/CSS3**: Modern web standartları
- **JavaScript (ES6+)**: Dinamik arayüz
- **Plotly.js**: İnteraktif grafikler
- **Fetch API**: Backend iletişimi

## Parametreler ve Öneriler

### Koloni Büyüklüğü
- **20-30**: Hızlı test için
- **50-100**: Dengeli performans (önerilen)
- **100-200**: En iyi sonuç için

### Maksimum İterasyon
- **50**: Hızlı yakınsama
- **100-200**: Dengeli (önerilen)
- **300+**: Çok hassas sonuçlar için

### Veri Periyodu
- **6 ay**: Kısa vadeli trend
- **1 yıl**: Dengeli (önerilen)
- **2-5 yıl**: Uzun vadeli analiz

### Risk Parametreleri
- **Min Weight**: Genellikle %0
- **Max Weight**: %30-50 arası (çeşitlendirme için)
- **Risk-Free Rate**: Türkiye için %10-40

## Limitasyonlar ve Notlar

1. **Veri Kaynağı**: Yahoo Finance API kullanılır, veri gecikmesi olabilir
2. **Geçmiş Performans**: Geçmiş veriler gelecek performansı garanti etmez
3. **İşlem Maliyetleri**: Komisyon ve vergiler hesaba katılmamıştır
4. **Piyasa Koşulları**: Ani değişimler modelde yer almaz

## Lisans

Bu proje eğitim amaçlıdır. Ticari kullanım öncesinde gerekli izinler alınmalıdır.

## Uyarı

**ÖNEMLİ**: Bu uygulama sadece eğitim ve araştırma amaçlıdır. Gerçek yatırım kararları almadan önce:
- Profesyonel finansal danışmanlık alın
- Piyasa risklerini değerlendirin
- Kişisel risk toleransınızı göz önünde bulundurun
- Yatırım yapmadan önce detaylı araştırma yapın

## Katkıda Bulunma

Hata raporları ve öneriler için issue açabilirsiniz.

## İletişim

Sorularınız için GitHub üzerinden ulaşabilirsiniz.

---

**Not**: BIST100 ve hisse isimleri Borsa İstanbul'a aittir. Bu proje resmi bir Borsa İstanbul ürünü değildir.
