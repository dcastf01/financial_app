import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import mfinancials as mf
import investpy

'''
- Calendario de proximos resultados --> investing
- Calendario de dividendos ¿?
- Noticias --> traducidas ¿? --> ¿degiro, marketscreener, yfinance?
- Calculo ratios históricos --> PER, EV/Ebitda, EV/FCF
- Conversion divisa estimates to financials 
'''

'''aapl = mf.Ticker("dole")
df_financial = aapl.financials.T
df_key_ratio = aapl.keyRatios.T
df_estimates = aapl.estimates.T
a = aapl.keyRatios'''

'''search_results = investpy.search_quotes(text='KO',
                                        products=['stocks'],
                                        countries=None,
                                        n_results=1)
search_results.retrieve_information()
'''


def earning_calendar(symbol, country=None, product=None):
    '''
    A partir del simbolo y el pais, recupera la información del stock si este está en la lista de stock.csv y sino
    lo busca el simbolo y recupera la primera coincidencia de investing.com


    :param symbol: symbol of the stock to retrieve its information from.
    :param country: name of the country from where the stock is from.
    :param product:
    :return:
    '''
    cols = ['Prev. Close', 'Todays Range', 'Revenue', 'Open', '52 wk Range',
               'EPS', 'Volume', 'Market Cap', 'Dividend (Yield)', 'Average Vol. (3m)', 'P/E Ratio',
               'Beta', '1-Year Change', 'Shares Outstanding', 'Next Earnings Date']

    if country and not isinstance(country, str):
        raise ValueError(
            "ERR#0128: countries filtering parameter is optional, but if specified, it"
            " must be a str."
        )
    if country:
        try:
            df = investpy.get_stock_information(symbol, country)
        except:
            search_results = investpy.search_quotes(text=symbol,
                                                    products=product,
                                                    countries=[country],
                                                    n_results=1)
            df1 = pd.DataFrame({'Stock Symbol': [search_results.symbol]})
            df2 = pd.DataFrame([search_results.retrieve_information().values()], columns=cols)
            df = pd.concat([df1, df2], axis=1)
    else:
        search_results = investpy.search_quotes(text=symbol,
                                                products=product,
                                                n_results=1)
        df1 = pd.DataFrame({'Stock Symbol': [search_results.symbol]})
        df2 = pd.DataFrame([search_results.retrieve_information().values()], columns=cols)
        df = pd.concat([df1, df2], axis=1)

    df = df[['Stock Symbol', 'Next Earnings Date']]
    return df


#df_ok = earning_calendar('ko', 'united states')
df_na9 = earning_calendar('NA9', 'germany')
