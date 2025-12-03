"""
BIST100 Hisse Senetleri Sektör Sınıflandırması ve Filtreleme
Performans Bazlı Akıllı Seçim Sistemi
"""

import yfinance as yf
import numpy as np
import json
import os
from datetime import datetime, timedelta

# =====================================================
# CACHE SISTEMI - API cagrilarini azaltmak icin
# =====================================================
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'stock_performance_cache.json')
CACHE_DURATION_HOURS = 24  # Cache 24 saat gecerli

def _ensure_cache_dir():
    """Cache dizinini olustur"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def _load_cache():
    """Cache dosyasini yukle"""
    _ensure_cache_dir()
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_cache(cache_data):
    """Cache dosyasini kaydet"""
    _ensure_cache_dir()
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

def _is_cache_valid(cache_entry):
    """Cache girisinin gecerli olup olmadigini kontrol et"""
    if not cache_entry or 'timestamp' not in cache_entry:
        return False
    cache_time = datetime.fromisoformat(cache_entry['timestamp'])
    return datetime.now() - cache_time < timedelta(hours=CACHE_DURATION_HOURS)

def clear_cache():
    """Cache'i temizle (manuel kullanim icin)"""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print("[CACHE] Cache temizlendi")


class NoStocksFoundError(Exception):
    """
    Volatilite filtresinden gecen hisse bulunamadiginda firlatilir.
    Kullaniciya anlamli hata mesaji gostermek icin kullanilir.
    """
    def __init__(self, message, risk_profile, volatility_threshold, sectors, total_stocks_checked):
        super().__init__(message)
        self.risk_profile = risk_profile
        self.volatility_threshold = volatility_threshold
        self.sectors = sectors
        self.total_stocks_checked = total_stocks_checked

