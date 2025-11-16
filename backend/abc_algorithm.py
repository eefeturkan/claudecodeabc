"""
Yapay Arı Kolonisi (Artificial Bee Colony - ABC) Algoritması
Karaboga, D. (2005) tarafından geliştirilen sürü zekası optimizasyon algoritması
"""

import numpy as np
from typing import Callable, Tuple, List


class ArtificialBeeColony:
    """
    Yapay Arı Kolonisi Optimizasyon Algoritması

    Üç tip arı grubu:
    1. Employee Bees (İşçi Arılar): Mevcut çözümleri araştırır
    2. Onlooker Bees (Gözlemci Arılar): İyi çözümleri seçer ve geliştirir
    3. Scout Bees (Keşif Arıları): Yeni rastgele çözümler üretir
    """

    def __init__(
        self,
        objective_function: Callable,
        dimensions: int,
        lower_bounds: np.ndarray,
        upper_bounds: np.ndarray,
        colony_size: int = 50,
        max_iterations: int = 100,
        limit: int = 100,
        minimize: bool = False
    ):
        """
        Args:
            objective_function: Optimize edilecek fonksiyon
            dimensions: Çözüm boyutu (kaç değişken var)
            lower_bounds: Alt sınırlar (np.array)
            upper_bounds: Üst sınırlar (np.array)
            colony_size: Koloni büyüklüğü (çift sayı olmalı)
            max_iterations: Maksimum iterasyon sayısı
            limit: Bir çözümün terk edilme limiti
            minimize: True ise minimize, False ise maximize
        """
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.lower_bounds = np.array(lower_bounds)
        self.upper_bounds = np.array(upper_bounds)
        self.colony_size = colony_size
        self.food_number = colony_size // 2  # Yiyecek kaynağı sayısı
        self.max_iterations = max_iterations
        self.limit = limit
        self.minimize = minimize

        # Çözümler ve fitness değerleri
        self.solutions = None
        self.fitness = None
        self.trials = None  # Her çözümün kaç kez iyileştirilemediği

        # En iyi çözüm
        self.best_solution = None
        self.best_fitness = None

        # İterasyon geçmişi
        self.history = {
            'best_fitness': [],
            'mean_fitness': []
        }

    def initialize_population(self):
        """Başlangıç popülasyonunu rastgele oluşturur"""
        self.solutions = np.random.uniform(
            self.lower_bounds,
            self.upper_bounds,
            size=(self.food_number, self.dimensions)
        )

        self.fitness = np.zeros(self.food_number)
        self.trials = np.zeros(self.food_number)

        # Başlangıç fitness değerlerini hesapla
        for i in range(self.food_number):
            self.fitness[i] = self._calculate_fitness(self.solutions[i])

        # En iyi çözümü bul
        self._update_best_solution()

    def _calculate_fitness(self, solution: np.ndarray) -> float:
        """
        Fitness değerini hesaplar

        Args:
            solution: Çözüm vektörü

        Returns:
            float: Fitness değeri (her zaman maksimize edilir)
        """
        objective_value = self.objective_function(solution)

        # Fitness değerini her zaman pozitif yap
        if self.minimize:
            # Minimize problemi için fitness
            if objective_value >= 0:
                fitness = 1.0 / (1.0 + objective_value)
            else:
                fitness = 1.0 + abs(objective_value)
        else:
            # Maximize problemi için fitness
            if objective_value >= 0:
                fitness = 1.0 + objective_value
            else:
                fitness = 1.0 / (1.0 + abs(objective_value))

        return fitness

    def _update_best_solution(self):
        """En iyi çözümü günceller"""
        best_idx = np.argmax(self.fitness)

        if self.best_fitness is None or self.fitness[best_idx] > self.best_fitness:
            self.best_fitness = self.fitness[best_idx]
            self.best_solution = self.solutions[best_idx].copy()

    def employee_bee_phase(self):
        """İşçi arı fazı: Mevcut çözümleri araştırır"""
        for i in range(self.food_number):
            # Rastgele bir parametre seç
            phi = np.random.uniform(-1, 1, self.dimensions)

            # Rastgele farklı bir çözüm seç
            k = np.random.choice([j for j in range(self.food_number) if j != i])

            # Yeni çözüm üret
            new_solution = self.solutions[i] + phi * (self.solutions[i] - self.solutions[k])

            # Sınırları kontrol et
            new_solution = np.clip(new_solution, self.lower_bounds, self.upper_bounds)

            # Fitness hesapla
            new_fitness = self._calculate_fitness(new_solution)

            # Eğer yeni çözüm daha iyiyse, güncelle
            if new_fitness > self.fitness[i]:
                self.solutions[i] = new_solution
                self.fitness[i] = new_fitness
                self.trials[i] = 0
            else:
                self.trials[i] += 1

    def calculate_probabilities(self) -> np.ndarray:
        """
        Gözlemci arılar için seçim olasılıklarını hesaplar

        Returns:
            np.ndarray: Seçim olasılıkları
        """
        # Fitness toplamı
        fitness_sum = np.sum(self.fitness)

        if fitness_sum == 0:
            return np.ones(self.food_number) / self.food_number

        # Olasılıklar (roulette wheel)
        probabilities = self.fitness / fitness_sum

        return probabilities

    def onlooker_bee_phase(self):
        """Gözlemci arı fazı: İyi çözümleri seçer ve geliştirir"""
        probabilities = self.calculate_probabilities()

        for _ in range(self.food_number):
            # Olasılıklara göre bir çözüm seç
            i = np.random.choice(self.food_number, p=probabilities)

            # Rastgele bir parametre seç
            phi = np.random.uniform(-1, 1, self.dimensions)

            # Rastgele farklı bir çözüm seç
            k = np.random.choice([j for j in range(self.food_number) if j != i])

            # Yeni çözüm üret
            new_solution = self.solutions[i] + phi * (self.solutions[i] - self.solutions[k])

            # Sınırları kontrol et
            new_solution = np.clip(new_solution, self.lower_bounds, self.upper_bounds)

            # Fitness hesapla
            new_fitness = self._calculate_fitness(new_solution)

            # Eğer yeni çözüm daha iyiyse, güncelle
            if new_fitness > self.fitness[i]:
                self.solutions[i] = new_solution
                self.fitness[i] = new_fitness
                self.trials[i] = 0
            else:
                self.trials[i] += 1

    def scout_bee_phase(self):
        """Keşif arısı fazı: Başarısız çözümleri yenileriyle değiştirir"""
        # Limit aşan çözümleri bul
        for i in range(self.food_number):
            if self.trials[i] >= self.limit:
                # Yeni rastgele çözüm üret
                self.solutions[i] = np.random.uniform(
                    self.lower_bounds,
                    self.upper_bounds,
                    size=self.dimensions
                )

                self.fitness[i] = self._calculate_fitness(self.solutions[i])
                self.trials[i] = 0

    def optimize(self, verbose: bool = False) -> Tuple[np.ndarray, float]:
        """
        Optimizasyonu çalıştırır

        Args:
            verbose: İterasyon bilgilerini yazdır

        Returns:
            Tuple[np.ndarray, float]: En iyi çözüm ve objektif değeri
        """
        # Popülasyonu başlat
        self.initialize_population()

        # Ana döngü
        for iteration in range(self.max_iterations):
            # İşçi arı fazı
            self.employee_bee_phase()

            # Gözlemci arı fazı
            self.onlooker_bee_phase()

            # Keşif arısı fazı
            self.scout_bee_phase()

            # En iyi çözümü güncelle
            self._update_best_solution()

            # Geçmişi kaydet
            self.history['best_fitness'].append(self.best_fitness)
            self.history['mean_fitness'].append(np.mean(self.fitness))

            if verbose and (iteration + 1) % 10 == 0:
                obj_value = self.objective_function(self.best_solution)
                print(f"İterasyon {iteration + 1}/{self.max_iterations} - "
                      f"En İyi Objektif: {obj_value:.6f}")

        # Son objektif değeri hesapla
        final_objective = self.objective_function(self.best_solution)

        return self.best_solution, final_objective

    def get_history(self) -> dict:
        """
        Optimizasyon geçmişini döndürür

        Returns:
            dict: İterasyon geçmişi
        """
        return self.history
