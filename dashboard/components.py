import streamlit as st
from .filters import csv_bytes
from .formatting import number

def cards(values):
    # Render row by row so narrow screens retain the intended KPI reading order.
    for start in range(0,len(values),3):
        row=values[start:start+3]
        for column,(label,value,kind) in zip(st.columns(len(row)),row):
            column.metric(label,number(value,kind))

def plot(fig,key): st.plotly_chart(fig,use_container_width=True,key=key,config={'displaylogo':False,'responsive':True})

def table(frame,label,key):
    st.dataframe(frame,use_container_width=True,hide_index=True)
    st.download_button('Download '+label+' CSV',csv_bytes(frame),file_name=key+'.csv',mime='text/csv',key='download_'+key)

def empty(frame):
    if frame.empty:
        st.info('No observations match these filters. Choose a broader selection; missing activity is not zero.')
        return True
    return False

def context(text): st.caption('Active scope: '+text)
