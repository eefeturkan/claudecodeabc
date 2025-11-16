"""
Portföy metriklerini hesaplayan modül
Risk, getiri, Sharpe ratio vb.
"""

import numpy as np
import pandas as pd


class PortfolioMetrics:
    """Portföy performans metrikleri hesaplama sınıfı"""

    def __init__(self, returns_df, risk_free_rate=0.10):
        """
        Args:
            returns_df (pd.DataFrame): Günlük getiri verileri
            risk_free_rate (float): Risksiz faiz oranı (yıllık, varsayılan %10)
        """
        self.returns_df = returns_df
        self.risk_free_rate = risk_free_rate
        self.mean_returns = returns_df.mean() * 252  # Yıllık
        self.cov_matrix = returns_df.cov() * 252  # Yıllık

    def portfolio_return(self, weights):
        """
        Portföy getirisini hesaplar

        Args:
            weights (np.array): Portföy ağırlıkları

        Returns:
            float: Yıllık portföy getirisi
        """
        return np.sum(self.mean_returns * weights)

    def portfolio_volatility(self, weights):
        """
        Portföy volatilitesini (risk) hesaplar

        Args:
            weights (np.array): Portföy ağırlıkları

        Returns:
            float: Yıllık portföy volatilitesi (standart sapma)
        """
        variance = np.dot(weights.T, np.dot(self.cov_matrix, weights))
        return np.sqrt(variance)

    def sharpe_ratio(self, weights):
        """
        Sharpe oranını hesaplar (risk-ayarlı getiri)

        Args:
            weights (np.array): Portföy ağırlıkları

        Returns:
            float: Sharpe oranı
        """
        portfolio_ret = self.portfolio_return(weights)
        portfolio_vol = self.portfolio_volatility(weights)

        if portfolio_vol == 0:
            return 0

        sharpe = (portfolio_ret - self.risk_free_rate) / portfolio_vol
        return sharpe

    def sortino_ratio(self, weights):
        """
        Sortino oranını hesaplar (sadece aşağı yönlü risk)

        Args:
            weights (np.array): Portföy ağırlıkları

        Returns:
            float: Sortino oranı
        """
        portfolio_ret = self.portfolio_return(weights)

        # Portföy günlük getirileri
        portfolio_returns = (self.returns_df * weights).sum(axis=1)

        # Sadece negatif getirilerin standart sapması
        downside_returns = portfolio_returns[portfolio_returns < 0]

        if len(downside_returns) == 0:
            return float('inf')

        downside_std = downside_returns.std() * np.sqrt(252)

        if downside_std == 0:
            return 0

        sortino = (portfolio_ret - self.risk_free_rate) / downside_std
        return sortino

    def max_drawdown(self, weights):
        """
        Maksimum düşüşü hesaplar

        Args:
            weights (np.array): Portföy ağırlıkları

        Returns:
            float: Maksimum düşüş yüzdesi
        """
        # Portföy günlük getirileri
        portfolio_returns = (self.returns_df * weights).sum(axis=1)

        # Kümülatif getiri
        cumulative = (1 + portfolio_returns).cumprod()

        # Running maximum
        running_max = cumulative.expanding().max()

        # Drawdown
        drawdown = (cumulative - running_max) / running_max

        return drawdown.min()

    def value_at_risk(self, weights, confidence=0.95):
        """
        Value at Risk (VaR) hesaplar

        Args:
            weights (np.array): Portföy ağırlıkları
            confidence (float): Güven seviyesi

        Returns:
            float: VaR değeri
        """
        portfolio_returns = (self.returns_df * weights).sum(axis=1)
        var = np.percentile(portfolio_returns, (1 - confidence) * 100)
        return var

    def conditional_var(self, weights, confidence=0.95):
        """
        Conditional VaR (CVaR/Expected Shortfall) hesaplar

        Args:
            weights (np.array): Portföy ağırlıkları
            confidence (float): Güven seviyesi

        Returns:
            float: CVaR değeri
        """
        portfolio_returns = (self.returns_df * weights).sum(axis=1)
        var = self.value_at_risk(weights, confidence)
        cvar = portfolio_returns[portfolio_returns <= var].mean()
        return cvar

    def portfolio_beta(self, weights, market_returns):
        """
        Portföy betasını hesaplar

        Args:
            weights (np.array): Portföy ağırlıkları
            market_returns (pd.Series): Piyasa getirileri

        Returns:
            float: Beta değeri
        """
        portfolio_returns = (self.returns_df * weights).sum(axis=1)

        # Kovaryans ve varyans
        covariance = np.cov(portfolio_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)

        if market_variance == 0:
            return 0

        beta = covariance / market_variance
        return beta

    def diversification_ratio(self, weights):
        """
        Çeşitlendirme oranını hesaplar

        Args:
            weights (np.array): Portföy ağırlıkları

        Returns:
            float: Çeşitlendirme oranı
        """
        # Ağırlıklı bireysel volatiliteler
        individual_vols = np.sqrt(np.diag(self.cov_matrix))
        weighted_vol_sum = np.sum(weights * individual_vols)

        # Portföy volatilitesi
        portfolio_vol = self.portfolio_volatility(weights)

        if portfolio_vol == 0:
            return 0

        div_ratio = weighted_vol_sum / portfolio_vol
        return div_ratio

    def get_all_metrics(self, weights):
        """
        Tüm portföy metriklerini hesaplar

        Args:
            weights (np.array): Portföy ağırlıkları

        Returns:
            dict: Tüm metrikler
        """
        return {
            'expected_return': self.portfolio_return(weights),
            'volatility': self.portfolio_volatility(weights),
            'sharpe_ratio': self.sharpe_ratio(weights),
            'sortino_ratio': self.sortino_ratio(weights),
            'max_drawdown': self.max_drawdown(weights),
            'var_95': self.value_at_risk(weights, 0.95),
            'cvar_95': self.conditional_var(weights, 0.95),
            'diversification_ratio': self.diversification_ratio(weights)
        }