# Sektörel sınıflandırma - TÜM BIST HİSSELERİ
STOCK_SECTORS = {
    # Bankacılık ve Finans
    'AKBNK': 'Bankacılık',
    'GARAN': 'Bankacılık',
    'HALKB': 'Bankacılık',
    'ISCTR': 'Bankacılık',
    'SKBNK': 'Bankacılık',
    'TSKB': 'Bankacılık',
    'VAKBN': 'Bankacılık',
    'YKBNK': 'Bankacılık',
    'ALBRK': 'Bankacılık',
    'ISMEN': 'Finans',
    'UNLU': 'Finans',
    'GEDIK': 'Finans',
    'PRKME': 'Finans',
    'VAKFN': 'Finans',
    'SEKFK': 'Finans',
    'SNKRN': 'Finans',
    'PSDTC': 'Finans',
    'COSMO': 'Finans',
    'UFUK': 'Finans',

    # Teknoloji ve Yazılım
    'LOGO': 'Teknoloji',
    'LINK': 'Teknoloji',
    'NETAS': 'Teknoloji',
    'TTKOM': 'Teknoloji',
    'TCELL': 'Teknoloji',
    'KRONT': 'Teknoloji',
    'VBTYZ': 'Teknoloji',
    'TKNSA': 'Teknoloji',
    'INDES': 'Teknoloji',
    'MTRKS': 'Teknoloji',
    'PKART': 'Teknoloji',
    'PAPIL': 'Teknoloji',
    'KONTR': 'Teknoloji',
    'KFEIN': 'Teknoloji',
    'REEDR': 'Teknoloji',

    # Savunma ve Havacılık
    'ASELS': 'Savunma',
    'THYAO': 'Havacılık',
    'PGSUS': 'Havacılık',
    'TAVHL': 'Havacılık',
    'CLEBI': 'Havacılık',

    # Enerji
    'AKSEN': 'Enerji',
    'AYEN': 'Enerji',
    'AYDEM': 'Enerji',
    'ZOREN': 'Enerji',
    'AKENR': 'Enerji',
    'AKFYE': 'Enerji',
    'ENJSA': 'Enerji',
    'TUPRS': 'Enerji',
    'TGSAS': 'Ticaret',
    'PETKM': 'Enerji',
    'AYGAZ': 'Enerji',
    'ODAS': 'Enerji',
    'EUPWR': 'Enerji',
    'EUREN': 'Enerji',
    'ANELE': 'Enerji',
    'CONSE': 'Enerji',
    'SMART': 'Enerji',
    'SMRTG': 'Enerji',
    'ZEDUR': 'Enerji',
    'SUNTK': 'Enerji',
    'IPEKE': 'Enerji',
    'ALFAS': 'Enerji',
    'PAMEL': 'Enerji',
    'MEPET': 'Enerji',
    'PKENT': 'Enerji',
    'TRCAS': 'Enerji',
    'PRKAB': 'Enerji',

    # Perakende
    'BIMAS': 'Perakende',
    'SOKM': 'Perakende',
    'MGROS': 'Perakende',
    'BIZIM': 'Perakende',
    'MAVI': 'Perakende',
    'KENT': 'Perakende',
    'CRFSA': 'Perakende',
    'VAKKO': 'Perakende',
    'MPARK': 'Perakende',

    # Gıda
    'ULKER': 'Gıda',
    'CCOLA': 'Gıda',
    'AEFES': 'Gıda',
    'PNSUT': 'Gıda',
    'TATEN': 'Gıda',
    'PENGD': 'Gıda',
    'TUKAS': 'Gıda',
    'SELGD': 'Gıda',
    'KERVT': 'Gıda',
    'BANVT': 'Gıda',
    'TBORG': 'Gıda',
    'SELVA': 'Gıda',
    'TABGD': 'Gıda',
    'KRSTL': 'Gıda',
    'YYLGD': 'Gıda',
    'YAYLA': 'Gıda',
    'SUWEN': 'Gıda',

    # Otomotiv
    'FROTO': 'Otomotiv',
    'TOASO': 'Otomotiv',
    'DOAS': 'Otomotiv',
    'OTKAR': 'Otomotiv',
    'TTRAK': 'Otomotiv',
    'ASUZU': 'Otomotiv',
    'KARSN': 'Otomotiv',
    'KATMR': 'Otomotiv',
    'TMSN': 'Otomotiv',
    'PARSN': 'Otomotiv',

    # İnşaat
    'ENKAI': 'İnşaat',
    'TKFEN': 'İnşaat',
    'IZOCM': 'İnşaat',
    'BAKAB': 'İnşaat',
    'BRLSM': 'İnşaat',

    # Gayrimenkul (GYO)
    'EKGYO': 'Gayrimenkul',
    'ALGYO': 'Gayrimenkul',
    'ISGYO': 'Gayrimenkul',
    'VKGYO': 'Gayrimenkul',
    'HLGYO': 'Gayrimenkul',
    'KLGYO': 'Gayrimenkul',
    'NUGYO': 'Gayrimenkul',
    'OZKGY': 'Gayrimenkul',
    'PEGYO': 'Gayrimenkul',
    'PEKGY': 'Gayrimenkul',
    'MRGYO': 'Gayrimenkul',
    'MTRYO': 'Gayrimenkul',
    'SNGYO': 'Gayrimenkul',
    'TDGYO': 'Gayrimenkul',
    'TRGYO': 'Gayrimenkul',
    'TSGYO': 'Gayrimenkul',
    'YESIL': 'Gayrimenkul',
    'YGGYO': 'Gayrimenkul',
    'AKFGY': 'Gayrimenkul',
    'DAPGM': 'Gayrimenkul',
    'IEYHO': 'Gayrimenkul',
    'KRPLS': 'Gayrimenkul',
    'KZBGY': 'Gayrimenkul',
    'RGYAS': 'Gayrimenkul',
    'RYGYO': 'Gayrimenkul',
    'SEGYO': 'Gayrimenkul',
    'SRVGY': 'Gayrimenkul',
    'VKFYO': 'Gayrimenkul',
    'YGYO': 'Gayrimenkul',

    # Çimento
    'AFYON': 'Çimento',
    'AKCNS': 'Çimento',
    'BTCIM': 'Çimento',
    'BUCIM': 'Çimento',
    'CIMSA': 'Çimento',
    'KONYA': 'Çimento',
    'OYAKC': 'Çimento',
    'BSOKE': 'Çimento',
    'CMENT': 'Çimento',
    'GOLTS': 'Çimento',
    'GLYHO': 'Holding',

    # Metal
    'BRSAN': 'Metal',
    'BOBET': 'Metal',
    'SARKY': 'Metal',
    'ERBOS': 'Metal',
    'FORMT': 'Metal',
    'TUCLK': 'Metal',
    'YKSLN': 'Metal',

    # Demir-Çelik
    'EREGL': 'Demir-Çelik',
    'KRDMA': 'Demir-Çelik',
    'KRDMB': 'Demir-Çelik',
    'KRDMD': 'Demir-Çelik',
    'ISDMR': 'Demir-Çelik',
    'CEMTS': 'Demir-Çelik',
    'CEMAS': 'Demir-Çelik',

    # Tekstil ve Deri
    'KORDS': 'Tekstil',
    'YUNSA': 'Tekstil',
    'YATAS': 'Tekstil',
    'BLCYT': 'Tekstil',
    'SNPAM': 'Tekstil',
    'DESA': 'Tekstil',
    'KRTEK': 'Tekstil',
    'SONME': 'Tekstil',
    'SKTAS': 'Tekstil',

    # Cam ve Seramik
    'SISE': 'Cam',
    'TRILC': 'Cam',
    'KUTPO': 'Seramik',
    'USAK': 'Seramik',
    'KLRHO': 'Seramik',
    'QUAGR': 'Seramik',

    # Holding
    'SAHOL': 'Holding',
    'KCHOL': 'Holding',
    'AGHOL': 'Holding',
    'DOHOL': 'Holding',
    'NTHOL': 'Holding',
    'ITTFH': 'Holding',
    'POLHO': 'Holding',
    'METRO': 'Holding',
    'ALARK': 'Holding',
    'GOZDE': 'Holding',
    'DEVA': 'Holding',
    'ECZYT': 'Holding',
    'BRYAT': 'Holding',
    'SANKO': 'Holding',
    'KRVGD': 'Holding',

    # Kimya
    'ALKIM': 'Kimya',
    'GUBRF': 'Kimya',
    'SODA': 'Kimya',
    'AKSA': 'Kimya',
    'SASA': 'Kimya',
    'BRISA': 'Kimya',
    'GOODY': 'Kimya',
    'KLKIM': 'Kimya',
    'MERCN': 'Kimya',
    'HEKTS': 'Kimya',
    'BAGFS': 'Kimya',
    'EGGUB': 'Kimya',
    'TARKM': 'Kimya',
    'SEYKM': 'Kimya',
    'SODSN': 'Kimya',
    'TMPOL': 'Kimya',
    'KOPOL': 'Kimya',

    # Elektrik-Elektronik
    'ARCLK': 'Elektrik-Elektronik',
    'VESTL': 'Elektrik-Elektronik',
    'VESBE': 'Elektrik-Elektronik',
    'KLMSN': 'Elektrik-Elektronik',
    'SILVR': 'Elektrik-Elektronik',

    # Sağlık ve İlaç
    'LKMNH': 'Sağlık',
    'MLP': 'Sağlık',
    'ECILC': 'Sağlık',
    'GENIL': 'Sağlık',
    'RTALB': 'Sağlık',
    'SELEC': 'Sağlık',
    'BIOEN': 'Sağlık',

    # Sigorta
    'ANSGR': 'Sigorta',
    'ANHYT': 'Sigorta',
    'RAYSG': 'Sigorta',
    'TURSG': 'Sigorta',
    'AGESA': 'Sigorta',

    # Spor
    'GSRAY': 'Spor',
    'FENER': 'Spor',
    'BJKAS': 'Spor',
    'TSPOR': 'Spor',

    # Denizcilik
    'GSDHO': 'Holding',

    # Madencilik
    'KOZAA': 'Madencilik',
    'KOZAL': 'Madencilik',

    # Lojistik ve Ulaşım
    'RYSAS': 'Lojistik',
    'RALYH': 'Lojistik',
    'KMPUR': 'Lojistik',
    'TLMAN': 'Lojistik',
    'PASEU': 'Lojistik',

    # Kağıt ve Ambalaj
    'KARTN': 'Kağıt',
    'VKING': 'Kağıt',
    'BARMA': 'Kağıt',
    'TIRE': 'Kağıt',
    'TEZOL': 'Kağıt',
    'SAYAS': 'Kağıt',

    # Tarım
    'KAYSE': 'Tarım',
    'MEKAG': 'Tarım',

    # Savunma Sanayii (ek)
    'ASTOR': 'Savunma',

    # Makine ve Endüstriyel
    'EGEEN': 'Makine',
    'GESAN': 'Makine',
    'GMTAS': 'Makine',
    'ULUFA': 'Makine',
    'UZERB': 'Makine',
    'YEOTK': 'Makine',
    'BRKSN': 'Makine',
    'POLTK': 'Makine',
    'RUBNS': 'Makine',

    # Mobilya
    'FLAP': 'Mobilya',
    'RODRG': 'Mobilya',

    # Giyim
    'ROYAL': 'Giyim',
    'SANFM': 'Giyim',

    # Diğer
    'ALMAD': 'Gıda',
    'GRSEL': 'Finans',
    'ICBCT': 'Finans',
    'KTLEV': 'Finans',
    'KTSKR': 'Gıda',
    'OZRDN': 'Kimya',
    'OZSUB': 'Gıda',
    'PRZMA': 'Teknoloji',
    'QUOGR': 'Seramik',
    'SAMAT': 'Kimya',
    'SANEL': 'Elektrik-Elektronik',
    'SEGMN': 'Tekstil',
    'SNICA': 'Kimya',
    'TURGG': 'Finans',
    'ULUSE': 'Elektrik-Elektronik',
    'ULUUN': 'Gıda',
    'VANGD': 'Gıda',
    'VERTU': 'Teknoloji',
    'VERUS': 'Finans',
}

