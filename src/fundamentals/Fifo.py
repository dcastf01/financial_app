import pandas as pd
import numpy as np

'''
df = df1 = pd.DataFrame({'Stock': [2,2,2,2,2,3,3,3,5,5,6],
                         'Date': ['2015-11-20', '2015-12-20', '2016-01-20', '2016-04-01', '2016-11-01', '2015-02-01', '2015-05-01',
                                              '2016-03-01', '2015-11-20', '2016-06-01', '2015-02-01'],
                         'Quantity': [20, 30, 60, -20, -10, 25, 15, -60, 50, -50, 35]})
'''
df = pd.read_csv('../../data/transactions.csv')


def final_portfolio(dfg):
    '''
    This function use the FiFo method to delete those transacctions in orden and return a snapshot of
    the portfolio with all opened positions.
    :param dfg: Dataframe of transacctions grouped by stocks and sorted by stock, date ascending
    :return: Datagrame with the portfolio after compute all sales with FiFo method.
    '''
    dfg['PN'] = np.where(dfg['Quantity'] > 0, 'P', 'N')
    dfg['CS'] = dfg.groupby(['Stock', 'PN'])['Quantity'].cumsum()
    if dfg[dfg['CS'] < 0]['Quantity'].count():
        subT = dfg[dfg['CS'] < 0]['CS'].iloc[-1]
        dfg['Quantity'] = np.where((dfg['CS'] + subT) <= 0, 0, dfg['Quantity'])
        dfg = dfg[dfg['Quantity'] > 0]
        if (len(dfg) > 0):
            dfg['Quantity'].iloc[0] = dfg['CS'].iloc[0] + subT
    return dfg


def FiFo2(dfg):
    '''

    :param dfg: Dataframe of transacctions grouped by stocks and sorted by stock, date ascending
    :return: Dataframe with pairs of buy - sales every 2 rows. Using the FiFo method
    '''
    df_prof = pd.DataFrame(columns=dfg.columns)
    if dfg[dfg['Quantity'] < 0]['Quantity'].count(): #si existe venta
        df_ventas = dfg[dfg['Quantity'] < 0].reset_index(drop=True)
        for index, row in df_ventas.iterrows():
            for index_dfg, row_dfg in dfg.iterrows():
                quantity_diff = row_dfg['Quantity']+row['Quantity']
                if quantity_diff <= 0:
                    row['Quantity'] = row['Quantity']+row_dfg['Quantity']
                    df_prof = df_prof.append(row_dfg)
                    df_prof = df_prof.append(row)
                    df_prof['Quantity'].iloc[-1] = -row_dfg['Quantity']
                    dfg = dfg[index+1:]
                    if quantity_diff == 0:
                        break
                elif quantity_diff > 0:
                    df_prof = df_prof.append(row_dfg)
                    df_prof['Quantity'].iloc[-1] = -row['Quantity']
                    df_prof = df_prof.append(row)
                    dfg['Quantity'].iloc[index] = row_dfg['Quantity']+row['Quantity']
                    break
    return df_prof


df = df.sort_values(by=['Stock', 'Date', 'Quantity'], ascending=[True, True, False])

dfR = df.groupby(['Stock'], as_index=False)\
    .apply(final_portfolio) \
    .drop(['CS', 'PN'], axis=1) \
    .reset_index(drop=True)

dfO = df.groupby(['Stock'], as_index=False)\
    .apply(FiFo2) \
    .reset_index(drop=True)

print(dfR[dfR['Quantity'] > 0])

