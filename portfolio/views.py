from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import StockHolding
import json
import yfinance as yf
from datetime import datetime, timedelta


# Popular stocks to display
POPULAR_STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'JNJ', 
                  'WMT', 'BA', 'DIS', 'NFLX', 'ADBE', 'PYPL', 'IBM', 'CSCO', 'INTC', 'AMD']


def get_stock_price(symbol):
    """Fetch current stock price"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')
        if len(data) > 0:
            return float(data['Close'].iloc[-1])
        return None
    except:
        return None


def get_stock_info(symbol):
    """Fetch detailed stock info"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            'name': info.get('longName', symbol),
            'price': info.get('currentPrice', 0),
            'change': info.get('regularMarketChange', 0),
            'changePercent': info.get('regularMarketChangePercent', 0),
            'marketCap': info.get('marketCap', 0),
            'pe': info.get('trailingPE', 'N/A'),
            '52WeekHigh': info.get('fiftyTwoWeekHigh', 0),
            '52WeekLow': info.get('fiftyTwoWeekLow', 0),
            'description': info.get('sector', 'N/A')
        }
    except:
        return None


def get_stock_history(symbol, days=30):
    """Fetch historical stock data for charts"""
    try:
        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        data = ticker.history(start=start_date, end=end_date)
        
        dates = [d.strftime('%Y-%m-%d') for d in data.index]
        prices = data['Close'].tolist()
        volumes = data['Volume'].tolist()
        
        return {
            'dates': dates,
            'prices': prices,
            'volumes': volumes
        }
    except:
        return None


@login_required(login_url="/login/")
def portfolio(request):
    """User's portfolio view"""
    if request.method == "POST":
        symbol = request.POST.get("symbol")
        quantity = request.POST.get("quantity")
        buy_price = request.POST.get("buy_price")

        if symbol and quantity and buy_price:
            StockHolding.objects.create(
                user=request.user,
                symbol=symbol.upper(),
                quantity=int(quantity),
                buy_price=float(buy_price)
            )
        return redirect("portfolio")

    holdings = StockHolding.objects.filter(user=request.user)
    
    holdings_with_prices = []
    total_invested = 0
    total_current_value = 0
    total_gain_loss = 0
    
    for holding in holdings:
        current_price = get_stock_price(holding.symbol)
        stock_info = get_stock_info(holding.symbol)
        
        if current_price:
            invested = holding.quantity * holding.buy_price
            current_value = holding.quantity * current_price
            gain_loss = current_value - invested
            gain_loss_percent = (gain_loss / invested * 100) if invested > 0 else 0
            
            holdings_with_prices.append({
                'id': holding.id,
                'symbol': holding.symbol,
                'quantity': holding.quantity,
                'buy_price': round(holding.buy_price, 2),
                'current_price': round(current_price, 2),
                'invested': round(invested, 2),
                'current_value': round(current_value, 2),
                'gain_loss': round(gain_loss, 2),
                'gain_loss_percent': round(gain_loss_percent, 2),
                'status': 'profit' if gain_loss >= 0 else 'loss',
                'stock_name': stock_info['name'] if stock_info else holding.symbol,
            })
            
            total_invested += invested
            total_current_value += current_value
            total_gain_loss += gain_loss
    
    symbols = [h['symbol'] for h in holdings_with_prices]
    quantities = [h['quantity'] for h in holdings_with_prices]
    current_values = [h['current_value'] for h in holdings_with_prices]
    
    chart_data = {
        'symbols': json.dumps(symbols),
        'quantities': json.dumps(quantities),
        'current_values': json.dumps(current_values),
    }
    
    total_gain_loss_percent = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0

    return render(request, "portfolio.html", {
        "holdings": holdings_with_prices,
        "chart_data": chart_data,
        "total_invested": round(total_invested, 2),
        "total_current_value": round(total_current_value, 2),
        "total_gain_loss": round(total_gain_loss, 2),
        "total_gain_loss_percent": round(total_gain_loss_percent, 2),
        "holdings_count": len(holdings_with_prices)
    })


def stocks_market(request):
    """Display all stocks with real-time data"""
    search_query = request.GET.get('search', '').upper()
    
    if search_query:
        stocks_list = [search_query]
    else:
        stocks_list = POPULAR_STOCKS
    
    stocks_data = []
    
    for symbol in stocks_list:
        stock_info = get_stock_info(symbol)
        current_price = get_stock_price(symbol)
        
        if stock_info and current_price:
            stocks_data.append({
                'symbol': symbol,
                'name': stock_info['name'],
                'price': round(current_price, 2),
                'change': round(stock_info['change'], 2),
                'changePercent': round(stock_info['changePercent'], 2),
                'pe': stock_info['pe'],
                'marketCap': stock_info['marketCap'],
                'sector': stock_info['description'],
                'high52': round(stock_info['52WeekHigh'], 2),
                'low52': round(stock_info['52WeekLow'], 2),
                'status': 'up' if stock_info['changePercent'] >= 0 else 'down'
            })
    
    return render(request, 'stocks_market.html', {
        'stocks': stocks_data,
        'search_query': search_query
    })


def stock_detail(request, symbol):
    """Display detailed stock info with charts"""
    symbol = symbol.upper()
    stock_info = get_stock_info(symbol)
    
    if not stock_info:
        return render(request, '404.html', {'message': f'Stock {symbol} not found'})
    
    # Get historical data
    history_30d = get_stock_history(symbol, 30)
    history_1y = get_stock_history(symbol, 365)
    
    # Chart data
    chart_data_30 = json.dumps({
        'dates': history_30d['dates'] if history_30d else [],
        'prices': history_30d['prices'] if history_30d else []
    }) if history_30d else '{}'
    
    chart_data_1y = json.dumps({
        'dates': history_1y['dates'] if history_1y else [],
        'prices': history_1y['prices'] if history_1y else []
    }) if history_1y else '{}'
    
    return render(request, 'stock_detail.html', {
        'symbol': symbol,
        'stock': stock_info,
        'chart_data_30': chart_data_30,
        'chart_data_1y': chart_data_1y
    })


def logout_view(request):
    logout(request)
    return redirect("/login/")