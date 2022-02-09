import os
from typing import List,Optional
from binance.error import ClientError, ServerError
from binance.spot import Spot as Client
from src.pipeline.crypto.utils import (
    from_datetime_to_format_timestamp_to_binance_api,
    strdate_to_format_timestamp_to_binance_api, from_timestamp_api_binance_to_date)

from datetime import datetime
import logging
import pandas as pd
import time
from tqdm import tqdm
from enum import Enum

class EnumCandlestickChartIntervals(Enum):
    interval_1m='1m'
    interval_3m='3m'
    interval_5m='5m'
    interval_15m='15m'
    interval_30m='30m'
    interval_1h='1h'
    interval_2h='2h'
    interval_4h='4h'
    interval_6h='6h'
    interval_8h='8h'
    interval_12h='12h'
    interval_1d='1d'
    interval_3d='3d'
    interval_1w='1w'
    interval_1M='1M'
    
def get_clients(user:str):
    #maybe with a dicctionary is better
    keys=[key_or_secret for key_or_secret in os.environ if 'API_KEY_BINANCE' in key_or_secret  ]
    secrets=[key_or_secret for key_or_secret in os.environ if 'API_SECRET_BINANCE'in key_or_secret  ]
    api_keys=[os.environ[userid_account] for userid_account in keys 
        if  userid_account.split("_")[-2]==user ]
    api_secrets=[os.environ[userid_account] for userid_account in secrets 
        if userid_account.split("_")[-2]==user ]
    # api_key=os.environ['API_KEY_BINANCE_CUENTA']
    # api_secret=os.environ['API_SECRET_BINANCE_CUENTA']

    clients =[ Client(api_key, api_secret) for api_key,api_secret in zip(api_keys,api_secrets)]

    return clients
class ClientBaseClass:
    def __init__(self,client:Client,user_id:str='userxx',use_previous_data:bool=True) -> None:
        self.client=client
        self.user_id=user_id
        self.use_previous_data=use_previous_data
        self.data_folder=r'D:\programacion\Repositorios\financial_app\data\01_raw'
class Earn(ClientBaseClass):
    NotImplementedError
    def __init__(self,client,) -> None:
        super().__init__(client)

class Spot(ClientBaseClass):
    def __init__(self,client,) -> None:
        super().__init__(client)
        self.wallet_type="SPOT"
    def get_current_information(self):

        return self.client.account()
    def _get_snapshot_spot(self,start_time,end_time):
        return self.client.account_snapshot(
            type=self.wallet_type,
            startTime=start_time,
            endTime=end_time,
        )
    def get_last_snapshot_spot_from_year(self,year:int):
        #necessary two day if not we don't get data but only need the day 31
        start_time=from_datetime_to_format_timestamp_to_binance_api(datetime(year,12,31,23,59))
        end_time=from_datetime_to_format_timestamp_to_binance_api(datetime(year+1,1,1,0,0))
        snapshot=self._get_snapshot_spot(start_time,end_time)
        snapshot=snapshot['snapshotVos'][-1]
        return snapshot
    def get_snapshot_spot_from_start_date_and_end_date(self,start_date:str,end_date:str,format_date:str="%d/%m/%Y"):

        begin_time=strdate_to_format_timestamp_to_binance_api(start_date,format_date)
        end_time=strdate_to_format_timestamp_to_binance_api(end_date,format_date)

        return self._get_snapshot_spot(begin_time,end_time)
        
class Wallet(Spot,Earn):
    def __init__(self,client,) -> None:
        super().__init__(client)

