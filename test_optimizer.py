"""
Test script for ABC Portfolio Optimizer
"""

import sys
sys.path.insert(0, 'backend')

from backend.data_fetcher import DataFetcher
from backend.portfolio_optimizer import PortfolioOptimizer
from backend.bist100_stocks import get_yahoo_symbols

def main():
    print("="*60)
    print("BIST100 ABC Portfolio Optimizer - Test Script")
    print("="*60)

    # Test stocks
    test_symbols = ['AKBNK', 'GARAN', 'THYAO', 'TUPRS', 'EREGL']
    print(f"\nTest Hisseleri: {test_symbols}")

    # Initialize data fetcher
    print("\n1. Veri çekme başlatılıyor...")
    fetcher = DataFetcher()

    # Get Yahoo symbols
    yahoo_symbols = get_yahoo_symbols(test_symbols)
    print(f"   Yahoo Sembolleri: {yahoo_symbols}")

    # Fetch data
    print("\n2. Fiyat verileri çekiliyor (1 yıl)...")
    prices_df = fetcher.fetch_stock_data(yahoo_symbols, period='1y')

    if prices_df.empty:
        print("   HATA: Veri çekilemedi!")
        return

    print(f"   Başarılı! {len(prices_df)} günlük veri çekildi")
    print(f"   Tarih aralığı: {prices_df.index[0]} - {prices_df.index[-1]}")

    # Calculate returns
    print("\n3. Getiriler hesaplanıyor...")
    returns_df = fetcher.calculate_returns(prices_df)
    returns_df.columns = [col.replace('.IS', '') for col in returns_df.columns]

    print(f"   Ortalama günlük getiriler:")
    for col in returns_df.columns:
        mean_ret = returns_df[col].mean() * 252 * 100
        print(f"      {col}: {mean_ret:.2f}% (yıllık)")

    # Optimize portfolio
    print("\n4. ABC optimizasyonu başlatılıyor...")
    print("   Koloni büyüklüğü: 30")
    print("   Maksimum iterasyon: 50")
    print("   Objektif: Sharpe Ratio Maksimizasyonu")
    print()

    optimizer = PortfolioOptimizer(
        returns_df=returns_df,
        risk_free_rate=0.10,
        min_weight=0.0,
        max_weight=0.5
    )

    results = optimizer.optimize(
        objective='sharpe',
        colony_size=30,
        max_iterations=50,
        verbose=True
    )

    print("\n5. Test tamamlandı!")
    print("="*60)

if __name__ == '__main__':
    main()
