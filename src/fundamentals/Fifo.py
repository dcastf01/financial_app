import pandas as pd
import numpy as np
from dateutil import relativedelta
import datetime


df = pd.read_csv('../../data/transactions.csv')


def FiFo(dfg, trade=True):
    '''
    :param dfg: Dataframe of transacctions grouped by stocks and sorted by stock, date ascending
    :return: Dataframe with pairs of buy - sales every 2 rows. Using the FiFo method
    '''
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


def regla_dos_meses(dfg):
    '''
    :param dfg: Dataframe of transacctions grouped by stocks and sorted by stock, date ascending
    :return: Dataframe with pairs of buy - sales every 2 rows. Using the FiFo method
    '''
    dfg['Compensation'] = 'Y'
    dfg['CS'] = dfg.groupby(['ISIN'])['Quantity'].cumsum()
    if dfg['CS'].iloc[-1] > 0:
        if dfg[dfg['Quantity'] < 0]['Quantity'].count():
            df_ventas = dfg[dfg['Quantity'] < 0]
            df_compras = dfg[dfg['Quantity'] > 0]
            for index, row in df_ventas.iterrows():
                for index_dfg, row_dfg in df_compras.iterrows():
                    date_inf = row['Date'] + relativedelta.relativedelta(months=-2)
                    date_sup = row['Date'] + relativedelta.relativedelta(months=2)
                    if date_inf < row_dfg['Date'] < date_sup:
                        dfg['Compensation'].loc[index] = 'N'
    return dfg


def one_line(df):
    df_one_line = pd.DataFrame()
    for i in range(0, len(df), 2):
        df_slide = df.iloc[i: i + 2]
        df_slide_one_line = df_slide.iloc[0, 0:4].copy()
        df_slide_one_line['Buy_Net_Value'] = df_slide['Net_Value_EUR'].iloc[0]
        df_slide_one_line['Sell_Net_Value'] = df_slide['Net_Value_EUR'].iloc[1]
        df_slide_one_line['Compensation'] = df_slide['Compensation'].iloc[1]
        df_one_line = df_one_line.append(df_slide_one_line)

    return df_one_line


def autoFx(df):
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
    df['AutoFx'] = np.select([((df['Date'].dt.date >= datetime.date(2021, 12, 20)) & (df['Currency'] != 'EUR')),
                              ((df['Date'].dt.date < datetime.date(2021, 12, 20)) & (df['Currency'] != 'EUR'))],
                             [np.round(-abs(0.0025 * df['Gross_Value_EUR']), decimals=2),
                              np.round(-abs(0.001 * df['Gross_Value_EUR']), decimals=2)],
                             default=np.nan)
    return df


def net_value(df):
    df['Net_Value_EUR'] = abs(df[["Gross_Value_EUR", "Fees", "AutoFx"]].sum(axis=1))
    return df


if __name__ == "__main__":
    df = df.sort_values(by=['ISIN', 'Date', 'Quantity'], ascending=[True, True, False]).reset_index(drop=True)
    df = autoFx(df)
    df = net_value(df)

    df = df.groupby(['ISIN'], as_index=False) \
        .apply(regla_dos_meses) \
        .drop(['CS'], axis=1) \
        .reset_index(drop=True)

    dfOut = df.groupby(['ISIN'], as_index=False) \
        .apply(FiFo) \
        .reset_index(drop=True)

    snapshot_df = df.groupby(['ISIN'], as_index=False) \
        .apply(FiFo, trade=False) \
        .reset_index(drop=True)

    a = one_line(dfOut)

    print(snapshot_df[snapshot_df['Quantity'] > 0])
