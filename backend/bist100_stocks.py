"""
BIST100 Hisse Senetleri Listesi
Yahoo Finance için .IS uzantısı ile birlikte
"""

# BIST100'de işlem gören başlıca hisseler
BIST100_STOCKS = {
    'AKBNK': 'Akbank',
    'ALARK': 'Alarko Holding',
    'ARCLK': 'Arçelik',
    'ASELS': 'Aselsan',
    'BIMAS': 'BIM',
    'EKGYO': 'Emlak Konut GYO',
    'ENJSA': 'Enerjisa',
    'EREGL': 'Ereğli Demir Çelik',
    'FROTO': 'Ford Otosan',
    'GARAN': 'Garanti BBVA',
    'HEKTS': 'Hektaş',
    'ISCTR': 'İş Bankası (C)',
    'KCHOL': 'Koç Holding',
    'KOZAL': 'Koza Altın',
    'KOZAA': 'Koza Anadolu Metal',
    'KRDMD': 'Kardemir (D)',
    'PETKM': 'Petkim',
    'PGSUS': 'Pegasus',
    'SAHOL': 'Sabancı Holding',
    'SISE': 'Şişe Cam',
    'SODA': 'Soda Sanayi',
    'TAVHL': 'TAV Havalimanları',
    'TCELL': 'Turkcell',
    'THYAO': 'Türk Hava Yolları',
    'TKFEN': 'Tekfen Holding',
    'TOASO': 'Tofaş',
    'TTKOM': 'Türk Telekom',
    'TUPRS': 'Tüpraş',
    'VAKBN': 'Vakıfbank',
    'VESTL': 'Vestel',
    'YKBNK': 'Yapı Kredi',
}

def get_stock_list():
    """
    BIST100 hisse listesini döndürür

    Returns:
        dict: Sembol ve şirket ismi eşleşmeleri
    """
    return BIST100_STOCKS

def get_yahoo_symbols(symbols=None):
    """
    Yahoo Finance için .IS uzantılı sembol listesi döndürür

    Args:
        symbols (list): Belirli semboller (None ise tümü)

    Returns:
        list: Yahoo Finance formatında semboller
    """
    if symbols is None:
        symbols = list(BIST100_STOCKS.keys())

    return [f"{symbol}.IS" for symbol in symbols]

def get_stock_name(symbol):
    """
    Sembol için şirket ismini döndürür

    Args:
        symbol (str): Hisse sembolü

    Returns:
        str: Şirket ismi
    """
    return BIST100_STOCKS.get(symbol, symbol)