class Market(ClientBaseClass):
    def __init__(self, client) -> None:
        super().__init__(client)
        self._exchange_info=self._get_exchange_info()
        
        self.file_symbols='symbols.csv'
        self.path_file_symbols=os.path.join(self.data_folder,self.file_symbols)
        self.file_last_price_of_year='last_price_of_year_2021.csv' #change 2021 per something and in the code use a replace
        self.path_file_last_price_of_year=os.path.join(self.data_folder,self.file_last_price_of_year)
        self.df_all_symbols=self._get_all_symbols()
        self.all_symbols=self.df_all_symbols['symbol'].unique()

    def _get_all_symbols(self):
        if os.path.isfile(self.path_file_symbols) and self.use_previous_data:
            df=pd.read_csv(self.path_file_symbols)
        else:
            exchange_info=self._get_exchange_info()
            df=pd.DataFrame(exchange_info['symbols'])
            logging.debug(df.head())
            df.to_csv(self.path_file_symbols)
        return df

    def _get_exchange_info(self):
        #This function need to sabe all the info and a refresh or something
        return self.client.exchange_info()

    def _check_if_symbols_are_in_local(self):
        return NotImplemented

    def _get_historic_candlestick_data(self, symbol,
        interval:Optional[EnumCandlestickChartIntervals]=EnumCandlestickChartIntervals.interval_1m,
        startTime:Optional[int]=None ,
        endTime:Optional[int]=None  ,):

        interval=interval.value
        return self.client.klines(
            symbol,
            interval,
            startTime=startTime,
            endTime=endTime
        )
    def get_last_minute_candlestick_data_from_year_all_symbols(self,year:int):
        #do the cache stuff
        if os.path.isfile(self.path_file_last_price_of_year) and self.use_previous_data:
            df=pd.read_csv(self.path_file_last_price_of_year)
        else:
            begin_time=from_datetime_to_format_timestamp_to_binance_api(datetime(year,12,31))
            end_time=from_datetime_to_format_timestamp_to_binance_api(datetime(year+1,1,1))
            columns=['Open time',
                'Open',
                'High',
                'Low',
                'Close',
                'Volume',
                'Close time',
                'Quote asset volume',
                'Number of trades',
                'Taker buy base asset volume',
                'Taker buy quote asset volume',
                'Ignore.'
                ]
            df=pd.DataFrame()
            for symbol in tqdm(self.all_symbols,desc=f'getting historic of symbols in year {year}'):
            
                data=self._get_historic_candlestick_data( symbol,startTime=begin_time,endTime=end_time)
                df_aux=pd.DataFrame(data,columns=columns)
                df_aux['symbol']=symbol
                df=df.append(df_aux,ignore_index=True)
            df.drop(columns='Ignore.',inplace=True)
            print(df.head())
            df.to_csv(self.path_file_last_price_of_year)
            return df
class Transactions(ClientBaseClass):

    def __init__(self, client,) -> None:
        super().__init__(client)
        
        self.complete_trade_history_file=f'complete_trade_{self.user_id}.csv'
        self.path_to_complete_trade_history=os.path.join(self.data_folder,self.complete_trade_history_file)
        
    def _get_trade_history(self,
        symbol,
        startTime:Optional[int]=None ,
        endTime:Optional[int]=None  ,
        rows=100):
        
        try:
            return self.client.my_trades(
                symbol=symbol,
                # startTime =startTime ,
                # endTime=endTime ,
                # rows=rows
            )
        except ClientError as e:
            
            a=e.args[-1]._store
            retry_after=e.args[-1]._store['retry-after'][1]

            logging.warning('Too much request weight used; current limit is 1200 request weight per 1 MINUTE. Please use the websocket for live updates to avoid polling the API.')
            logging.warning(f'We will wait {str(retry_after)}')
            time.sleep(int(retry_after))
            try:
                return self.client.my_trades(
                symbol=symbol,
                # startTime =startTime ,
                # endTime=endTime ,
                # rows=rows
            )
            except Exception as e:
                print(e)
            print("hi")

        except Exception as e:
            print(e)
            raise "unknow error"
        
    def get_trade_history_one_symbol(self,symbol)->dict:
        return self._get_trade_history(symbol)
        return 
    
    def get_complete_trade_history(self,all_symbols:Optional[list]=None)->pd.DataFrame:
        #something of cache here
        if os.path.isfile(self.path_to_complete_trade_history) and self.use_previous_data:
            df=pd.read_csv(self.path_to_complete_trade_history)
        else:
            df=pd.DataFrame() #read from previous one and decide if get this data or not

            for symbol in tqdm(all_symbols,desc=f'gettingthe name of all symbols'):
           
                data=self.get_trade_history_one_symbol(symbol)
                df_aux=pd.DataFrame(data)
                
                if not df_aux.empty:
                    df=df.append(df_aux,ignore_index=True)
            df.to_csv(self.path_to_complete_trade_history)
        return df

class Investment(ClientBaseClass):
    
    def __init__(self, client) -> None:
        super().__init__(client)
        self.investment_file=f'investment_{self.user_id}.csv'
        
    def _get_investment(self,begin_time:int,end_time:int)->dict:
        #probably we need the withdraw but now only the investment
        
        try:
            fiat=self.client.fiat_order_history(transactionType =0,
            beginTime  =begin_time,
            endTime =end_time
            )
            return fiat
        except Exception as e:
            logging.error(e)

    def get_complete_year_of_investment(self,year:int)->dict:
        begin_time=from_datetime_to_format_timestamp_to_binance_api(datetime(year,1,1))
        end_time=from_datetime_to_format_timestamp_to_binance_api(datetime(year,12,31))

        fiat=self._get_investment(begin_time,end_time)
        return fiat
    
    def get_investment_from_start_date_and_end_date(self,start_date:str,end_date:str,format_date:str="%d/%m/%Y"):

        begin_time=strdate_to_format_timestamp_to_binance_api(start_date,format_date)
        end_time=strdate_to_format_timestamp_to_binance_api(end_date,format_date)

        fiat=self._get_investment(begin_time,end_time)
        return fiat

class BinanceUser(Investment,Transactions,Market,Wallet):
    def __init__(self, client) -> None:
        super().__init__(client)