# Risk Profilleri (volatilite bazlı)
# NOT: BIST gelismekte olan piyasa oldugu icin volatilite esikleri
# gelismis piyasalara gore daha yuksek tutulmustur
RISK_PROFILES = {
    'düşük': {
        'sectors': [
            'Bankacılık', 'Gıda', 'Perakende', 'Holding', 'Sigorta',
            'Sağlık', 'Finans', 'Gayrimenkul'  # Stabil sektorler eklendi
        ],
        'volatility_threshold': 0.45,  # %45 - BIST icin gercekci dusuk risk esigi
        'description': 'Kararlı gelir, düşük risk'
    },
    'orta': {
        'sectors': [
            'Bankacılık', 'Enerji', 'İnşaat', 'Otomotiv', 'Teknoloji',
            'Gıda', 'Perakende', 'Kimya', 'Elektrik-Elektronik',
            'Cam', 'Tekstil', 'Lojistik', 'Metal', 'Çimento',  # Orta riskli sektorler eklendi
            'Makine', 'Seramik', 'Kağıt'
        ],
        'volatility_threshold': 0.65,  # %65 - Dengeli risk
        'description': 'Dengeli risk-getiri'
    },
    'yüksek': {
        'sectors': [
            'Teknoloji', 'Savunma', 'Enerji', 'Havacılık', 'Demir-Çelik',
            'Madencilik', 'Spor', 'Tarım', 'Mobilya', 'Giyim', 'Ticaret'  # Yuksek riskli sektorler eklendi
        ],
        'volatility_threshold': 1.0,   # %100 - Sinirsiz (yuksek risk toleransi)
        'description': 'Yüksek getiri potansiyeli, yüksek risk'
    }
}

