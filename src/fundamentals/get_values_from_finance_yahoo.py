import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import datetime
from plotly.subplots import make_subplots
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


def display_year(z, year: int = None, month_lines: bool = True, fig=None, row: int = None):
    if year is None:
        num_years = len(z)//365
        year = datetime.datetime.now().year

    d1 = datetime.date(year, 1, 1)
    d2 = datetime.date(year, 12, 31)

    number_of_days = (d2 - d1).days + 1

    #data = np.ones(number_of_days) * np.nan
    #data[:len(z)] = z
    data = z

    delta = d2 - d1

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if number_of_days == 366:  # leap year
        month_days[1] = 29
    month_positions = (np.cumsum(month_days) - 15) / 7

    dates_in_year = [d1 + datetime.timedelta(i) for i in
                     range(delta.days + 1)]  # list with datetimes for each day a year
    weekdays_in_year = [i.weekday() for i in
                        dates_in_year]  # gives [0,1,2,3,4,5,6,0,1,2,3,4,5,6,…] (ticktext in xaxis dict translates this to weekdays

    weeknumber_of_dates = []
    for i in dates_in_year:
        inferred_week_no = int(i.strftime("%V"))
        if inferred_week_no >= 52 and i.month == 1:
            weeknumber_of_dates.append(0)
        elif inferred_week_no == 1 and i.month == 12:
            weeknumber_of_dates.append(53)
        else:
            weeknumber_of_dates.append(inferred_week_no)

    text = [str(i) for i in dates_in_year] # gives something like list of strings like ‘2018-01-25’ for each date. Used in data trace to make good hovertext.
    # 4cc417 green #347c17 dark green
    colorscale = [[False, '#eeeeee'], [True, '#76cf63']]

    # handle end of year

    data = [
        go.Heatmap(
            x=weeknumber_of_dates,
            y=weekdays_in_year,
            z=data,
            text=text,
            hovertemplate=
            "<b>%{text}</b><br><br>" +
            "Symbol: %{z}<br>" +
            "<extra></extra>",
            xgap=3,  # this
            ygap=3,  # and this is used to make the grid-like apperance
            showscale=False,
            colorscale=colorscale
        )
    ]

    if month_lines:
        kwargs = dict(
            mode='lines',
            line=dict(
                color='#9e9e9e',
                width=1,
            ),
            hoverinfo='skip',
        )

        for date, dow, wkn in zip(
                dates_in_year, weekdays_in_year, weeknumber_of_dates
        ):
            if date.day == 1:
                data += [
                    go.Scatter(
                        x=[wkn - .5, wkn - .5],
                        y=[dow - .5, 6.5],
                        **kwargs,
                    )
                ]
                if dow:
                    data += [
                        go.Scatter(
                            x=[wkn - .5, wkn + .5],
                            y=[dow - .5, dow - .5],
                            **kwargs,
                        ),
                        go.Scatter(
                            x=[wkn + .5, wkn + .5],
                            y=[dow - .5, -.5],
                            **kwargs,
                        )
                    ]

    layout = go.Layout(
        title='activity chart',
        height=250,
        yaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            autorange="reversed",
        ),
        xaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=month_names,
            tickvals=month_positions,
        ),
        font={'size': 10, 'color': '#9e9e9e'},
        plot_bgcolor=('#fff'),
        margin=dict(t=40),
        showlegend=False,
    )

    if fig is None:
        fig = go.Figure(data=data, layout=layout)
    else:
        fig.add_traces(data, rows=[(row + 1)] * len(data), cols=[1] * len(data))
        fig.update_layout(layout)
        fig.update_xaxes(layout['xaxis'])
        fig.update_yaxes(layout['yaxis'])

    return fig


def display_years(z, years):
    day_counter = 0

    fig = make_subplots(rows=len(years), cols=1, subplot_titles=years)
    for i, year in enumerate(years):
        d1 = datetime.date(year, 1, 1)
        d2 = datetime.date(year, 12, 31)

        number_of_days = (d2 - d1).days + 1
        data = z[day_counter: day_counter + number_of_days]

        display_year(data, year=year, fig=fig, row=i)
        fig.update_layout(height=250 * len(years))
        day_counter += number_of_days
    return fig


if __name__ == "__main__":

    z = np.random.randint(2, size=(50,))
    df_na9 = earning_calendar('NA9')

    display_year(df_na9)
    display_years(z, (2020, 2021, 2022))

    #df_ok = earning_calendar('ko', 'united states')
    df_na9 = earning_calendar('NA9')
