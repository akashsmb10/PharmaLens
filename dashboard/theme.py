import streamlit as st
from .data_loader import ROOT,manifest

COLORS=['#176B87','#BD6B26','#4A578F','#297657','#994B6B','#6A7687','#8C651B']

def header():
    m=manifest()
    st.title('PharmaLens')
    st.caption('Pharmaceutical Prescribing Intelligence · Atorvastatin | England | NHSBSA | 2023–2025')
    st.caption('Portfolio application. Independent of NHS and Axtria; no endorsement implied.')
    style=ROOT/'dashboard/assets/styles.css'
    if style.is_file(): st.markdown('<style>'+style.read_text()+'</style>',unsafe_allow_html=True)
    st.sidebar.caption('Historical coverage: '+m['historical_start'][:7]+' to '+m['historical_end'][:7])
    st.sidebar.caption('Validated dataset: '+m['data_version'][:12])
    st.sidebar.caption('Application version: '+m['app_version'])
    st.sidebar.link_button('NHSBSA source and scope','https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data')