# Yatırım süresi - periyot eşleştirmesi
INVESTMENT_PERIODS = {
    'kısa': {
        'period': '6mo',
        'description': 'Kısa vadeli (6 ay)',
        'focus': 'Momentum ve kısa vadeli trendler'
    },
    'orta': {
        'period': '1y',
        'description': 'Orta vadeli (1 yıl)',
        'focus': 'Dengeli trend analizi'
    },
    'uzun': {
        'period': '5y',
        'description': 'Uzun vadeli (5 yıl)',
        'focus': 'Uzun vadeli büyüme ve istikrar'
    }
}


def get_stocks_by_sector(sector):
    """
    Belirli bir sektördeki hisseleri döndürür

    Args:
        sector (str): Sektör adı

    Returns:
        list: Hisse sembolleri
    """
    return [symbol for symbol, sec in STOCK_SECTORS.items() if sec == sector]


def get_available_sectors():
    """
    Mevcut tüm sektörleri döndürür

    Returns:
        list: Benzersiz sektör listesi
    """
    return sorted(list(set(STOCK_SECTORS.values())))


def calculate_stock_performance(symbol, period='1y'):
    """
    Bir hissenin performans metriklerini hesaplar
    CACHE DESTEKLI: Ayni hisse icin tekrar API cagrisi yapmaz

    Args:
        symbol (str): Hisse sembolü
        period (str): Veri periyodu ('6mo', '1y', '5y')

    Returns:
        dict: Performans metrikleri (sharpe, volatility, return, score)
    """
    # Cache key olustur
    cache_key = f"{symbol}_{period}"

    # Cache'den kontrol et
    cache = _load_cache()
    if cache_key in cache and _is_cache_valid(cache[cache_key]):
        print(f"    [CACHE] {symbol}: Cache'den yuklendi")
        return cache[cache_key]['data']

    # Cache'de yoksa veya suresi dolmussa API'den cek
    try:
        print(f"    [API] {symbol}: Yahoo Finance'den cekiliyor...")
        ticker = yf.Ticker(f"{symbol}.IS")
        hist = ticker.history(period=period)

        if hist.empty or len(hist) < 20:
            return None

        # Günlük getiriler
        returns = hist['Close'].pct_change().dropna()

        if len(returns) < 10:
            return None

        # Metrikler
        mean_return = returns.mean() * 252  # Yıllık ortalama getiri
        volatility = returns.std() * np.sqrt(252)  # Yıllık volatilite

        # Sharpe Ratio (risksiz oran %15 varsayalım - Türkiye için)
        risk_free_rate = 0.15
        sharpe_ratio = (mean_return - risk_free_rate) / volatility if volatility > 0 else 0

        # Toplam getiri
        total_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1

        # Performans skoru (ağırlıklı)
        # Sharpe önemli ama pozitif getiri de lazım
        score = (sharpe_ratio * 0.4) + (total_return * 0.3) + ((1 - min(volatility, 1)) * 0.3)

        result = {
            'symbol': symbol,
            'sharpe_ratio': sharpe_ratio,
            'volatility': volatility,
            'annual_return': mean_return,
            'total_return': total_return,
            'score': score
        }

        # Cache'e kaydet
        cache[cache_key] = {
            'timestamp': datetime.now().isoformat(),
            'data': result
        }
        _save_cache(cache)

        return result
    except Exception as e:
        print(f"Performans hesaplama hatası ({symbol}): {e}")
        return None


