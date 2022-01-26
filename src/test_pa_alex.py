import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
# import plotly.graph_objects as go
st.set_page_config(page_title='Financial Alex',  layout='wide', page_icon='random')
tickets=['KO','MSFT']

with st.spinner('Updating Report... ten paciencia'):
    choice=st.selectbox( "escoge una que veas que funciona", tickets)

    obj_ticket = yf.Ticker(choice)

    start_date = datetime(2021, 1, 1)
    end_date = datetime.today()
    df = obj_ticket.history(start=start_date,end=end_date)

    st.table(df)