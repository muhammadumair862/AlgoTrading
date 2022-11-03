from django.http import HttpResponse
from django.shortcuts import render
from plotly.offline import plot
import yfinance as yf
import plotly.graph_objects as go
import vectorbt as vbt
import numpy as np
import pandas as pd


# Indicators
# $$$$$$$$$$$$   Strat    $$$$$$$$$
def rsi_algo(data = None):
    close_price = data.get('Close')

    rsi = vbt.RSI.run(close_price)
    
    entries = rsi.rsi_crossed_below(30)
    exits = rsi.rsi_crossed_above(70)
    
    pf = vbt.Portfolio.from_signals(
     init_cash=20000,
     close=close_price, 
     entries=entries, 
     exits=exits,
     size=100,
     size_type='value'
    )
    fig=pf.plot(settings=dict(bm_returns=False))

    chart_fig = plot(fig, output_type='div')
    return chart_fig,pf


def ma_algo(data = None):
    close_price = data.get('Close')

    ma_slow = vbt.MA.run(close_price,200)
    ma_fast = vbt.MA.run(close_price,20)
    
    entries = ma_fast
    exits = ma_slow
    
    pf = vbt.Portfolio.from_signals(
     init_cash=20000,
     close=close_price, 
     entries=entries, 
     exits=exits,
     size=100,
     size_type='value'
    )
    fig=pf.plot(settings=dict(bm_returns=False))

    chart_fig = plot(fig, output_type='div')
    return chart_fig,pf


def macd_algo(data = None):
    close_price = data.get('Close')

    rsi = vbt.RSI.run(close_price)
    
    entries = rsi.rsi_crossed_below(30)
    exits = rsi.rsi_crossed_above(70)
    
    pf = vbt.Portfolio.from_signals(
     init_cash=20000,
     close=close_price, 
     entries=entries, 
     exits=exits,
     size=100,
     size_type='value'
    )
    fig=pf.plot(settings=dict(bm_returns=False))

    chart_fig = plot(fig, output_type='div')
    return chart_fig,pf


# $$$$$$$$$$$$   End    $$$$$$$$$



def index(request, period='3mo', symbol="BTC-USD"):
    if request.method=="POST":
        symbol = request.POST['search']
    
    ticker = yf.Ticker(symbol)
    df=ticker.history(period=period)
    
    def candlestic():
            fig=df.vbt.ohlcv.plot()
            fig.update_layout(
                yaxis_title="Price ($)"
            )
            chart_fig = plot(fig, output_type='div')
            return chart_fig
        
    return render(request,'index.html',{'data':candlestic(),'ticker':symbol})

def protfolio(request):
    if request.method=="POST":
        period=str(request.POST['ticker_period'])+'d'
        symbol=request.POST['symbol']
        ticker = yf.Ticker(symbol)
        df=ticker.history(period=period)

        def candlestic():
            fig=df.vbt.ohlcv.plot()
            fig.update_layout(
                yaxis_title="Price ($)"
            )
            chart_fig = plot(fig, output_type='div')
            return chart_fig
        if request.POST['indicator_opt']=='rsi':
            result_chart,pf=rsi_algo(data=df)
        elif request.POST['indicator_opt']=='macd':
            result_chart,pf=rsi_algo(data=df)
        elif request.POST['indicator_opt']=='ma':
            result_chart,pf=rsi_algo(data=df)
        return render(request,'analysis.html',{'data':candlestic(),'ticker':symbol,'result_chart':result_chart,'pf':pf})
    else:
        return HttpResponse('You can not access this page')