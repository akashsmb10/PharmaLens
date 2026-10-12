import streamlit as st
from .data_loader import read_doc

def explain(source,period,calculation,evidence='Verified descriptive finding',caveat='Observed extract; absent activity is unknown. Items are product occurrences, not unique patients.'):
    with st.expander('How was this calculated?'):
        st.write('Source: NHSBSA monthly PCA · '+source)
        st.write('Period: '+period)
        st.write('Calculation: '+calculation)
        st.write('Evidence: '+evidence)
        st.caption(caveat)

def methodology(names):
    with st.expander('Methodology and limitations'):
        name=st.selectbox('Methodology document',names,key='methodology_'+names[0])
        text=read_doc(name)
        if text is None: st.info('Methodology document is not included in this deployment.')
        else: st.markdown(text)
