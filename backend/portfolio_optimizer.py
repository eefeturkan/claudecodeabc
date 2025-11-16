"""
ABC Algoritması ile Portföy Optimizasyonu
"""

import numpy as np
import pandas as pd
from abc_algorithm import ArtificialBeeColony
from metrics import PortfolioMetrics


class PortfolioOptimizer:
    """ABC algoritması kullanarak portföy optimizasyonu"""

    def __init__(
        self,
        returns_df: pd.DataFrame,
        risk_free_rate: float = 0.10,
        min_weight: float = 0.0,
        max_weight: float = 0.5
    ):
        """
        Args:
            returns_df: Hisse getiri verileri (DataFrame)
            risk_free_rate: Risksiz faiz oranı
            min_weight: Minimum hisse ağırlığı
            max_weight: Maksimum hisse ağırlığı
        """
        self.returns_df = returns_df
        self.risk_free_rate = risk_free_rate
        self.min_weight = min_weight
        self.max_weight = max_weight

        self.n_assets = len(returns_df.columns)
        self.asset_names = list(returns_df.columns)

        # Metrik hesaplayıcı
        self.metrics = PortfolioMetrics(returns_df, risk_free_rate)

        # Optimizasyon sonuçları
        self.optimal_weights = None
        self.optimal_metrics = None
        self.optimization_history = None

    def _normalize_weights(self, weights: np.ndarray) -> np.ndarray:
        """
        Ağırlıkları normalize eder (toplam = 1)

        Args:
            weights: Ham ağırlıklar

        Returns:
            np.ndarray: Normalize edilmiş ağırlıklar
        """
        # Negatif değerleri 0 yap
        weights = np.maximum(weights, 0)

        # Toplam
        total = np.sum(weights)

        if total == 0:
            # Eşit ağırlık
            return np.ones(self.n_assets) / self.n_assets

        # Normalize et
        normalized = weights / total

        return normalized

    def _sharpe_objective(self, weights: np.ndarray) -> float:
        """
        Sharpe ratio için objektif fonksiyon (maksimize)

        Args:
            weights: Portföy ağırlıkları

        Returns:
            float: Sharpe ratio
        """
        # Ağırlıkları normalize et
        weights = self._normalize_weights(weights)

        # Sharpe ratio hesapla
        sharpe = self.metrics.sharpe_ratio(weights)

        return sharpe

    def _min_variance_objective(self, weights: np.ndarray) -> float:
        """
        Minimum varyans için objektif fonksiyon

        Args:
            weights: Portföy ağırlıkları

        Returns:
            float: Negatif volatilite (maksimize edilecek)
        """
        # Ağırlıkları normalize et
        weights = self._normalize_weights(weights)

        # Volatiliteyi hesapla ve negatifini döndür
        volatility = self.metrics.portfolio_volatility(weights)

        return -volatility

    def _max_return_objective(self, weights: np.ndarray) -> float:
        """
        Maksimum getiri için objektif fonksiyon

        Args:
            weights: Portföy ağırlıkları

        Returns:
            float: Portföy getirisi
        """
        # Ağırlıkları normalize et
        weights = self._normalize_weights(weights)

        # Getiriyi hesapla
        portfolio_return = self.metrics.portfolio_return(weights)

        return portfolio_return

    def optimize(
        self,
        objective: str = 'sharpe',
        colony_size: int = 50,
        max_iterations: int = 100,
        limit: int = 100,
        verbose: bool = False
    ) -> dict:
        """
        Portföy optimizasyonunu çalıştırır

        Args:
            objective: Objektif fonksiyon ('sharpe', 'min_variance', 'max_return')
            colony_size: ABC koloni büyüklüğü
            max_iterations: Maksimum iterasyon sayısı
            limit: Çözüm terk etme limiti
            verbose: Detaylı çıktı

        Returns:
            dict: Optimizasyon sonuçları
        """
        # Objektif fonksiyonu seç
        if objective == 'sharpe':
            obj_func = self._sharpe_objective
        elif objective == 'min_variance':
            obj_func = self._min_variance_objective
        elif objective == 'max_return':
            obj_func = self._max_return_objective
        else:
            raise ValueError(f"Geçersiz objektif: {objective}")

        # Alt ve üst sınırlar
        lower_bounds = np.full(self.n_assets, self.min_weight)
        upper_bounds = np.full(self.n_assets, self.max_weight)

        # ABC algoritması
        abc = ArtificialBeeColony(
            objective_function=obj_func,
            dimensions=self.n_assets,
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds,
            colony_size=colony_size,
            max_iterations=max_iterations,
            limit=limit,
            minimize=False  # Her zaman maksimize
        )

        # Optimizasyon
        if verbose:
            print(f"\n{objective.upper()} optimizasyonu başlatılıyor...")
            print(f"Varlık sayısı: {self.n_assets}")
            print(f"Koloni büyüklüğü: {colony_size}")
            print(f"Maksimum iterasyon: {max_iterations}\n")

        best_solution, best_objective = abc.optimize(verbose=verbose)

        # Ağırlıkları normalize et
        self.optimal_weights = self._normalize_weights(best_solution)

        # Tüm metrikleri hesapla
        self.optimal_metrics = self.metrics.get_all_metrics(self.optimal_weights)

        # Optimizasyon geçmişi
        self.optimization_history = abc.get_history()

        # Sonuçları hazırla
        results = {
            'objective': objective,
            'weights': {
                self.asset_names[i]: float(self.optimal_weights[i])
                for i in range(self.n_assets)
            },
            'metrics': {
                key: float(value) for key, value in self.optimal_metrics.items()
            },
            'history': self.optimization_history
        }

        if verbose:
            print(f"\n{'='*60}")
            print("Optimizasyon Tamamlandı!")
            print(f"{'='*60}")
            print(f"\nPortföy Ağırlıkları:")
            for asset, weight in results['weights'].items():
                if weight > 0.001:  # %0.1'den büyük ağırlıkları göster
                    print(f"  {asset}: {weight*100:.2f}%")
            print(f"\nPerformans Metrikleri:")
            print(f"  Beklenen Getiri: {results['metrics']['expected_return']*100:.2f}%")
            print(f"  Volatilite (Risk): {results['metrics']['volatility']*100:.2f}%")
            print(f"  Sharpe Ratio: {results['metrics']['sharpe_ratio']:.4f}")
            print(f"  Sortino Ratio: {results['metrics']['sortino_ratio']:.4f}")
            print(f"  Max Drawdown: {results['metrics']['max_drawdown']*100:.2f}%")
            print(f"  Çeşitlendirme Oranı: {results['metrics']['diversification_ratio']:.4f}")
            print(f"{'='*60}\n")

        return results

    def efficient_frontier(
        self,
        n_portfolios: int = 50,
        colony_size: int = 30,
        max_iterations: int = 50
    ) -> pd.DataFrame:
        """
        Etkin sınırı hesaplar (farklı risk-getiri kombinasyonları)

        Args:
            n_portfolios: Oluşturulacak portföy sayısı
            colony_size: ABC koloni büyüklüğü
            max_iterations: Maksimum iterasyon

        Returns:
            pd.DataFrame: Risk-getiri-sharpe dataframe
        """
        results = []

        # Farklı hedef getiriler için optimize et
        target_returns = np.linspace(
            self.metrics.mean_returns.min(),
            self.metrics.mean_returns.max(),
            n_portfolios
        )

        for target_return in target_returns:
            # Hedef getiri kısıtı ile minimum varyans
            def constrained_objective(weights):
                weights = self._normalize_weights(weights)
                portfolio_ret = self.metrics.portfolio_return(weights)

                # Getiri kısıtını ceza fonksiyonu ile ekle
                penalty = abs(portfolio_ret - target_return) * 10

                # Minimize volatility
                volatility = self.metrics.portfolio_volatility(weights)

                return -(volatility + penalty)

            lower_bounds = np.full(self.n_assets, self.min_weight)
            upper_bounds = np.full(self.n_assets, self.max_weight)

            abc = ArtificialBeeColony(
                objective_function=constrained_objective,
                dimensions=self.n_assets,
                lower_bounds=lower_bounds,
                upper_bounds=upper_bounds,
                colony_size=colony_size,
                max_iterations=max_iterations,
                limit=50,
                minimize=False
            )

            best_solution, _ = abc.optimize(verbose=False)
            weights = self._normalize_weights(best_solution)

            # Metrikleri hesapla
            ret = self.metrics.portfolio_return(weights)
            vol = self.metrics.portfolio_volatility(weights)
            sharpe = self.metrics.sharpe_ratio(weights)

            results.append({
                'return': ret,
                'volatility': vol,
                'sharpe_ratio': sharpe
            })

        return pd.DataFrame(results)
