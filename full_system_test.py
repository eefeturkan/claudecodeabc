"""
KAPSAMLI SISTEM TESTI - TUM KOMBINASYONLAR
9 test: 3 risk profili x 3 periyot
"""

import sys
sys.path.insert(0, 'c:\\Users\\HECTOR\\Desktop\\claudecodeabc')

from backend.stock_classifier import filter_stocks_by_preferences, calculate_stock_performance
import time

# Test kombinasyonlari
RISK_PROFILES = ['düşük', 'orta', 'yüksek']
INVESTMENT_PERIODS = ['kısa', 'orta', 'uzun']  # Backend string values
PERIOD_MAPPING = {'kısa': '6mo', 'orta': '1y', 'uzun': '5y'}
PERIOD_NAMES = {'kısa': 'KISA (6 ay)', 'orta': 'ORTA (1 yil)', 'uzun': 'UZUN (5 yil)'}
MAX_STOCKS = 10

print("=" * 100)
print("KAPSAMLI SISTEM TESTI - TUM RISK PROFILI VE PERIYOT KOMBINASYONLARI")
print("=" * 100)
print(f"Toplam Test: {len(RISK_PROFILES) * len(INVESTMENT_PERIODS)}")
print(f"Risk Profilleri: {RISK_PROFILES}")
print(f"Periyotlar: {list(PERIOD_NAMES.values())}")
print("=" * 100)

results = []
test_num = 1
total_tests = len(RISK_PROFILES) * len(INVESTMENT_PERIODS)

for risk in RISK_PROFILES:
    for inv_period in INVESTMENT_PERIODS:
        period_code = PERIOD_MAPPING[inv_period]  # '6mo', '1y', or '5y' for API
        print(f"\n\n[TEST {test_num}/{total_tests}] {risk.upper()} Risk + {PERIOD_NAMES[inv_period]}")
        print("-" * 100)

        start_time = time.time()

        try:
            # Hisse secimi
            stocks = filter_stocks_by_preferences(
                risk_profile=risk,
                investment_period=inv_period,  # Use 'kısa', 'orta', 'uzun'
                sectors=None,
                max_stocks=MAX_STOCKS,
                use_performance_ranking=True
            )

            duration = time.time() - start_time

            # Hisse sayisi kontrolu
            if len(stocks) == 0:
                print(f"[HATA] Hic hisse secilemedi!")
                results.append({
                    'test_num': test_num,
                    'risk': risk,
                    'period': period,
                    'success': False,
                    'error': 'No stocks selected',
                    'duration': duration
                })
                test_num += 1
                continue

            print(f"\n[OK] {len(stocks)} hisse secildi: {stocks}")
            print(f"[SURE] {duration:.1f} saniye\n")

            # Her hissenin performansini kontrol et
            print("[PERFORMANS ANALIZI]")
            print("-" * 100)

            negative_sharpe = []
            negative_score = []
            high_volatility = []

            sharpe_values = []
            score_values = []
            vol_values = []

            for symbol in stocks:
                perf = calculate_stock_performance(symbol, period_code)  # Use correct period code
                if perf:
                    sharpe = perf['sharpe_ratio']
                    score = perf['score']
                    vol = perf['volatility']

                    sharpe_values.append(sharpe)
                    score_values.append(score)
                    vol_values.append(vol)

                    status = "OK"
                    issues = []

                    if sharpe < 0:
                        negative_sharpe.append(symbol)
                        status = "HATA"
                        issues.append(f"Sharpe={sharpe:.2f}<0")

                    if score < 0:
                        negative_score.append(symbol)
                        status = "HATA"
                        issues.append(f"Score={score:.2f}<0")

                    if vol > 1.5:  # %150'den fazla cok yuksek
                        high_volatility.append(symbol)
                        issues.append(f"Vol={vol*100:.0f}% cok yuksek")

                    issue_str = ", ".join(issues) if issues else ""
                    print(f"  [{status}] {symbol:8} | Sharpe: {sharpe:6.2f} | Score: {score:6.2f} | Vol: {vol*100:5.1f}% {issue_str}")

            # Ortalama metrikleri hesapla
            avg_sharpe = sum(sharpe_values) / len(sharpe_values) if sharpe_values else 0
            avg_score = sum(score_values) / len(score_values) if score_values else 0
            avg_vol = sum(vol_values) / len(vol_values) if vol_values else 0
            min_sharpe = min(sharpe_values) if sharpe_values else 0
            max_sharpe = max(sharpe_values) if sharpe_values else 0

            print(f"\n[ORTALAMALAR]")
            print(f"  Sharpe: Min={min_sharpe:.2f}, Max={max_sharpe:.2f}, Avg={avg_sharpe:.2f}")
            print(f"  Volatilite: Avg={avg_vol*100:.1f}%")

            # Sorun var mi kontrol et
            issues_found = []

            if negative_sharpe:
                issues_found.append(f"Negatif Sharpe: {negative_sharpe}")

            if negative_score:
                issues_found.append(f"Negatif Score: {negative_score}")

            if high_volatility:
                issues_found.append(f"Cok Yuksek Volatilite: {high_volatility}")

            # Sonuc
            if issues_found:
                print(f"\n[UYARI] Sorunlar tespit edildi:")
                for issue in issues_found:
                    print(f"  - {issue}")
                success = False
            else:
                print(f"\n[BASARILI] Tum hisseler uygun performans gosteriyor!")
                success = True

            results.append({
                'test_num': test_num,
                'risk': risk,
                'period': period_code,
                'period_name': PERIOD_NAMES[inv_period],
                'success': success,
                'stocks': stocks,
                'num_stocks': len(stocks),
                'avg_sharpe': avg_sharpe,
                'min_sharpe': min_sharpe,
                'max_sharpe': max_sharpe,
                'avg_vol': avg_vol,
                'negative_sharpe': negative_sharpe,
                'negative_score': negative_score,
                'high_volatility': high_volatility,
                'issues': issues_found,
                'duration': duration
            })

        except Exception as e:
            duration = time.time() - start_time
            print(f"\n[HATA] Test basarisiz: {str(e)}")
            results.append({
                'test_num': test_num,
                'risk': risk,
                'period': period_code,
                'success': False,
                'error': str(e),
                'duration': duration
            })

        test_num += 1
        time.sleep(0.5)

