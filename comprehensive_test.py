"""
Kapsamlı Sistem Testi - Sunum Öncesi
Tüm risk profili ve vade kombinasyonlarını test eder
"""

import sys
import time
import json
from datetime import datetime
from backend.stock_classifier import filter_stocks_by_preferences
from backend.portfolio_optimizer import optimize_portfolio

# Test konfigürasyonu
RISK_PROFILES = ['düşük', 'orta', 'yüksek']
PERIODS = ['6mo', '1y', '5y']
PERIOD_NAMES = {'6mo': 'KISA', '1y': 'ORTA', '5y': 'UZUN'}
MAX_STOCKS = 10
INITIAL_INVESTMENT = 100000

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{'='*80}")
    print(f"{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{'='*80}\n")

def print_test_start(risk, period):
    period_name = PERIOD_NAMES[period]
    print(f"\n{Colors.BLUE}► Test: {risk.upper()} risk + {period_name} vade ({period}){Colors.RESET}")
    print("-" * 80)

def validate_stocks(stocks, risk_profile, period):
    """Seçilen hisseleri doğrula"""
    issues = []

    if len(stocks) == 0:
        issues.append("❌ Hiç hisse seçilmedi!")
        return issues

    if len(stocks) > MAX_STOCKS:
        issues.append(f"❌ Çok fazla hisse seçildi: {len(stocks)} > {MAX_STOCKS}")

    # Her hissenin performansını kontrol et
    from backend.stock_classifier import calculate_stock_performance

    negative_sharpe = []
    negative_score = []

    for symbol in stocks:
        perf = calculate_stock_performance(symbol, period)
        if perf:
            if perf['sharpe_ratio'] < 0:
                negative_sharpe.append(f"{symbol} (Sharpe={perf['sharpe_ratio']:.2f})")
            if perf['score'] < 0:
                negative_score.append(f"{symbol} (Score={perf['score']:.2f})")

    if negative_sharpe:
        issues.append(f"❌ Negatif Sharpe hisseler: {', '.join(negative_sharpe)}")
    if negative_score:
        issues.append(f"❌ Negatif Score hisseler: {', '.join(negative_score)}")

    return issues

def validate_optimization(result, stocks):
    """Optimizasyon sonuçlarını doğrula"""
    issues = []

    # Ağırlık kontrolü
    weights = result.get('weights', {})
    total_weight = sum(weights.values())

    if abs(total_weight - 1.0) > 0.01:
        issues.append(f"❌ Toplam ağırlık %100 değil: {total_weight*100:.2f}%")

    # Her hisseye ağırlık verilmiş mi?
    if len(weights) != len(stocks):
        issues.append(f"❌ Ağırlık sayısı hisse sayısıyla eşleşmiyor: {len(weights)} vs {len(stocks)}")

    # Sharpe ratio pozitif mi?
    sharpe = result.get('metrics', {}).get('sharpe_ratio', 0)
    if sharpe < 0:
        issues.append(f"❌ Negatif Sharpe Ratio: {sharpe:.4f}")

    # Volatilite makul mu?
    volatility = result.get('metrics', {}).get('volatility', 0)
    if volatility > 1.5:  # %150'den fazla
        issues.append(f"⚠️ Aşırı yüksek volatilite: {volatility*100:.2f}%")

    return issues

def run_single_test(risk_profile, period):
    """Tek bir test senaryosu çalıştır"""
    start_time = time.time()

    try:
        # 1. Hisse seçimi
        print(f"  🔍 Hisse seçimi yapılıyor...")
        stocks = filter_stocks_by_preferences(
            risk_profile=risk_profile,
            investment_period=period,
            sectors=None,
            max_stocks=MAX_STOCKS,
            use_performance_ranking=True
        )

        # Hisse seçimini doğrula
        stock_issues = validate_stocks(stocks, risk_profile, period)
        if stock_issues:
            return {
                'success': False,
                'error': '\n    '.join(stock_issues),
                'duration': time.time() - start_time,
                'stage': 'stock_selection'
            }

        print(f"  ✅ {len(stocks)} hisse seçildi: {stocks}")

        # 2. Optimizasyon
        print(f"  🤖 ABC optimizasyonu başlatılıyor...")
        result = optimize_portfolio(
            stocks=stocks,
            period=period,
            objective='sharpe',
            min_weight=0.05,
            max_weight=0.30
        )

        # Optimizasyonu doğrula
        opt_issues = validate_optimization(result, stocks)
        if opt_issues:
            return {
                'success': False,
                'error': '\n    '.join(opt_issues),
                'duration': time.time() - start_time,
                'stage': 'optimization',
                'stocks': stocks,
                'result': result
            }

        duration = time.time() - start_time

        return {
            'success': True,
            'stocks': stocks,
            'result': result,
            'duration': duration
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'duration': time.time() - start_time,
            'stage': 'exception'
        }

