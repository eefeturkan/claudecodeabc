# BIST100 Portföy Optimizasyonu - Yapay Arı Kolonisi

BIST100 hisse senetleri için Yapay Arı Kolonisi (Artificial Bee Colony - ABC) algoritması kullanarak optimal portföy dağılımı hesaplayan web uygulaması.

## Özellikler

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

### Web Arayüzü
- Kullanıcı dostu modern tasarım
- İnteraktif grafikler (Plotly.js)
- Gerçek zamanlı optimizasyon sonuçları
- Pasta grafik ve tablo görünümleri

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
│   └── portfolio_optimizer.py   # ABC ile portföy optimizasyonu
├── frontend/
│   ├── static/
│   │   ├── css/style.css        # Stil dosyası
│   │   └── js/main.js           # Frontend JavaScript
│   └── templates/
│       └── index.html           # Ana sayfa
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

1. **Hisse Seçimi**: BIST100 hisselerinden en az 2 tanesini seçin
2. **Parametreleri Ayarlayın**:
   - Amaç fonksiyonu (Sharpe, Max Getiri, Min Risk)
   - Veri periyodu (6 ay, 1 yıl, 2 yıl, 5 yıl)
   - Koloni büyüklüğü (20-200)
   - Maksimum iterasyon (50-500)
   - Min/Max hisse ağırlıkları
   - Risksiz faiz oranı
3. **Optimizasyonu Başlatın**: "Optimizasyonu Başlat" butonuna tıklayın
4. **Sonuçları İnceleyin**:
   - Portföy metrikleri
   - Optimal ağırlık dağılımı
   - Yakınsama grafiği

### Python Scripti ile Test

```bash
python test_optimizer.py
```

## API Endpoints

### GET /api/stocks
BIST100 hisse listesini döndürür.

**Response:**
```json
{
  "success": true,
  "stocks": [
    {"symbol": "AKBNK", "name": "Akbank"},
    ...
  ]
}
```

### POST /api/optimize
Portföy optimizasyonunu çalıştırır.

**Request:**
```json
{
  "symbols": ["AKBNK", "GARAN", "THYAO"],
  "period": "1y",
  "objective": "sharpe",
  "colony_size": 50,
  "max_iterations": 100,
  "min_weight": 0.0,
  "max_weight": 0.5,
  "risk_free_rate": 0.10
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
