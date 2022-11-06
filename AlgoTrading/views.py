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
def rsi_algo(data = None, period=14):
    close_price = data.get('Close')

    rsi = vbt.RSI.run(close_price, period)
    
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


def ma_algo(data = None, fast=14, slow=200):
    close_price = data.get('Close')

    ma_slow = vbt.MA.run(close_price, slow)
    ma_fast = vbt.MA.run(close_price, fast)
    
    entries = ma_slow.ma_crossed_above(ma_fast.ma)
    exits = ma_slow.ma_crossed_below(ma_fast.ma)
    
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


def macd_algo(data = None, fastperiod=12, slowperiod=26, signalperiod=9):
    close_price = data.get('Close')

    macd = vbt.MACD.run(close_price, fastperiod, slowperiod,
                                     signalperiod)
    
    entries = macd.macd_crossed_above(macd.signal)
    exits = macd.macd_crossed_below(macd.signal)
    
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
        df.index=df.index.strftime('%Y-%m-%d %H:%M:%S')

        def candlestic():
            fig=df.vbt.ohlcv.plot()
            fig.update_layout(
                yaxis_title="Price ($)"
            )
            chart_fig = plot(fig, output_type='div')
            return chart_fig

        if request.POST['indicator_opt']=='rsi':
            if request.POST['rsi']=='':
                result_chart,pf=rsi_algo(data=df)
            else:
                result_chart,pf=rsi_algo(data=df,period=int(request.POST['rsi']))
                

        elif request.POST['indicator_opt']=='macd':
            if request.POST['macd_fast']=='':
                result_chart,pf= macd_algo(data=df)
            else:
                result_chart,pf= macd_algo(data=df, fastperiod=int(request.POST['macd_fast']),
                                            slowperiod= int(request.POST['macd_slow']),
                                            signalperiod= int(request.POST['macd_signal']))
        
        elif request.POST['indicator_opt']=='ma':
            if request.POST['ma_fast']=='':
                result_chart,pf= ma_algo(data=df)
            else:
                result_chart,pf= ma_algo(data=df, fast=int(request.POST['ma_fast']),
                                            slow= int(request.POST['ma_slow']))
        return render(request,'analysis.html',{'data':candlestic(),'ticker':symbol,'result_chart':result_chart,'pf':pf})
    else:
        return HttpResponse('You can not access this page')