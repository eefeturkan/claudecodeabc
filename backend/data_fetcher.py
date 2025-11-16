"""
Yahoo Finance'ten hisse senedi verilerini çeken modül
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataFetcher:
    """Yahoo Finance veri çekme sınıfı"""

    def __init__(self):
        self.cache = {}

    def fetch_stock_data(self, symbols, period='1y', interval='1d'):
        """
        Hisse senedi verilerini Yahoo Finance'ten çeker

        Args:
            symbols (list): Yahoo Finance sembol listesi (örn: ['AKBNK.IS'])
            period (str): Veri periyodu ('1mo', '3mo', '6mo', '1y', '2y', '5y')
            interval (str): Veri aralığı ('1d', '1wk', '1mo')

        Returns:
            pd.DataFrame: Kapanış fiyatları dataframe'i
        """
        try:
            # Birden fazla sembol için veri çek
            data = yf.download(
                symbols,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True
            )

            # Eğer tek sembol varsa, sütun yapısını düzelt
            if len(symbols) == 1:
                df = pd.DataFrame()
                df[symbols[0]] = data['Close']
            else:
                df = data['Close']

            # Eksik verileri temizle
            df = df.dropna()

            return df

        except Exception as e:
            print(f"Veri çekme hatası: {e}")
            return pd.DataFrame()

    def calculate_returns(self, prices_df):
        """
        Günlük getirileri hesaplar

        Args:
            prices_df (pd.DataFrame): Fiyat verileri

        Returns:
            pd.DataFrame: Günlük getiri yüzdeleri
        """
        returns = prices_df.pct_change().dropna()
        return returns

    def calculate_log_returns(self, prices_df):
        """
        Logaritmik getirileri hesaplar

        Args:
            prices_df (pd.DataFrame): Fiyat verileri

        Returns:
            pd.DataFrame: Log getiriler
        """
        log_returns = np.log(prices_df / prices_df.shift(1)).dropna()
        return log_returns

    def get_covariance_matrix(self, returns_df):
        """
        Getiri kovaryans matrisini hesaplar

        Args:
            returns_df (pd.DataFrame): Getiri verileri

        Returns:
            pd.DataFrame: Kovaryans matrisi
        """
        return returns_df.cov()

    def get_correlation_matrix(self, returns_df):
        """
        Getiri korelasyon matrisini hesaplar

        Args:
            returns_df (pd.DataFrame): Getiri verileri

        Returns:
            pd.DataFrame: Korelasyon matrisi
        """
        return returns_df.corr()

    def get_mean_returns(self, returns_df, annualize=True):
        """
        Ortalama getirileri hesaplar

        Args:
            returns_df (pd.DataFrame): Getiri verileri
            annualize (bool): Yıllık getiriye dönüştür

        Returns:
            pd.Series: Ortalama getiriler
        """
        mean_returns = returns_df.mean()

        if annualize:
            mean_returns = mean_returns * 252  # 252 işlem günü

        return mean_returns

    def get_stock_info(self, symbol):
        """
        Hisse senedi hakkında detaylı bilgi

        Args:
            symbol (str): Yahoo Finance sembolü

        Returns:
            dict: Hisse bilgileri
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'marketCap': info.get('marketCap', 0),
                'currency': info.get('currency', 'TRY')
            }
        except Exception as e:
            print(f"Bilgi çekme hatası ({symbol}): {e}")
            return {'symbol': symbol, 'name': symbol}

    def validate_symbols(self, symbols):
        """
        Sembollerin geçerliliğini kontrol eder

        Args:
            symbols (list): Sembol listesi

        Returns:
            dict: {'valid': [], 'invalid': []}
        """
        valid = []
        invalid = []

        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                # Son 5 günlük veriyi test et
                hist = ticker.history(period='5d')

                if not hist.empty:
                    valid.append(symbol)
                else:
                    invalid.append(symbol)
            except:
                invalid.append(symbol)

        return {'valid': valid, 'invalid': invalid}
