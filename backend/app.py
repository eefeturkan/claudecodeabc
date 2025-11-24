"""
Flask Web Uygulaması - BIST100 ABC Portföy Optimizasyonu
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os

# Backend modüllerini import et
sys.path.insert(0, os.path.dirname(__file__))

from bist100_stocks import get_stock_list, get_yahoo_symbols, get_stock_name
from data_fetcher import DataFetcher
from portfolio_optimizer import PortfolioOptimizer
from stock_classifier import (
    get_available_sectors,
    filter_stocks_by_preferences,
    get_recommendation_summary,
    RISK_PROFILES,
    INVESTMENT_PERIODS,
    NoStocksFoundError
)

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# Global değişkenler
data_fetcher = DataFetcher()


@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """
    BIST100 hisse listesini döndürür

    Returns:
        JSON: Hisse listesi
    """
    try:
        stocks = get_stock_list()

        # Liste formatına çevir
        stock_list = [
            {'symbol': symbol, 'name': name}
            for symbol, name in stocks.items()
        ]

        return jsonify({
            'success': True,
            'stocks': stock_list
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/optimize', methods=['POST'])
def optimize_portfolio():
    """
    Portföy optimizasyonunu çalıştırır

    Request JSON:
        {
            "symbols": ["AKBNK", "GARAN", ...],
            "period": "1y",
            "objective": "sharpe",
            "colony_size": 50,
            "max_iterations": 100,
            "min_weight": 0.0,
            "max_weight": 0.5,
            "risk_free_rate": 0.45
        }

    Returns:
        JSON: Optimizasyon sonuçları
    """
    try:
        # Request verilerini al
        data = request.get_json()

        symbols = data.get('symbols', [])
        period = data.get('period', '1y')
        objective = data.get('objective', 'sharpe')
        colony_size = data.get('colony_size', 50)
        max_iterations = data.get('max_iterations', 100)
        min_weight = data.get('min_weight', 0.0)
        max_weight = data.get('max_weight', 0.5)
        risk_free_rate = data.get('risk_free_rate', 0.45)
        investment_amount = data.get('investment_amount', 100000)

        # Validasyon
        if not symbols or len(symbols) < 2:
            return jsonify({
                'success': False,
                'error': 'En az 2 hisse seçmelisiniz'
            }), 400

        # Yahoo Finance sembolleri
        yahoo_symbols = get_yahoo_symbols(symbols)

        # Veri çek
        print(f"Veri çekiliyor: {yahoo_symbols}")
        prices_df = data_fetcher.fetch_stock_data(
            yahoo_symbols,
            period=period,
            interval='1d'
        )

        if prices_df.empty:
            return jsonify({
                'success': False,
                'error': 'Veri çekilemedi. Lütfen sembolleri kontrol edin.'
            }), 400

        # Günlük getirileri hesapla
        returns_df = data_fetcher.calculate_returns(prices_df)

        if returns_df.empty or len(returns_df) < 10:
            return jsonify({
                'success': False,
                'error': 'Yeterli veri yok. Farklı bir periyot seçin.'
            }), 400

        # Sütun isimlerini düzelt (.IS kısmını kaldır)
        returns_df.columns = [col.replace('.IS', '') for col in returns_df.columns]

        # Portföy optimizasyonu
        print(f"Optimizasyon başlatılıyor: {objective}")
        optimizer = PortfolioOptimizer(
            returns_df=returns_df,
            risk_free_rate=risk_free_rate,
            min_weight=min_weight,
            max_weight=max_weight
        )

        results = optimizer.optimize(
            objective=objective,
            colony_size=colony_size,
            max_iterations=max_iterations,
            limit=100,
            verbose=True
        )

        # Hisse isimlerini ve TL tutarlarını ekle
        weights_with_names = []
        for symbol, weight in results['weights'].items():
            amount_tl = weight * investment_amount
            weights_with_names.append({
                'symbol': symbol,
                'name': get_stock_name(symbol),
                'weight': weight,
                'percentage': weight * 100,
                'amount_tl': amount_tl
            })

        # Ağırlığa göre sırala
        weights_with_names.sort(key=lambda x: x['weight'], reverse=True)

        # Response hazırla
        response = {
            'success': True,
            'objective': results['objective'],
            'investment_amount': investment_amount,
            'weights': weights_with_names,
            'metrics': results['metrics'],
            'history': results['history'],
            'summary': {
                'total_stocks': len(symbols),
                'stocks_with_weight': sum(1 for w in weights_with_names if w['weight'] > 0.001),
                'expected_return_pct': results['metrics']['expected_return'] * 100,
                'volatility_pct': results['metrics']['volatility'] * 100,
                'sharpe_ratio': results['metrics']['sharpe_ratio']
            }
        }

        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/validate', methods=['POST'])
def validate_symbols():
    """
    Sembollerin geçerliliğini kontrol eder

    Request JSON:
        {
            "symbols": ["AKBNK", "GARAN", ...]
        }

    Returns:
        JSON: Geçerli ve geçersiz semboller
    """
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])

        yahoo_symbols = get_yahoo_symbols(symbols)
        validation = data_fetcher.validate_symbols(yahoo_symbols)

        # .IS kısmını kaldır
        valid = [s.replace('.IS', '') for s in validation['valid']]
        invalid = [s.replace('.IS', '') for s in validation['invalid']]

        return jsonify({
            'success': True,
            'valid': valid,
            'invalid': invalid
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock-info/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """
    Belirli bir hisse hakkında bilgi

    Args:
        symbol: Hisse sembolü

    Returns:
        JSON: Hisse bilgileri
    """
    try:
        yahoo_symbol = f"{symbol}.IS"
        info = data_fetcher.get_stock_info(yahoo_symbol)

        return jsonify({
            'success': True,
            'info': info
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    """
    Mevcut sektör listesini döndürür

    Returns:
        JSON: Sektör listesi
    """
    try:
        sectors = get_available_sectors()

        return jsonify({
            'success': True,
            'sectors': sectors
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/preferences', methods=['GET'])
def get_preferences_info():
    """
    Risk profilleri ve yatırım periyotları hakkında bilgi döndürür

    Returns:
        JSON: Tercih seçenekleri
    """
    try:
        return jsonify({
            'success': True,
            'risk_profiles': {
                key: {
                    'description': value['description'],
                    'sectors': value['sectors']
                }
                for key, value in RISK_PROFILES.items()
            },
            'investment_periods': {
                key: {
                    'description': value['description'],
                    'period': value['period'],
                    'focus': value['focus']
                }
                for key, value in INVESTMENT_PERIODS.items()
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recommend', methods=['POST'])
def recommend_stocks():
    """
    Kullanıcı tercihlerine göre hisse önerir

    Request JSON:
        {
            "risk_profile": "orta",
            "investment_period": "orta",
            "sectors": ["Teknoloji", "Bankacılık"],
            "max_stocks": 10
        }

    Returns:
        JSON: Önerilen hisseler
    """
    try:
        data = request.get_json()

        risk_profile = data.get('risk_profile', 'orta')
        investment_period = data.get('investment_period', 'orta')
        sectors = data.get('sectors', None)  # None = tüm sektörler
        max_stocks = data.get('max_stocks', 10)

        # Öneri oluştur
        recommendation = get_recommendation_summary(
            risk_profile=risk_profile,
            investment_period=investment_period,
            sectors=sectors,
            max_stocks=max_stocks
        )

        # Hisse isimlerini ekle
        stocks_with_names = [
            {
                'symbol': symbol,
                'name': get_stock_name(symbol)
            }
            for symbol in recommendation['recommended_stocks']
        ]

        recommendation['stocks_with_names'] = stocks_with_names

        return jsonify({
            'success': True,
            'recommendation': recommendation
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/optimize-with-preferences', methods=['POST'])
def optimize_with_preferences():
    """
    Kullanıcı tercihlerine göre hisse önerir VE portföy optimizasyonu yapar

    Request JSON:
        {
            "risk_profile": "orta",
            "investment_period": "orta",
            "sectors": ["Teknoloji", "Bankacılık"],
            "max_stocks": 10,
            "colony_size": 50,
            "max_iterations": 100,
            "min_weight": 0.0,
            "max_weight": 0.5,
            "risk_free_rate": 0.45,
            "investment_amount": 100000
        }

    Returns:
        JSON: Önerilen hisseler + Optimizasyon sonuçları
    """
    try:
        data = request.get_json()

        # Tercihler
        risk_profile = data.get('risk_profile', 'orta')
        investment_period = data.get('investment_period', 'orta')
        sectors = data.get('sectors', None)
        max_stocks = data.get('max_stocks', 10)

        # Optimizasyon parametreleri
        colony_size = data.get('colony_size', 50)
        max_iterations = data.get('max_iterations', 100)
        min_weight = data.get('min_weight', 0.0)
        max_weight = data.get('max_weight', 0.30)  # Varsayılan %30 - daha iyi çeşitlendirme
        risk_free_rate = data.get('risk_free_rate', 0.45)
        investment_amount = data.get('investment_amount', 100000)

        # ZORUNLU ÇEŞİTLENDİRME: Her hisseye minimum ağırlık ver
        # Bu sayede tek hisseye %100 vermesi engellenecek
        if max_stocks >= 5:
            # 5+ hisse için: Her hisse en az %5, en fazla %30
            min_weight = max(min_weight, 0.05)
            max_weight = min(max_weight, 0.30)
        elif max_stocks >= 3:
            # 3-4 hisse için: Her hisse en az %10, en fazla %40
            min_weight = max(min_weight, 0.10)
            max_weight = min(max_weight, 0.40)
        else:
            # 2 hisse için: Her hisse en az %20, en fazla %50
            min_weight = max(min_weight, 0.20)
            max_weight = min(max_weight, 0.50)

        # Öneri oluştur
        recommendation = get_recommendation_summary(
            risk_profile=risk_profile,
            investment_period=investment_period,
            sectors=sectors,
            max_stocks=max_stocks
        )

        symbols = recommendation['recommended_stocks']
        period = recommendation['investment_period']['period']

        # Risk profiline göre amaç fonksiyonu belirle
        # NOT: Hem max_return hem min_variance tek hisseye %100 verebildiği için
        # TÜM risk profilleri için sharpe kullanıyoruz
        # Çeşitlendirme max_weight ile kontrol edilir
        objective = 'sharpe'

        # Risk profiline göre risk_free_rate'i ayarla (daha hassas optimizasyon için)
        # Düşük risk: Daha yüksek risk-free rate = daha muhafazakar
        # Yüksek risk: Daha düşük risk-free rate = daha agresif

        print(f"Önerilen hisseler: {symbols}")
        print(f"Periyot: {period}, Amaç: {objective}")
        print(f"Ağırlık kısıtları: Min %{min_weight*100:.1f}, Max %{max_weight*100:.1f}")

        # Yahoo Finance sembolleri
        yahoo_symbols = get_yahoo_symbols(symbols)

        # Veri çek
        prices_df = data_fetcher.fetch_stock_data(
            yahoo_symbols,
            period=period,
            interval='1d'
        )

        if prices_df.empty:
            return jsonify({
                'success': False,
                'error': 'Veri çekilemedi. Lütfen farklı tercihler deneyin.'
            }), 400

        # Günlük getirileri hesapla
        returns_df = data_fetcher.calculate_returns(prices_df)

        if returns_df.empty or len(returns_df) < 10:
            return jsonify({
                'success': False,
                'error': 'Yeterli veri yok. Farklı tercihler deneyin.'
            }), 400

        # Sütun isimlerini düzelt
        returns_df.columns = [col.replace('.IS', '') for col in returns_df.columns]

        # Portföy optimizasyonu
        print(f"Optimizasyon başlatılıyor: {objective}")
        optimizer = PortfolioOptimizer(
            returns_df=returns_df,
            risk_free_rate=risk_free_rate,
            min_weight=min_weight,
            max_weight=max_weight
        )

        results = optimizer.optimize(
            objective=objective,
            colony_size=colony_size,
            max_iterations=max_iterations,
            limit=100,
            verbose=True
        )

        # Hisse isimlerini ve TL tutarlarını ekle
        weights_with_names = []
        for symbol, weight in results['weights'].items():
            amount_tl = weight * investment_amount
            weights_with_names.append({
                'symbol': symbol,
                'name': get_stock_name(symbol),
                'weight': weight,
                'percentage': weight * 100,
                'amount_tl': amount_tl
            })

        # Ağırlığa göre sırala
        weights_with_names.sort(key=lambda x: x['weight'], reverse=True)

        # Hisse bilgilerini ve sektör dağılımını ekle
        from stock_classifier import STOCK_SECTORS

        stocks_with_names = []
        sector_weights = {}

        for symbol in symbols:
            stock_info = {
                'symbol': symbol,
                'name': get_stock_name(symbol),
                'sector': STOCK_SECTORS.get(symbol, 'Diğer')
            }
            stocks_with_names.append(stock_info)

        # Sektör ağırlıklarını hesapla
        for weight_info in weights_with_names:
            symbol = weight_info['symbol']
            sector = STOCK_SECTORS.get(symbol, 'Diğer')
            if sector not in sector_weights:
                sector_weights[sector] = 0
            sector_weights[sector] += weight_info['weight']

        # Sektör dağılımı listesi
        sector_distribution = [
            {'sector': sector, 'weight': weight, 'percentage': weight * 100}
            for sector, weight in sector_weights.items()
        ]
        sector_distribution.sort(key=lambda x: x['weight'], reverse=True)

        # Periyot bilgisi
        period_years_map = {'6mo': 0.5, '1y': 1, '5y': 5}
        period_years = period_years_map.get(period, 1)

        # Bileşik getiri hesapla (compound return)
        annual_return = results['metrics']['expected_return']
        compound_return = (1 + annual_return) ** period_years - 1

        # Beklenen toplam para miktarı
        expected_total_amount = investment_amount * (1 + compound_return)

        # Response hazırla
        response = {
            'success': True,
            'recommendation': {
                'risk_profile': recommendation['risk_profile'],
                'investment_period': recommendation['investment_period'],
                'selected_sectors': recommendation['selected_sectors'],
                'recommended_stocks': stocks_with_names,
                'stock_count': len(symbols)
            },
            'optimization': {
                'objective': objective,
                'investment_amount': investment_amount,
                'period_years': period_years,
                'expected_total_amount': expected_total_amount,
                'weights': weights_with_names,
                'sector_distribution': sector_distribution,
                'metrics': results['metrics'],
                'history': results['history'],
                'summary': {
                    'total_stocks': len(symbols),
                    'stocks_with_weight': sum(1 for w in weights_with_names if w['weight'] > 0.001),
                    'expected_return_pct': results['metrics']['expected_return'] * 100,  # main.js uyumu
                    'expected_annual_return_pct': results['metrics']['expected_return'] * 100,  # main_new.js uyumu
                    'expected_total_return_pct': compound_return * 100,
                    'volatility_pct': results['metrics']['volatility'] * 100,
                    'sharpe_ratio': results['metrics']['sharpe_ratio']
                }
            }
        }

        return jsonify(response)

    except NoStocksFoundError as e:
        # Volatilite filtresinden gecen hisse bulunamadi - kullaniciya anlamli mesaj goster
        import traceback
        traceback.print_exc()

        # Risk profili aciklamasi
        risk_descriptions = {
            'düşük': 'Dusuk risk profili (%45 volatilite limiti)',
            'orta': 'Orta risk profili (%65 volatilite limiti)',
            'yüksek': 'Yuksek risk profili'
        }
        risk_desc = risk_descriptions.get(e.risk_profile, e.risk_profile)

        # Sektor listesi
        sector_list = ", ".join(e.sectors) if isinstance(e.sectors, list) else str(e.sectors)

        # Detayli hata mesaji
        detailed_message = (
            f"Sectiginiz sektorlerde ({sector_list}) {risk_desc} icin uygun hisse bulunamadi.\n\n"
            f"Sebep: {e.total_stocks_checked} hisse incelendi, ancak hicbiri "
            f"volatilite limitinin ({e.volatility_threshold:.0%}) altinda degil.\n\n"
            f"Oneriler:\n"
            f"- Farkli sektorler secmeyi deneyin\n"
            f"- Risk profilini 'orta' veya 'yuksek' olarak degistirin\n"
            f"- Birden fazla sektor secerek cesitliligi artirin"
        )

        return jsonify({
            'success': False,
            'error': detailed_message,
            'error_type': 'no_stocks_found',
            'details': {
                'risk_profile': e.risk_profile,
                'volatility_threshold': e.volatility_threshold,
                'sectors': e.sectors,
                'stocks_checked': e.total_stocks_checked
            }
        }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("="*60)
    print("BIST100 Yapay Arı Kolonisi Portföy Optimizasyonu")
    print("="*60)
    print("\nSunucu başlatılıyor...")
    print("Web arayüzü: http://localhost:5000")
    print("\nÇıkmak için: CTRL+C")
    print("="*60)

    app.run(debug=True, host='0.0.0.0', port=5000)
