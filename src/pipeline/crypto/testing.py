#This api is 


import os

from dotenv import load_dotenv

load_dotenv('conf\local\.env')
# print(os.environ)
import datetime
import logging
import time
from datetime import date

import pandas as pd
from binance.lib.utils import config_logging
from binance.spot import Spot as Client
from src.pipeline.crypto.binance_functions import (Investment, Market, Spot,
                                                   Transactions, get_clients)
from src.pipeline.crypto.utils import (
    from_datetime_to_format_timestamp_to_binance_api,
    strdate_to_format_timestamp_to_binance_api, from_timestamp_api_binance_to_date)

config_logging(logging, logging.DEBUG)


clients = get_clients("USERXX")
client=clients[1]


market=Market(client)
print(market._all_symbols)

transactions=Transactions(client)
i=1
df=pd.DataFrame
for info_symbol in market._all_symbols:
    symbol=info_symbol['symbol']
    data=transactions.get_complete_trade_history(symbol)
    df_aux=pd.DataFrame(data)
    
    print(df.shape)
    i+=1
    if not df.empty:
        df=df.append(df_aux,ignore_index=True)
        print(i)
        print(df.head(20))
        print(df.describe())
 
df.to_csv(r'D:\programacion\Repositorios\financial_app\data\01_raw\userxx.csv')
# df=pd.read_csv(r'data\01_raw\part-00000-7e94a6f2-a4c2-492a-b072-8aaf82f06de7-c000.csv')
print(df.head())
print(df.groupby("Pair").count())
#Con esto se obtienen los intereses
# b=client.asset_dividend_record(
#     startTime=start_time,
#     endTime=end_time,
#     limit=500,
#     )
# print(b)
# df=pd.DataFrame(b['rows'])
print(df.head(50))

c=client.savings_purchase_record(lendingType="DAILY")
print(c)
spot=Spot(clients[1])
last_snapshot_2021=spot.get_last_snapshot_spot_from_year(2021)
df=pd.DataFrame(last_snapshot_2021['data']["balances"])
#recordar que necesito varias cuentas 
print(df.head())



# logging.info(a)
#With this we get all the year of investment into df
investment=Investment(clients[0])
fiat=investment.get_complete_year_of_investment(2021)
logging.info(fiat)

df=pd.DataFrame(fiat['data'])

df['indicatedAmount']=df['indicatedAmount'].astype(float)
print(df.head())
print(df.shape)
print(df.indicatedAmount)
print(df.indicatedAmount.sum())
#hasta aqui

