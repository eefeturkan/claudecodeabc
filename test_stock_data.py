"""
Hisse Veri Çekme Test Scripti

Yahoo Finance'ten çekilen verileri kontrol eder ve görselleştirir.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from data_fetcher import DataFetcher
from bist100_stocks import get_yahoo_symbols
import pandas as pd
from datetime import datetime

def test_stock_data(symbols, period='1y'):
    """
    Hisse verilerini çeker ve analiz eder

    Args:
        symbols: BIST sembolleri listesi (örn: ['LOGO', 'ASELS', 'THYAO'])
        period: Veri periyodu (örn: '1y', '6mo', '5y')
    """
    print("="*80)
    print("HİSSE VERİ ÇEKME TEST SCRİPTİ")
    print("="*80)
    print(f"\nTest Edilecek Hisseler: {symbols}")
    print(f"Periyot: {period}")
    print(f"Bugünün Tarihi: {datetime.now().strftime('%Y-%m-%d')}")
    print("\n" + "="*80)

    # Data fetcher oluştur
    fetcher = DataFetcher()

    # Yahoo Finance sembolleri
    yahoo_symbols = get_yahoo_symbols(symbols)
    print(f"\nYahoo Finance Sembolleri: {yahoo_symbols}")

    # Veri çek
    print(f"\n{'Veri Çekiliyor...':-^80}")
    prices_df = fetcher.fetch_stock_data(yahoo_symbols, period=period, interval='1d')

    if prices_df.empty:
        print("[HATA] VERI CEKILEMEDI!")
        return

    print(f"[OK] Veri basariyla cekildi")
    print(f"Toplam Gün Sayısı: {len(prices_df)}")
    print(f"Tarih Aralığı: {prices_df.index[0].strftime('%Y-%m-%d')} → {prices_df.index[-1].strftime('%Y-%m-%d')}")

    # Her hisse için detaylı analiz
    print(f"\n{'FİYAT ANALİZİ':-^80}")

    for yahoo_symbol in yahoo_symbols:
        symbol = yahoo_symbol.replace('.IS', '')

        if yahoo_symbol not in prices_df.columns:
            print(f"\n[HATA] {symbol}: Veri bulunamadi")
            continue

        prices = prices_df[yahoo_symbol].dropna()

        if len(prices) == 0:
            print(f"\n[HATA] {symbol}: Tum veriler NaN")
            continue

        # İstatistikler
        first_price = prices.iloc[0]
        last_price = prices.iloc[-1]
        min_price = prices.min()
        max_price = prices.max()
        avg_price = prices.mean()

        total_return = ((last_price - first_price) / first_price) * 100
        volatility = prices.pct_change().std() * (252 ** 0.5) * 100  # Yıllık volatilite

        print(f"\n[ANALIZ] {symbol} ({yahoo_symbol})")
        print(f"   Veri Sayısı: {len(prices)} gün")
        print(f"   İlk Tarih: {prices.index[0].strftime('%Y-%m-%d')}")
        print(f"   Son Tarih: {prices.index[-1].strftime('%Y-%m-%d')}")
        print(f"   İlk Fiyat: {first_price:.2f} TL")
        print(f"   Son Fiyat: {last_price:.2f} TL")
        print(f"   Min Fiyat: {min_price:.2f} TL")
        print(f"   Max Fiyat: {max_price:.2f} TL")
        print(f"   Ortalama: {avg_price:.2f} TL")
        print(f"   Toplam Getiri: {total_return:+.2f}%")
        print(f"   Yıllık Volatilite: {volatility:.2f}%")

        # Son 10 günün fiyatları
        print(f"\n   Son 10 Gün:")
        last_10 = prices.tail(10)
        for date, price in last_10.items():
            print(f"   {date.strftime('%Y-%m-%d')}: {price:.2f} TL")

    # Getiri hesaplama
    print(f"\n{'GETİRİ ANALİZİ':-^80}")
    returns_df = fetcher.calculate_returns(prices_df)
    returns_df.columns = [col.replace('.IS', '') for col in returns_df.columns]

    print(f"\nGünlük Getiri İstatistikleri:")
    print(returns_df.describe())

    # Korelasyon matrisi
    print(f"\n{'KORELASYON MATRİSİ':-^80}")
    correlation = returns_df.corr()
    print(correlation)

    # En yüksek ve en düşük getiri günleri
    print(f"\n{'AŞIRI GETİRİ GÜNLERİ':-^80}")
    for col in returns_df.columns:
        returns = returns_df[col].dropna()
        if len(returns) == 0:
            continue

        max_return_date = returns.idxmax()
        max_return = returns.max() * 100
        min_return_date = returns.idxmin()
        min_return = returns.min() * 100

        print(f"\n{col}:")
        print(f"   En Yüksek Getiri: {max_return:+.2f}% ({max_return_date.strftime('%Y-%m-%d')})")
        print(f"   En Düşük Getiri: {min_return:+.2f}% ({min_return_date.strftime('%Y-%m-%d')})")

    # Sharpe Ratio karşılaştırması
    print(f"\n{'SHARPE RATIO KARŞILAŞTIRMASI':-^80}")
    risk_free_rates = [0.10, 0.20, 0.45]  # %10, %20, %45

    for symbol in returns_df.columns:
        returns = returns_df[symbol].dropna()
        if len(returns) == 0:
            continue

        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * (252 ** 0.5)

        print(f"\n{symbol}:")
        print(f"   Yıllık Getiri: {annual_return * 100:.2f}%")
        print(f"   Yıllık Volatilite: {annual_volatility * 100:.2f}%")

        for rf in risk_free_rates:
            sharpe = (annual_return - rf) / annual_volatility if annual_volatility > 0 else 0
            print(f"   Sharpe (RF={rf*100:.0f}%): {sharpe:.3f}")

    print("\n" + "="*80)
    print("TEST TAMAMLANDI")
    print("="*80)


if __name__ == '__main__':
    print("\n" + "="*80)
    print("LOGO VE DİĞER TEKNOLOJİ HİSSELERİ KARŞILAŞTIRMASI")
    print("="*80)

    # LOGO ve diğer teknoloji hisselerini test et
    tech_stocks = ['LOGO', 'ASELS', 'LINK', 'NETAS', 'THYAO']
    test_stock_data(tech_stocks, period='1y')

    print("\n\n" + "="*80)
    print("BANKALAR KARŞILAŞTIRMASI")
    print("="*80)

    # Karşılaştırma için bankalar
    banks = ['AKBNK', 'GARAN', 'YKBNK', 'ISCTR', 'HALKB']
    test_stock_data(banks, period='1y')
