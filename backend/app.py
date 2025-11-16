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
            "risk_free_rate": 0.10
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
        risk_free_rate = data.get('risk_free_rate', 0.10)
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

        # Getirileri hesapla
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


if __name__ == '__main__':
    print("="*60)
    print("BIST100 Yapay Arı Kolonisi Portföy Optimizasyonu")
    print("="*60)
    print("\nSunucu başlatılıyor...")
    print("Web arayüzü: http://localhost:5000")
    print("\nÇıkmak için: CTRL+C")
    print("="*60)

    app.run(debug=True, host='0.0.0.0', port=5000)