def analyze_results(results):
    """Tüm sonuçları analiz et ve tutarsızlıkları bul"""
    print_header("DETAYLI ANALİZ")

    issues = []

    # Başarılı testleri topla
    successful = {k: v for k, v in results.items() if v['success']}

    if len(successful) == 0:
        print(f"{Colors.RED}❌ Hiçbir test başarılı olmadı!{Colors.RESET}")
        return

    # 1. Volatilite - Risk İlişkisi
    print("\n📊 1. VOLATİLİTE - RİSK PROFİLİ İLİŞKİSİ")
    print("-" * 80)

    vol_by_risk = {'düşük': [], 'orta': [], 'yüksek': []}
    for (risk, period), data in successful.items():
        vol = data['result']['metrics']['volatility']
        vol_by_risk[risk].append(vol)

    avg_vols = {}
    for risk, vols in vol_by_risk.items():
        if vols:
            avg_vol = sum(vols) / len(vols)
            avg_vols[risk] = avg_vol
            print(f"  {risk.upper():10} → Ortalama Volatilite: {avg_vol*100:6.2f}%")

    # Volatilite kontrolü
    if len(avg_vols) >= 2:
        if 'düşük' in avg_vols and 'yüksek' in avg_vols:
            if avg_vols['yüksek'] <= avg_vols['düşük']:
                issues.append("❌ Yüksek risk volatilitesi düşük riskten düşük!")
            else:
                print(f"  {Colors.GREEN}✅ Volatilite artışı doğru (düşük→yüksek){Colors.RESET}")

    # 2. Sharpe Ratio Kontrolü
    print("\n📊 2. SHARPE RATIO KONTROLLERI")
    print("-" * 80)

    negative_sharpes = []
    for (risk, period), data in successful.items():
        sharpe = data['result']['metrics']['sharpe_ratio']
        if sharpe < 0:
            negative_sharpes.append(f"{risk}-{period}")
        print(f"  {risk:8} + {PERIOD_NAMES[period]:5} → Sharpe: {sharpe:7.4f}")

    if negative_sharpes:
        issues.append(f"❌ Negatif Sharpe testler: {', '.join(negative_sharpes)}")
    else:
        print(f"  {Colors.GREEN}✅ Tüm Sharpe değerleri pozitif{Colors.RESET}")

    # 3. Ağırlık Kontrolü
    print("\n📊 3. PORTFÖY AĞIRLIKLARI")
    print("-" * 80)

    weight_issues = []
    for (risk, period), data in successful.items():
        weights = data['result']['weights']
        total = sum(weights.values())
        min_w = min(weights.values())
        max_w = max(weights.values())

        if abs(total - 1.0) > 0.01:
            weight_issues.append(f"{risk}-{period}: toplam={total*100:.2f}%")

        print(f"  {risk:8} + {PERIOD_NAMES[period]:5} → Min: {min_w*100:5.2f}% | Max: {max_w*100:5.2f}% | Toplam: {total*100:6.2f}%")

    if weight_issues:
        issues.append(f"❌ Ağırlık toplamı hatalı: {', '.join(weight_issues)}")
    else:
        print(f"  {Colors.GREEN}✅ Tüm ağırlıklar %100 toplamında{Colors.RESET}")

    # 4. En İyi Performanslar
    print("\n📊 4. EN İYİ PERFORMANSLAR")
    print("-" * 80)

    best_return = max(successful.items(), key=lambda x: x[1]['result']['metrics']['expected_return'])
    best_sharpe = max(successful.items(), key=lambda x: x[1]['result']['metrics']['sharpe_ratio'])
    lowest_vol = min(successful.items(), key=lambda x: x[1]['result']['metrics']['volatility'])

    print(f"  🏆 En Yüksek Getiri: {best_return[0][0]}-{PERIOD_NAMES[best_return[0][1]]} = {best_return[1]['result']['metrics']['expected_return']*100:.2f}%")
    print(f"  🏆 En İyi Sharpe: {best_sharpe[0][0]}-{PERIOD_NAMES[best_sharpe[0][1]]} = {best_sharpe[1]['result']['metrics']['sharpe_ratio']:.4f}")
    print(f"  🏆 En Düşük Volatilite: {lowest_vol[0][0]}-{PERIOD_NAMES[lowest_vol[0][1]]} = {lowest_vol[1]['result']['metrics']['volatility']*100:.2f}%")

    # Sorunları raporla
    if issues:
        print(f"\n{Colors.RED}🚨 TESPIT EDILEN SORUNLAR:{Colors.RESET}")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"\n{Colors.GREEN}✅ TÜM KONTROLLER BAŞARILI - SİSTEM SUNUM İÇİN HAZIR!{Colors.RESET}")