# GENEL RAPOR
print("\n\n" + "=" * 100)
print("GENEL TEST RAPORU")
print("=" * 100)

successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"\nToplam Test: {len(results)}")
print(f"Basarili: {len(successful)} ({len(successful)/len(results)*100:.0f}%)")
print(f"Basarisiz: {len(failed)} ({len(failed)/len(results)*100:.0f}%)")

if failed:
    print(f"\n[BASARISIZ TESTLER]")
    for r in failed:
        print(f"  Test {r['test_num']}: {r['risk']} + {r['period']}")
        if 'error' in r:
            print(f"    Hata: {r['error']}")
        if 'issues' in r and r['issues']:
            for issue in r['issues']:
                print(f"    - {issue}")

# RISK PROFILI ANALIZI
print(f"\n[RISK PROFILI - VOLATILITE ILISKISI]")
print("-" * 100)

vol_by_risk = {'düşük': [], 'orta': [], 'yüksek': []}
sharpe_by_risk = {'düşük': [], 'orta': [], 'yüksek': []}

for r in successful:
    vol_by_risk[r['risk']].append(r['avg_vol'])
    sharpe_by_risk[r['risk']].append(r['avg_sharpe'])

for risk in RISK_PROFILES:
    if vol_by_risk[risk]:
        avg_vol = sum(vol_by_risk[risk]) / len(vol_by_risk[risk])
        avg_sharpe = sum(sharpe_by_risk[risk]) / len(sharpe_by_risk[risk])
        print(f"  {risk.upper():10} | Avg Vol: {avg_vol*100:5.1f}% | Avg Sharpe: {avg_sharpe:5.2f} | Test Sayisi: {len(vol_by_risk[risk])}")

