"""
HIZLI TEST - SADECE 1 YIL (ORTA VADE)
3 test: 3 risk profili x 1 periyot (1y)
"""

import sys
sys.path.insert(0, 'c:\\Users\\HECTOR\\Desktop\\claudecodeabc')

from backend.stock_classifier import filter_stocks_by_preferences, calculate_stock_performance
import time

# Sadece 1y test
RISK_PROFILES = ['düşük', 'orta', 'yüksek']
PERIOD = '1y'
MAX_STOCKS = 10

print("=" * 100)
print("HIZLI SISTEM TESTI - SADECE ORTA VADE (1 YIL)")
print("=" * 100)
print(f"Toplam Test: {len(RISK_PROFILES)}")
print(f"Risk Profilleri: {RISK_PROFILES}")
print(f"Periyot: 1 yil (1y)")
print("=" * 100)

results = []
test_num = 1

for risk in RISK_PROFILES:
    print(f"\n\n[TEST {test_num}/{len(RISK_PROFILES)}] {risk.upper()} Risk + ORTA VADE (1 yil)")
    print("-" * 100)

    start_time = time.time()

    try:
        # Hisse secimi
        stocks = filter_stocks_by_preferences(
            risk_profile=risk,
            investment_period='orta',  # Maps to 1y
            sectors=None,
            max_stocks=MAX_STOCKS,
            use_performance_ranking=True
        )

        duration = time.time() - start_time

        if len(stocks) == 0:
            print(f"[HATA] Hic hisse secilemedi!")
            results.append({
                'risk': risk,
                'success': False,
                'error': 'No stocks'
            })
            test_num += 1
            continue

        print(f"\n[OK] {len(stocks)} hisse secildi: {stocks}")
        print(f"[SURE] {duration:.1f} saniye\n")

        # Performans kontrolu
        print("[PERFORMANS KONTROLU]")
        print("-" * 100)

        issues = []
        for symbol in stocks:
            perf = calculate_stock_performance(symbol, PERIOD)
            if perf:
                sharpe = perf['sharpe_ratio']
                score = perf['score']
                vol = perf['volatility']

                status = "OK"
                problem = []

                if sharpe < 0:
                    status = "HATA"
                    problem.append(f"Sharpe={sharpe:.2f}<0")
                    issues.append(f"{symbol}: Negatif Sharpe")

                if score < 0:
                    status = "HATA"
                    problem.append(f"Score={score:.2f}<0")
                    issues.append(f"{symbol}: Negatif Score")

                prob_str = ", ".join(problem) if problem else ""
                print(f"  [{status}] {symbol:8} | Sharpe: {sharpe:6.2f} | Score: {score:6.2f} | Vol: {vol*100:5.1f}% {prob_str}")

        if issues:
            print(f"\n[UYARI] Sorunlar:")
            for issue in issues:
                print(f"  - {issue}")
            success = False
        else:
            print(f"\n[BASARILI] Tum hisseler uygun!")
            success = True

        results.append({
            'risk': risk,
            'success': success,
            'stocks': stocks,
            'issues': issues
        })

    except Exception as e:
        print(f"\n[HATA] Test basarisiz: {str(e)}")
        results.append({
            'risk': risk,
            'success': False,
            'error': str(e)
        })

    test_num += 1
    time.sleep(0.5)

# RAPOR
print("\n\n" + "=" * 100)
print("OZET RAPOR")
print("=" * 100)

successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"\nToplam: {len(results)} | Basarili: {len(successful)} | Basarisiz: {len(failed)}")

if failed:
    print(f"\n[BASARISIZ TESTLER]")
    for r in failed:
        print(f"  - {r['risk'].upper()}")
        if 'error' in r:
            print(f"    Hata: {r['error']}")
        if 'issues' in r and r['issues']:
            for issue in r['issues']:
                print(f"    {issue}")

# Negatif Sharpe toplami
all_issues = []
for r in successful + failed:
    if 'issues' in r:
        all_issues.extend(r['issues'])

print("\n" + "=" * 100)
if len(failed) == 0 and len(all_issues) == 0:
    print("[SONUC] TUM TESTLER BASARILI - SISTEM HAZIR!")
    print("=" * 100)
    print("\n  [OK] 3/3 risk profili test edildi")
    print("  [OK] Tum hisseler pozitif Sharpe/Score")
    print("  [OK] Negatif performans hisse yok")
    print("\nSistem sunum icin hazir!")
    exit(0)
else:
    print("[UYARI] SORUNLAR VAR!")
    print("=" * 100)
    if failed:
        print(f"  [HATA] {len(failed)} test basarisiz")
    if all_issues:
        print(f"  [HATA] {len(all_issues)} sorun bulundu")
    exit(1)