def main():
    print_header("KAPSAMLI SİSTEM TESTİ - SUNUM ÖNCESİ KONTROL")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Toplam Test: {len(RISK_PROFILES) * len(PERIODS)}")
    print(f"Risk Profilleri: {', '.join(RISK_PROFILES)}")
    print(f"Periyotlar: {', '.join([f'{p} ({PERIOD_NAMES[p]})' for p in PERIODS])}")

    results = {}
    failed_tests = []

    test_num = 1
    total_tests = len(RISK_PROFILES) * len(PERIODS)

    for risk in RISK_PROFILES:
        for period in PERIODS:
            print_test_start(risk, period)
            print(f"  Test {test_num}/{total_tests}")

            result = run_single_test(risk, period)
            results[(risk, period)] = result

            if result['success']:
                metrics = result['result']['metrics']
                print(f"\n  {Colors.GREEN}✅ BAŞARILI{Colors.RESET} ({result['duration']:.1f}s)")
                print(f"    Hisse Sayısı: {len(result['stocks'])}")
                print(f"    Beklenen Getiri: {metrics['expected_return']*100:.2f}%")
                print(f"    Volatilite: {metrics['volatility']*100:.2f}%")
                print(f"    Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
                print(f"    Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
            else:
                print(f"\n  {Colors.RED}❌ BAŞARISIZ{Colors.RESET} ({result['duration']:.1f}s)")
                print(f"    Aşama: {result.get('stage', 'unknown')}")
                print(f"    Hata:\n    {result['error']}")
                failed_tests.append((risk, period, result['error']))

            test_num += 1
            time.sleep(0.5)  # Kısa bekleme

    # Sonuç analizi
    successful_count = sum(1 for r in results.values() if r['success'])

    print_header("TEST ÖZETI")
    print(f"Toplam Test: {total_tests}")
    print(f"Başarılı: {Colors.GREEN}{successful_count}{Colors.RESET}")
    print(f"Başarısız: {Colors.RED}{len(failed_tests)}{Colors.RESET}")
    print(f"Başarı Oranı: {successful_count/total_tests*100:.1f}%")

    if failed_tests:
        print(f"\n{Colors.RED}BAŞARISIZ TESTLER:{Colors.RESET}")
        for risk, period, error in failed_tests:
            print(f"  • {risk}-{PERIOD_NAMES[period]}: {error[:100]}...")

    # Detaylı analiz
    if successful_count > 0:
        analyze_results(results)

    # JSON rapor kaydet
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': total_tests,
        'successful': successful_count,
        'failed': len(failed_tests),
        'results': {}
    }

    for (risk, period), data in results.items():
        key = f"{risk}_{period}"
        if data['success']:
            report['results'][key] = {
                'success': True,
                'stocks': data['stocks'],
                'metrics': data['result']['metrics'],
                'duration': data['duration']
            }
        else:
            report['results'][key] = {
                'success': False,
                'error': data['error'],
                'stage': data.get('stage'),
                'duration': data['duration']
            }

    with open('sunum_test_raporu.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📄 Detaylı rapor kaydedildi: sunum_test_raporu.json")

    if successful_count == total_tests:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 TÜM TESTLER BAŞARILI - SİSTEM SUNUM İÇİN HAZIR!{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}⚠️ Bazı testler başarısız - kontrol gerekli{Colors.RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
