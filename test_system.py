# -*- coding: utf-8 -*-
"""
BIST100 Portfolio Optimizer - System Test Script
Tüm risk profili ve yatırım süresi kombinasyonlarını test eder
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

# Test kombinasyonları
RISK_PROFILES = ['düşük', 'orta', 'yüksek']
INVESTMENT_PERIODS = ['kısa', 'orta', 'uzun']

def test_optimize_with_preferences(risk_profile, investment_period, max_stocks=10, investment_amount=100000):
    """Belirli bir kombinasyonu test et"""
    url = f"{BASE_URL}/api/optimize-with-preferences"

    payload = {
        "risk_profile": risk_profile,
        "investment_period": investment_period,
        "max_stocks": max_stocks,
        "investment_amount": investment_amount,
        "colony_size": 50,
        "max_iterations": 100
    }

    try:
        response = requests.post(url, json=payload, timeout=300)
        data = response.json()
        return data
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_all_tests():
    """Tüm kombinasyonları test et"""
    results = []

    print("=" * 80)
    print("BIST100 PORTFÖY OPTİMİZASYONU - SİSTEM TESTİ")
    print("=" * 80)
    print()

    total_tests = len(RISK_PROFILES) * len(INVESTMENT_PERIODS)
    current_test = 0

    for risk in RISK_PROFILES:
        for period in INVESTMENT_PERIODS:
            current_test += 1
            print(f"\n[{current_test}/{total_tests}] Test: {risk.upper()} risk + {period.upper()} vade")
            print("-" * 60)

            start_time = time.time()
            result = test_optimize_with_preferences(risk, period)
            elapsed = time.time() - start_time

            test_result = {
                "risk_profile": risk,
                "investment_period": period,
                "elapsed_seconds": round(elapsed, 2),
                "success": result.get("success", False)
            }

            if result.get("success"):
                optimization = result.get("optimization", {})
                summary = optimization.get("summary", {})
                metrics = optimization.get("metrics", {})
                recommendation = result.get("recommendation", {})

                test_result.update({
                    "stocks_selected": len(recommendation.get("recommended_stocks", [])),
                    "stocks_with_weight": summary.get("stocks_with_weight", 0),
                    "expected_return_pct": round(summary.get("expected_annual_return_pct", 0), 2),
                    "volatility_pct": round(summary.get("volatility_pct", 0), 2),
                    "sharpe_ratio": round(summary.get("sharpe_ratio", 0), 4),
                    "sortino_ratio": round(metrics.get("sortino_ratio", 0), 4),
                    "max_drawdown": round(metrics.get("max_drawdown", 0) * 100, 2),
                    "expected_total_amount": round(optimization.get("expected_total_amount", 0), 2)
                })

                print(f"  [OK] BASARILI ({elapsed:.1f}s)")
                print(f"    Seçilen hisse: {test_result['stocks_selected']}")
                print(f"    Ağırlık verilen: {test_result['stocks_with_weight']}")
                print(f"    Beklenen Getiri: %{test_result['expected_return_pct']}")
                print(f"    Volatilite: %{test_result['volatility_pct']}")
                print(f"    Sharpe Ratio: {test_result['sharpe_ratio']}")
                print(f"    Sortino Ratio: {test_result['sortino_ratio']}")
                print(f"    Max Drawdown: %{test_result['max_drawdown']}")
                print(f"    Beklenen Toplam: {test_result['expected_total_amount']:,.0f} TL")
            else:
                error = result.get("error", "Bilinmeyen hata")
                test_result["error"] = error
                print(f"  [FAIL] BASARISIZ ({elapsed:.1f}s)")
                print(f"    Hata: {error[:200]}...")

            results.append(test_result)

    return results

def generate_report(results):
    """Test raporu oluştur"""
    print("\n")
    print("=" * 80)
    print("TEST RAPORU")
    print("=" * 80)

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"\nToplam Test: {len(results)}")
    print(f"Başarılı: {len(successful)}")
    print(f"Başarısız: {len(failed)}")

    if failed:
        print("\n--- BAŞARISIZ TESTLER ---")
        for r in failed:
            print(f"  - {r['risk_profile']} + {r['investment_period']}: {r.get('error', 'Bilinmeyen')[:100]}")

    if successful:
        print("\n--- PERFORMANS ÖZETİ ---")
        print(f"{'Risk':<10} {'Vade':<8} {'Getiri%':<10} {'Vol%':<8} {'Sharpe':<8} {'Sortino':<8} {'MaxDD%':<8}")
        print("-" * 70)

        for r in successful:
            print(f"{r['risk_profile']:<10} {r['investment_period']:<8} "
                  f"{r['expected_return_pct']:<10} {r['volatility_pct']:<8} "
                  f"{r['sharpe_ratio']:<8} {r['sortino_ratio']:<8} {r['max_drawdown']:<8}")

        # En iyi performanslar
        print("\n--- EN İYİ PERFORMANSLAR ---")

        best_return = max(successful, key=lambda x: x['expected_return_pct'])
        print(f"En Yüksek Getiri: {best_return['risk_profile']} + {best_return['investment_period']} = %{best_return['expected_return_pct']}")

        best_sharpe = max(successful, key=lambda x: x['sharpe_ratio'])
        print(f"En İyi Sharpe: {best_sharpe['risk_profile']} + {best_sharpe['investment_period']} = {best_sharpe['sharpe_ratio']}")

        lowest_vol = min(successful, key=lambda x: x['volatility_pct'])
        print(f"En Düşük Volatilite: {lowest_vol['risk_profile']} + {lowest_vol['investment_period']} = %{lowest_vol['volatility_pct']}")

        lowest_dd = min(successful, key=lambda x: x['max_drawdown'])
        print(f"En Düşük Max Drawdown: {lowest_dd['risk_profile']} + {lowest_dd['investment_period']} = %{lowest_dd['max_drawdown']}")

    # Mantık kontrolleri
    print("\n--- MANTIK KONTROLLERİ ---")

    checks_passed = 0
    checks_total = 0

    # 1. Yüksek risk > Düşük risk volatilite kontrolü
    checks_total += 1
    high_risk_vol = [r['volatility_pct'] for r in successful if r['risk_profile'] == 'yüksek']
    low_risk_vol = [r['volatility_pct'] for r in successful if r['risk_profile'] == 'düşük']

    if high_risk_vol and low_risk_vol:
        avg_high = sum(high_risk_vol) / len(high_risk_vol)
        avg_low = sum(low_risk_vol) / len(low_risk_vol)
        if avg_high >= avg_low:
            print(f"[OK] Yuksek risk volatilitesi ({avg_high:.1f}%) >= Dusuk risk ({avg_low:.1f}%)")
            checks_passed += 1
        else:
            print(f"[!] UYARI: Yuksek risk volatilitesi ({avg_high:.1f}%) < Dusuk risk ({avg_low:.1f}%)")

    # 2. Sharpe ratio pozitif mi?
    checks_total += 1
    positive_sharpe = all(r['sharpe_ratio'] > 0 for r in successful)
    if positive_sharpe:
        print("[OK] Tum Sharpe oranlari pozitif")
        checks_passed += 1
    else:
        negative = [r for r in successful if r['sharpe_ratio'] <= 0]
        print(f"[!] UYARI: {len(negative)} test negatif Sharpe orani verdi")

    # 3. Max drawdown makul aralikta mi?
    checks_total += 1
    max_dd_values = [r['max_drawdown'] for r in successful]
    if all(0 <= dd <= 100 for dd in max_dd_values):
        print(f"[OK] Max Drawdown degerleri makul aralikta (0-100%)")
        checks_passed += 1
    else:
        print(f"[!] UYARI: Max Drawdown degerleri anormal")

    # 4. Hisse secimi yapilmis mi?
    checks_total += 1
    all_have_stocks = all(r['stocks_with_weight'] > 0 for r in successful)
    if all_have_stocks:
        print(f"[OK] Tum testlerde en az 1 hisse secildi")
        checks_passed += 1
    else:
        zero_stocks = [r for r in successful if r['stocks_with_weight'] == 0]
        print(f"[!] UYARI: {len(zero_stocks)} testte hisse secilemedi")

    print(f"\nMantık Kontrolleri: {checks_passed}/{checks_total} geçti")

    return {
        "total_tests": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "checks_passed": checks_passed,
        "checks_total": checks_total
    }

if __name__ == "__main__":
    print("Test başlatılıyor...")
    print("(Bu işlem birkaç dakika sürebilir)")

    results = run_all_tests()
    summary = generate_report(results)

    # JSON olarak kaydet
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDetaylı sonuçlar: test_results.json")
    print("=" * 80)
