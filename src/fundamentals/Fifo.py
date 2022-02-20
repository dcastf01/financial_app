import pandas as pd
import numpy as np
from dateutil import relativedelta
import datetime
from forex_python.converter import CurrencyRates
from currency_converter import ECB_URL, CurrencyConverter
from pathlib import Path
import os
import shutil
import urllib.request
import sys


class Declaracion:

    @staticmethod
    def fifo(dfg, trade=True):
        """
        :param dfg: Dataframe of transacctions grouped by stocks and sorted by stock, date ascending
        :param trade: If Trade=True, then return the df with all pair buy-sell.
            If Trade=False, return a df with opened position after compute all sell transaction
        :return: Dataframe with pairs of buy - sales every 2 rows. Using the fifo method
        """
        df_compras = dfg[dfg['Quantity'] > 0].reset_index(drop=True)
        df_prof = pd.DataFrame(columns=dfg.columns)
        if dfg[dfg['Quantity'] < 0]['Quantity'].count():
            df_ventas = dfg[dfg['Quantity'] < 0].reset_index(drop=True)
            for index, row in df_ventas.iterrows():
                for index_dfg, row_dfg in df_compras.iterrows():
                    quantity_diff = row_dfg['Quantity'] + row['Quantity']
                    if quantity_diff <= 0:
                        row['Quantity'] = row['Quantity'] + row_dfg['Quantity']
                        df_prof = df_prof.append(row_dfg)
                        df_prof = df_prof.append(row)
                        df_prof['Quantity'].iloc[-1] = -row_dfg['Quantity']
                        df_compras = df_compras[1:]
                        if quantity_diff == 0:
                            break
                        else:
                            '''Las comisiones de venta solo se pueden sumar una vez, 
                            si ya se ha usado este registro se ponen a cero'''
                            row['Fees'] = np.nan
                            row['Exchange_Rate'] = np.nan
                    elif quantity_diff > 0:
                        df_prof = df_prof.append(row_dfg)
                        df_prof['Quantity'].iloc[-1] = -row['Quantity']
                        df_prof = df_prof.append(row)
                        '''Las comisiones de compra solo se pueden sumar una vez, 
                         si ya se ha usado este registro se ponen a cero'''
                        df_compras['Quantity'].iloc[index] = row_dfg['Quantity'] + row['Quantity']
                        df_compras['Fees'].iloc[index] = np.nan
                        df_compras['Exchange_Rate'].iloc[index] = np.nan
                        break
        if trade:
            return df_prof
        else:
            return df_compras

    @staticmethod
    def compensation_rules(dfg):
        """
        :param dfg: Dataframe of transacctions grouped by stocks and sorted by stock, date ascending
        :return: Dataframe with pairs of buy - sales every 2 rows. Using the fifo method
        """
        dfg['Compensation'] = 'Y'
        dfg['CS'] = dfg.groupby(['ISIN'])['Quantity'].cumsum()
        if dfg['CS'].iloc[-1] > 0:
            if dfg[dfg['Quantity'] < 0]['Quantity'].count():
                df_ventas = dfg[dfg['Quantity'] < 0]
                df_compras = dfg[dfg['Quantity'] > 0]
                for index, row in df_ventas.iterrows():
                    for index_dfg, row_dfg in df_compras.iterrows():
                        if row.Currency != 'EUR':
                            date_inf = row['Date'] + relativedelta.relativedelta(months=-12)
                            date_sup = row['Date'] + relativedelta.relativedelta(months=12)
                        else:
                            date_inf = row['Date'] + relativedelta.relativedelta(months=-2)
                            date_sup = row['Date'] + relativedelta.relativedelta(months=2)
                        if date_inf < row_dfg['Date'] < date_sup:
                            dfg['Compensation'].loc[index] = 'N'
        return dfg

    def one_line(self, df):
        df_one_line = pd.DataFrame()
        for i in range(0, len(df), 2):
            df_slide = df.iloc[i: i + 2]
            df_slide_one_line = df_slide.iloc[0, 0:4].copy()
            df_slide_one_line['Currency'] = df_slide['Currency'].iloc[0]
            df_slide_one_line['Buy_Net_Value'] = df_slide['Net_Value_EUR'].iloc[0]
            df_slide_one_line['Sell_Net_Value'] = df_slide['Net_Value_EUR'].iloc[1]
            df_slide_one_line['Compensation'] = df_slide['Compensation'].iloc[1]
            df_one_line = df_one_line.append(df_slide_one_line)

            df_one_line = self.profit_and_loss(df_one_line)
            df_one_line['Compensation'] = np.select([df_one_line['PnL'] > 0], ['Y'],
                                                    default=df_one_line['Compensation'])

        return df_one_line

    @staticmethod
    def auto_fx(df):
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
        df['AutoFx'] = np.select([((df['Date'].dt.date >= datetime.date(2021, 12, 20)) & (df['Currency'] != 'EUR')),
                                  ((df['Date'].dt.date < datetime.date(2021, 12, 20)) & (df['Currency'] != 'EUR'))],
                                 [np.round(-abs(0.0025 * df['Gross_Value_EUR']), decimals=2),
                                  np.round(-abs(0.001 * df['Gross_Value_EUR']), decimals=2)],
                                 default=np.nan)
        return df

    @staticmethod
    def net_value(df):
        df['Net_Value_EUR'] = abs(df[["Gross_Value_EUR", "Fees", "AutoFx"]].sum(axis=1))
        return df

    @staticmethod
    def profit_and_loss(df):
        df['PnL'] = df["Sell_Net_Value"] - df["Buy_Net_Value"]
        return df

    def stock_statements(self, df):
        df = self.one_line(df)
        df[['Buy_Net_Value', 'Sell_Net_Value']] = df.groupby(['ISIN', 'Compensation'])[
            'Buy_Net_Value', 'Sell_Net_Value'].transform('sum')
        df.drop_duplicates(subset=['Buy_Net_Value', 'Sell_Net_Value'], inplace=True)
        return df

    @staticmethod
    def currency_converter(amount, currency, new_currency='EUR', date=datetime.date.today()):
        filename = f"ecb_{datetime.date.today():%Y%m%d}.zip"
        ruta = '../../data/currency_convert/'
        if not os.path.isfile(os.path.join(ruta, filename)):
            urllib.request.urlretrieve(ECB_URL, filename)
            for file in os.listdir(ruta):
                file_path = os.path.join(ruta, file)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
            shutil.move(os.path.join(os.getcwd(),filename), ruta + filename)
        c = CurrencyConverter(ruta + filename)
        c_forex = CurrencyRates()
        if isinstance(amount, str):
            amount = float(amount.replace(',', '.'))
        try:
            currency = c.convert(amount, currency, new_currency, date=date)
        except:
            currency = c_forex.convert(currency, new_currency, amount, date)
        currency = str(round(currency, 2))
        return currency

    def dividend_statement(self, df):
        df = df[df['Description'] == 'Dividendo']
        df['Local_Currency'] = 'EUR'
        df['Local_Gross_Income'] = df.apply(lambda row: self.currency_converter(row['Gross_Income'], row['Currency'], 'EUR',  date=self.strtodate(row['Date'])), axis=1)
        return df

    @staticmethod
    def strtodate(date):
        strordate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        return strordate


if __name__ == "__main__":
    declaracion = Declaracion()
    dividendos = pd.read_csv('../../data/account_overview.csv')
    dividendos = declaracion.dividend_statement(dividendos)

    '''df = pd.read_csv('../../data/transactions.csv')

    df = df.sort_values(by=['ISIN', 'Date', 'Quantity'], ascending=[True, True, False]).reset_index(drop=True)
    df = declaracion.auto_fx(df)
    df = declaracion.net_value(df)

    df = df.groupby(['ISIN'], as_index=False) \
        .apply(declaracion.compensation_rules) \
        .drop(['CS'], axis=1) \
        .reset_index(drop=True)

    dfOut = df.groupby(['ISIN'], as_index=False) \
        .apply(declaracion.fifo) \
        .reset_index(drop=True)

    snapshot_df = df.groupby(['ISIN'], as_index=False) \
        .apply(declaracion.fifo, trade=False) \
        .reset_index(drop=True)

    declaracion = declaracion.stock_statements(dfOut)'''

    print('ei')
