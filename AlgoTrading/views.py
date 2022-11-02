from django.http import HttpResponse
from django.shortcuts import render
from plotly.offline import plot
import yfinance as yf
import plotly.graph_objects as go
import vectorbt as vbt
import numpy as np
import pandas as pd


def logic(data=None):
    open_price = data.get('Open')
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




def index(request):
    if request.method=="GET":
        # print(request.GET.get('syb', False))
        period='6mo'
        symbol="BTC-USD"
        ticker = yf.Ticker(symbol)
        df=ticker.history(period=period)

        def candlestic():
            fig=df.vbt.ohlcv.plot()
            fig.update_layout(
                yaxis_title="Price ($)"
            )
            chart_fig = plot(fig, output_type='div')
            return chart_fig
        result_chart,pf=logic(data=df)
        return render(request,'index.html',{'data':candlestic(),'ticker':symbol,'result_chart':result_chart,'pf':pf})
    else:
        return HttpResponse(request.POST["syb"])