def rank_stocks_by_performance(symbols, period='1y', top_n=None, volatility_threshold=None):
    """
    Hisseleri performanslarına göre sıralar ve volatilite filtreleme uygular

    Args:
        symbols (list): Hisse sembolleri
        period (str): Veri periyodu
        top_n (int): En iyi kaç hisse döndürülsün (None ise hepsi)
        volatility_threshold (float): Maksimum kabul edilebilir volatilite (None ise sınırsız)

    Returns:
        list: Performansa göre sıralı hisse listesi
    """
    performances = []

    for symbol in symbols:
        perf = calculate_stock_performance(symbol, period)
        if perf:
            # PERFORMANS FİLTRELERİ
            # 1. Volatilite filtresi
            # 2. Sharpe Ratio > 0 (negatif risk-ayarlı getiri kabul edilmez)
            # 3. Score > 0 (genel performans pozitif olmalı)

            volatility_ok = volatility_threshold is None or perf['volatility'] <= volatility_threshold
            sharpe_ok = perf['sharpe_ratio'] > 0
            score_ok = perf['score'] > 0

            if volatility_threshold is not None:
                if volatility_ok and sharpe_ok and score_ok:
                    performances.append(perf)
                    print(f"    [OK] {symbol}: Vol={perf['volatility']:.2%}, Sharpe={perf['sharpe_ratio']:.2f}, Score={perf['score']:.2f} (KABUL)")
                else:
                    reasons = []
                    if not volatility_ok:
                        reasons.append(f"Vol={perf['volatility']:.2%}>{volatility_threshold:.0%}")
                    if not sharpe_ok:
                        reasons.append(f"Sharpe={perf['sharpe_ratio']:.2f}<0")
                    if not score_ok:
                        reasons.append(f"Score={perf['score']:.2f}<0")
                    print(f"    [X] {symbol}: {', '.join(reasons)} (REDDEDILDI)")
            else:
                # Volatilite limiti yoksa sadece Sharpe ve Score kontrolü
                if sharpe_ok and score_ok:
                    performances.append(perf)
                else:
                    print(f"    [X] {symbol}: Kötü performans (Sharpe={perf['sharpe_ratio']:.2f}, Score={perf['score']:.2f})")

    # Skora göre sırala (yüksekten düşüğe)
    performances.sort(key=lambda x: x['score'], reverse=True)

    # Sadece sembolleri döndür
    ranked_symbols = [p['symbol'] for p in performances]

    if top_n:
        return ranked_symbols[:top_n]
    return ranked_symbols