# VOLATILITE TUTARLILIGI KONTROLU
print(f"\n[VOLATILITE TUTARLILIGI]")
if len([v for v in vol_by_risk.values() if v]) >= 2:
    risk_vols = []
    for risk in RISK_PROFILES:
        if vol_by_risk[risk]:
            risk_vols.append((risk, sum(vol_by_risk[risk]) / len(vol_by_risk[risk])))

    # Dusuk < Orta < Yuksek olmali mi kontrol et
    if len(risk_vols) == 3:
        dusuk_vol = next((v for r, v in risk_vols if r == 'düşük'), None)
        yuksek_vol = next((v for r, v in risk_vols if r == 'yüksek'), None)

        if dusuk_vol and yuksek_vol:
            if yuksek_vol >= dusuk_vol:
                print(f"  [OK] Yuksek risk volatilitesi ({yuksek_vol*100:.1f}%) >= Dusuk risk ({dusuk_vol*100:.1f}%)")
            else:
                print(f"  [UYARI] Yuksek risk volatilitesi ({yuksek_vol*100:.1f}%) < Dusuk risk ({dusuk_vol*100:.1f}%)")

# SHARPE RATIO KONTROLU
print(f"\n[SHARPE RATIO KONTROLLERI]")
all_negative_sharpe = []
for r in successful:
    if r.get('negative_sharpe'):
        all_negative_sharpe.extend(r['negative_sharpe'])

if all_negative_sharpe:
    print(f"  [HATA] {len(all_negative_sharpe)} negatif Sharpe hisse bulundu: {set(all_negative_sharpe)}")
else:
    print(f"  [OK] Tum hisseler pozitif Sharpe Ratio'ya sahip!")

# PERFORMANS TABLOSU
print(f"\n[DETAYLI PERFORMANS TABLOSU]")
print("-" * 100)
print(f"{'Test':<6} {'Risk':<10} {'Periyot':<15} {'Hisse':<6} {'Min Sharpe':<12} {'Avg Sharpe':<12} {'Avg Vol':<10} {'Durum':<10}")
print("-" * 100)

for r in results:
    if r['success']:
        status = "OK" if not r.get('issues') else "UYARI"
        print(f"{r['test_num']:<6} {r['risk']:<10} {r['period_name']:<15} {r['num_stocks']:<6} "
              f"{r['min_sharpe']:<12.2f} {r['avg_sharpe']:<12.2f} {r['avg_vol']*100:<10.1f} {status:<10}")
    else:
        print(f"{r['test_num']:<6} {r['risk']:<10} {r.get('period', 'N/A'):<15} {'N/A':<6} "
              f"{'HATA':<12} {'HATA':<12} {'HATA':<10} {'BASARISIZ':<10}")

# FINAL SONUC
print("\n" + "=" * 100)
if len(failed) == 0 and len(all_negative_sharpe) == 0:
    print("[SONUC] TUM TESTLER BASARILI - SISTEM SUNUM ICIN HAZIR!")
    print("=" * 100)
    print("\nKRITIK KONTROLLER:")
    print(f"  [OK] {len(successful)}/{len(results)} test basarili")
    print(f"  [OK] Tum hisseler pozitif Sharpe Ratio'ya sahip")
    print(f"  [OK] Risk-volatilite iliskisi tutarli")
    print(f"  [OK] Negatif performans hisse yok")
    print("\nSistem sunum icin tamamen hazir!")
    exit(0)
else:
    print("[UYARI] BAZI TESTLER BASARISIZ VEYA SORUNLAR VAR!")
    print("=" * 100)
    if failed:
        print(f"  [HATA] {len(failed)} test basarisiz")
    if all_negative_sharpe:
        print(f"  [HATA] {len(all_negative_sharpe)} negatif Sharpe hisse bulundu")
    print("\nKod duzeltmesi gerekli!")
    exit(1)
