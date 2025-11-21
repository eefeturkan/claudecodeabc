"""
BIST100 Hisse Senetleri Sektör Sınıflandırması ve Filtreleme
"""

# Sektörel sınıflandırma
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

    # Teknoloji ve Yazılım
    'LOGO': 'Teknoloji',
    'LINK': 'Teknoloji',
    'NETAS': 'Teknoloji',
    'TTKOM': 'Teknoloji',
    'TCELL': 'Teknoloji',
    'KRONT': 'Teknoloji',
    'VBTYZ': 'Teknoloji',
    'TKNSA': 'Teknoloji',

    # Savunma ve Havacılık
    'ASELS': 'Savunma',
    'THYAO': 'Havacılık',
    'PGSUS': 'Havacılık',
    'TAVHL': 'Havacılık',

    # Enerji
    'AKSEN': 'Enerji',
    'AYEN': 'Enerji',
    'AYDEM': 'Enerji',
    'ZOREN': 'Enerji',
    'AKENR': 'Enerji',
    'AKFYE': 'Enerji',
    'ENJSA': 'Enerji',
    'TUPRS': 'Enerji',
    'TGSAS': 'Enerji',  # TGSAN -> TGSAS (Tüpraş)
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

    # Perakende ve Gıda
    'BIMAS': 'Perakende',
    'SOKM': 'Perakende',
    'MGROS': 'Perakende',
    'BIZIM': 'Perakende',
    'MAVI': 'Perakende',
    'ULKER': 'Gıda',
    'CCOLA': 'Gıda',
    'AEFES': 'Gıda',
    'PNSUT': 'Gıda',
    'TATEN': 'Gıda',  # TATGD -> TATEN (Tat Gıda)
    'PENGD': 'Gıda',
    'TUKAS': 'Gıda',
    'SELGD': 'Gıda',
    'KERVT': 'Gıda',
    'BANVT': 'Gıda',
    'KENT': 'Perakende',
    'CRFSA': 'Perakende',

    # Otomotiv
    'FROTO': 'Otomotiv',
    'TOASO': 'Otomotiv',
    'DOAS': 'Otomotiv',
    'OTKAR': 'Otomotiv',
    'TTRAK': 'Otomotiv',
    'ASUZU': 'Otomotiv',
    'KARSN': 'Otomotiv',

    # İnşaat ve Gayrimenkul
    'ENKAI': 'İnşaat',
    'TKFEN': 'İnşaat',
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

    # Çimento ve Yapı Malzemeleri
    'AFYON': 'Çimento',
    'AKCNS': 'Çimento',
    'BTCIM': 'Çimento',
    'BUCIM': 'Çimento',
    'CIMSA': 'Çimento',
    'KONYA': 'Çimento',
    'OYAKC': 'Çimento',
    'BSOKE': 'Çimento',
    'CMENT': 'Çimento',
    'IZOCM': 'İnşaat',
    'BRSAN': 'Metal',
    'BOBET': 'Metal',

    # Demir-Çelik ve Metal
    'EREGL': 'Demir-Çelik',
    'KRDMA': 'Demir-Çelik',
    'KRDMB': 'Demir-Çelik',
    'ISDMR': 'Demir-Çelik',
    'SARKY': 'Metal',

    # Tekstil ve Deri
    'KORDS': 'Tekstil',
    'YUNSA': 'Tekstil',
    'YATAS': 'Tekstil',
    'BLCYT': 'Tekstil',
    'SNPAM': 'Tekstil',
    'DESA': 'Tekstil',
    'KRTEK': 'Tekstil',

    # Cam ve Seramik
    'SISE': 'Cam',
    'TRILC': 'Cam',  # TRKCM -> TRILC (Trakya Cam)
    'KUTPO': 'Seramik',

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

    # Elektrik-Elektronik
    'ARCLK': 'Elektrik-Elektronik',
    'VESTL': 'Elektrik-Elektronik',
    'VESBE': 'Elektrik-Elektronik',

    # Hizmetler ve Sağlık
    'CLEBI': 'Hizmetler',
    'LKMNH': 'Sağlık',
    'MLP': 'Sağlık',

    # Sigorta
    'ANSGR': 'Sigorta',
    'ANHYT': 'Sigorta',
    'RAYSG': 'Sigorta',
    'TURSG': 'Sigorta',

    # Spor
    'GSRAY': 'Spor',  # GSRAY -> GSDHO (Galatasaray)
    'FENER': 'Spor',
    'BJKAS': 'Spor',
    'TSPOR': 'Spor',
}

# Risk Profilleri (volatilite bazlı)
RISK_PROFILES = {
    'düşük': {
        'sectors': ['Bankacılık', 'Gıda', 'Perakende', 'Holding'],
        'volatility_threshold': 0.30,  # Düşük volatilite
        'description': 'Kararlı gelir, düşük risk'
    },
    'orta': {
        'sectors': ['Bankacılık', 'Enerji', 'İnşaat', 'Otomotiv', 'Teknoloji', 'Gıda', 'Perakende'],
        'volatility_threshold': 0.50,
        'description': 'Dengeli risk-getiri'
    },
    'yüksek': {
        'sectors': ['Teknoloji', 'Savunma', 'Enerji', 'Havacılık', 'Demir-Çelik'],
        'volatility_threshold': 1.0,  # Yüksek volatilite kabul edilir
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


def filter_stocks_by_preferences(risk_profile='orta', sectors=None, max_stocks=10):
    """
    Kullanıcı tercihlerine göre hisse filtreler

    Args:
        risk_profile (str): 'düşük', 'orta', 'yüksek'
        sectors (list): İstenen sektörler (None ise tüm sektörler)
        max_stocks (int): Maksimum hisse sayısı

    Returns:
        list: Filtrelenmiş hisse sembolleri
    """
    # Sektör seçimi: Kullanıcı seçimi varsa öncelik ona, yoksa risk profiline göre
    if sectors:
        # Kullanıcı sektör belirtmişse, sadece onları kullan
        allowed_sectors = sectors
    else:
        # Kullanıcı sektör belirtmemişse, risk profiline göre uygun sektörleri al
        profile = RISK_PROFILES.get(risk_profile, RISK_PROFILES['orta'])
        allowed_sectors = profile['sectors']

    # Sektörlere göre hisseleri filtrele
    filtered_stocks = []
    for symbol, sector in STOCK_SECTORS.items():
        if sector in allowed_sectors:
            filtered_stocks.append(symbol)

    # Çeşitlilik için sektörlerden dengeli dağılım
    stocks_by_sector = {}
    for symbol in filtered_stocks:
        sector = STOCK_SECTORS[symbol]
        if sector not in stocks_by_sector:
            stocks_by_sector[sector] = []
        stocks_by_sector[sector].append(symbol)

    # Her sektörden eşit sayıda hisse al
    balanced_stocks = []

    # Eğer hiç hisse bulunamadıysa boş liste döndür
    if len(stocks_by_sector) == 0:
        return []

    stocks_per_sector = max(1, max_stocks // len(stocks_by_sector))

    for sector, symbols in stocks_by_sector.items():
        balanced_stocks.extend(symbols[:stocks_per_sector])

    # Max hisse sayısını aşmıyorsa geri kalanı ekle
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

    recommended_stocks = filter_stocks_by_preferences(risk_profile, sectors, max_stocks)

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
