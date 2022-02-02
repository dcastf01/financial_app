import os
from typing import List
from binance.spot import Spot as Client
from src.pipeline.crypto.utils import (
    from_datetime_to_format_timestamp_to_binance_api,
    strdate_to_format_timestamp_to_binance_api, timestamp_from_api_to_date)

from datetime import date
import logging

logging


def get_clients(user):
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
    def __init__(self,client,) -> None:
        self.client:List[Client]=client

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
        start_time=from_datetime_to_format_timestamp_to_binance_api(date(year,12,31))
        end_time=from_datetime_to_format_timestamp_to_binance_api(date(year+1,1,1))
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

    

class Investment(ClientBaseClass):
    
    def __init__(self, client) -> None:
        super().__init__(client)

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
        begin_time=from_datetime_to_format_timestamp_to_binance_api(date(year,1,1))
        end_time=from_datetime_to_format_timestamp_to_binance_api(date(year,12,31))

        fiat=self._get_investment(begin_time,end_time)
        return fiat
    def get_investment_from_start_date_and_end_date(self,start_date:str,end_date:str,format_date:str="%d/%m/%Y"):

        begin_time=strdate_to_format_timestamp_to_binance_api(start_date,format_date)
        end_time=strdate_to_format_timestamp_to_binance_api(end_date,format_date)

        fiat=self._get_investment(begin_time,end_time)
        return fiat