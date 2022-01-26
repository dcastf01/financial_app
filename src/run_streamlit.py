
import streamlit as st


st.set_page_config(page_title='CanarIAs',  layout='wide', page_icon=':money:')

#this is the header
 

t1, t2 = st.columns((0.07,1)) 

t1.image('images/index.png', width = 120)
t2.title("South Western Ambulance Service - Hospital Handover Report")