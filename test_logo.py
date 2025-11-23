# -*- coding: utf-8 -*-
"""
LOGO ve diger hisselerin veri kontrolu
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from data_fetcher import DataFetcher
from bist100_stocks import get_yahoo_symbols
import warnings
warnings.filterwarnings('ignore')

def test_stocks(symbols, period='1y'):
    print("="*80)
    print(f"TEST: {symbols}")
    print(f"Periyot: {period}")
    print("="*80)

    fetcher = DataFetcher()
    yahoo_symbols = get_yahoo_symbols(symbols)

    print(f"\nYahoo sembolleri: {yahoo_symbols}")
    print("\nVeri cekiliyor...")

    # Fiyat verilerini cek
    prices_df = fetcher.fetch_stock_data(yahoo_symbols, period=period, interval='1d')

    if prices_df.empty:
        print("HATA: Veri cekilemedi!")
        return

    print(f"Veri cekildi: {len(prices_df)} gun")
    print(f"Tarih: {prices_df.index[0]} - {prices_df.index[-1]}")

    # Her hisse icin analiz
    print("\n" + "="*80)
    print("FIYAT ANALIZI")
    print("="*80)

    for yahoo_symbol in yahoo_symbols:
        symbol = yahoo_symbol.replace('.IS', '')

        if yahoo_symbol not in prices_df.columns:
            print(f"\n{symbol}: VERI YOK")
            continue

        prices = prices_df[yahoo_symbol].dropna()

        if len(prices) == 0:
            print(f"\n{symbol}: TUM VERILER NaN")
            continue

        first_price = prices.iloc[0]
        last_price = prices.iloc[-1]
        min_price = prices.min()
        max_price = prices.max()

        total_return_pct = ((last_price - first_price) / first_price) * 100

        print(f"\n{symbol}:")
        print(f"  Veri sayisi: {len(prices)} gun")
        print(f"  Ilk fiyat ({prices.index[0].date()}): {first_price:.2f} TL")
        print(f"  Son fiyat ({prices.index[-1].date()}): {last_price:.2f} TL")
        print(f"  Min fiyat: {min_price:.2f} TL")
        print(f"  Max fiyat: {max_price:.2f} TL")
        print(f"  TOPLAM GETIRI: {total_return_pct:+.2f}%")

        # Son 5 gun
        print(f"  Son 5 gun:")
        for date, price in prices.tail(5).items():
            print(f"    {date.date()}: {price:.2f} TL")

    # Getiri analizi
    print("\n" + "="*80)
    print("GETIRI ANALIZI")
    print("="*80)

    returns_df = fetcher.calculate_returns(prices_df)
    returns_df.columns = [col.replace('.IS', '') for col in returns_df.columns]

    for symbol in returns_df.columns:
        returns = returns_df[symbol].dropna()

        if len(returns) == 0:
            continue

        # Yillik metrikler (252 islem gunu)
        annual_return = returns.mean() * 252 * 100
        annual_volatility = returns.std() * (252 ** 0.5) * 100

        print(f"\n{symbol}:")
        print(f"  Yillik getiri: {annual_return:+.2f}%")
        print(f"  Yillik volatilite: {annual_volatility:.2f}%")

        # Farkli risk-free rate'lerle Sharpe
        for rf_pct in [10, 20, 45]:
            rf = rf_pct / 100.0
            sharpe = ((annual_return/100) - rf) / (annual_volatility/100) if annual_volatility > 0 else 0
            print(f"  Sharpe (RF={rf_pct}%): {sharpe:.3f}")

if __name__ == '__main__':
    # Test 1: Teknoloji hisseleri
    print("\n\nTEKNOLOJI HISSELERI")
    tech_stocks = ['LOGO', 'ASELS', 'LINK', 'NETAS', 'THYAO']
    test_stocks(tech_stocks, period='1y')

    print("\n\n")

    # Test 2: Bankalar
    print("BANKALAR")
    banks = ['AKBNK', 'GARAN', 'YKBNK', 'ISCTR', 'HALKB']
    test_stocks(banks, period='1y')

    print("\n\nTEST TAMAMLANDI")
    print("="*80)