def filter_stocks_by_preferences(risk_profile='orta', investment_period='orta', sectors=None, max_stocks=10, use_performance_ranking=True):
    """
    Kullanıcı tercihlerine göre hisse filtreler
    PERFORMANS BAZLI SEÇİM + VOLATİLİTE FİLTRESİ:
    Risk profiline uygun volatilitedeki en iyi performanslı hisseler seçilir

    Args:
        risk_profile (str): 'düşük', 'orta', 'yüksek'
        investment_period (str): 'kısa', 'orta', 'uzun' - yatirim suresi
        sectors (list): İstenen sektörler (None ise tüm sektörler)
        max_stocks (int): Maksimum hisse sayısı
        use_performance_ranking (bool): Performans sıralaması kullanılsın mı

    Returns:
        list: Filtrelenmiş ve sıralanmış hisse sembolleri
    """
    # Risk profilini al
    profile = RISK_PROFILES.get(risk_profile, RISK_PROFILES['orta'])

    # Volatilite eşiği - HER ZAMAN risk profiline göre uygulanır
    volatility_threshold = profile['volatility_threshold']

    # Yatırım süresine göre periyot belirle (INVESTMENT_PERIODS'dan al)
    period_info = INVESTMENT_PERIODS.get(investment_period, INVESTMENT_PERIODS['orta'])
    period = period_info['period']

    # Sektör seçimi: Kullanıcı seçimi varsa öncelik ona, yoksa risk profiline göre
    if sectors:
        allowed_sectors = sectors
    else:
        allowed_sectors = profile['sectors']

    # Sektörlere göre hisseleri filtrele
    filtered_stocks = []
    for symbol, sector in STOCK_SECTORS.items():
        if sector in allowed_sectors:
            filtered_stocks.append(symbol)

    print(f"\n{'='*60}")
    print(f"[Filtre] Risk Profili: {risk_profile.upper()}")
    print(f"[Filtre] Volatilite Esigi: <= {volatility_threshold:.0%}")
    print(f"[Filtre] Sektorler: {allowed_sectors}")
    print(f"[Filtre] Filtrelenmis hisse havuzu: {len(filtered_stocks)} hisse")
    print(f"{'='*60}")

    # Performans bazlı sıralama
    if use_performance_ranking and len(filtered_stocks) > 0:
        print(f"\n[Performans Analizi] {len(filtered_stocks)} hisse analiz ediliyor...")
        print(f"[Volatilite Filtresi] Sadece <= {volatility_threshold:.0%} volatiliteli hisseler kabul edilecek\n")

        # Sektör bazlı performans analizi
        stocks_by_sector = {}
        for symbol in filtered_stocks:
            sector = STOCK_SECTORS[symbol]
            if sector not in stocks_by_sector:
                stocks_by_sector[sector] = []
            stocks_by_sector[sector].append(symbol)

        # Her sektörden en iyi performans gösterenleri al (volatilite filtreli)
        balanced_stocks = []
        stocks_per_sector = max(1, max_stocks // len(stocks_by_sector))

        for sector, symbols in stocks_by_sector.items():
            print(f"\n  [{sector}] sektoru analiz ediliyor...")
            # Sektordeki hisseleri performansa gore sirala VE volatilite filtrele
            ranked = rank_stocks_by_performance(
                symbols,
                period,
                top_n=stocks_per_sector,
                volatility_threshold=volatility_threshold  # Volatilite filtresi
            )
            balanced_stocks.extend(ranked)
            if ranked:
                print(f"  [{sector}] Secilen hisseler: {ranked}")
            else:
                print(f"  [{sector}] Uygun hisse bulunamadi (volatilite cok yuksek)")

        # Max hisse sayısını aşıyorsa, genel performansa göre kes
        if len(balanced_stocks) > max_stocks:
            # Tüm seçilenleri tekrar sırala ve en iyileri al
            balanced_stocks = rank_stocks_by_performance(
                balanced_stocks,
                period,
                top_n=max_stocks,
                volatility_threshold=volatility_threshold
            )

        # Hala eksikse, diğer sektörlerden ekle
        elif len(balanced_stocks) < max_stocks:
            remaining_needed = max_stocks - len(balanced_stocks)
            remaining_stocks = [s for s in filtered_stocks if s not in balanced_stocks]
            print(f"\n[Ek Arama] {remaining_needed} hisse daha gerekli, diger hisseler kontrol ediliyor...")
            additional = rank_stocks_by_performance(
                remaining_stocks,
                period,
                top_n=remaining_needed,
                volatility_threshold=volatility_threshold
            )
            balanced_stocks.extend(additional)

        print(f"\n{'='*60}")
        print(f"[SONUC] Risk: {risk_profile.upper()} | Volatilite Esigi: <={volatility_threshold:.0%}")
        print(f"[SONUC] Secilen {len(balanced_stocks)} hisse: {balanced_stocks}")
        print(f"{'='*60}\n")

        # HATA KONTROLU: Hic hisse bulunamadiysa kullaniciya anlamli mesaj ver
        if len(balanced_stocks) == 0:
            sector_names = ", ".join(allowed_sectors) if isinstance(allowed_sectors, list) else str(allowed_sectors)
            raise NoStocksFoundError(
                message=f"Secilen sektorlerde ({sector_names}) {risk_profile} risk profiline uygun hisse bulunamadi.",
                risk_profile=risk_profile,
                volatility_threshold=volatility_threshold,
                sectors=allowed_sectors,
                total_stocks_checked=len(filtered_stocks)
            )

        return balanced_stocks[:max_stocks]

    else:
        # Performans sıralaması kapalıysa eski yöntem
        stocks_by_sector = {}
        for symbol in filtered_stocks:
            sector = STOCK_SECTORS[symbol]
            if sector not in stocks_by_sector:
                stocks_by_sector[sector] = []
            stocks_by_sector[sector].append(symbol)

        balanced_stocks = []
        if len(stocks_by_sector) == 0:
            return []

        stocks_per_sector = max(1, max_stocks // len(stocks_by_sector))

        for sector, symbols in stocks_by_sector.items():
            balanced_stocks.extend(symbols[:stocks_per_sector])

        if len(balanced_stocks) < max_stocks:
            remaining = max_stocks - len(balanced_stocks)
            for symbols in stocks_by_sector.values():
                for symbol in symbols:
                    if symbol not in balanced_stocks:
                        balanced_stocks.append(symbol)
                        if len(balanced_stocks) >= max_stocks:
                            break
                if len(balanced_stocks) >= max_stocks:
                    break

        return balanced_stocks[:max_stocks]


def get_recommendation_summary(risk_profile, investment_period, sectors, max_stocks):
    """
    Öneri özetini döndürür

    Args:
        risk_profile (str): Risk profili
        investment_period (str): Yatırım süresi
        sectors (list): Seçili sektörler
        max_stocks (int): Max hisse sayısı

    Returns:
        dict: Öneri özeti
    """
    profile = RISK_PROFILES.get(risk_profile, RISK_PROFILES['orta'])
    period = INVESTMENT_PERIODS.get(investment_period, INVESTMENT_PERIODS['orta'])

    # investment_period parametresi eklendi - period tutarliligi saglandi
    recommended_stocks = filter_stocks_by_preferences(
        risk_profile=risk_profile,
        investment_period=investment_period,
        sectors=sectors,
        max_stocks=max_stocks
    )

    return {
        'risk_profile': {
            'level': risk_profile,
            'description': profile['description'],
            'recommended_sectors': profile['sectors']
        },
        'investment_period': {
            'duration': investment_period,
            'period': period['period'],
            'description': period['description'],
            'focus': period['focus']
        },
        'selected_sectors': sectors if sectors else profile['sectors'],
        'recommended_stocks': recommended_stocks,
        'stock_count': len(recommended_stocks),
        'max_stocks': max_stocks
    }


def get_sector_statistics():
    """
    Sektör bazlı istatistikleri döndürür

    Returns:
        dict: Her sektördeki hisse sayısı
    """
    stats = {}
    for symbol, sector in STOCK_SECTORS.items():
        if sector not in stats:
            stats[sector] = 0
        stats[sector] += 1
    return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
