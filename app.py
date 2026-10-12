import logging
import streamlit as st
from dashboard.data_contracts import DataError
from dashboard.navigation import navigation
from dashboard.theme import header

def main():
    st.set_page_config(page_title='PharmaLens · Prescribing Intelligence',layout='wide',initial_sidebar_state='collapsed')
    try:
        header(); page=navigation(); page.run()
        st.divider()
        st.caption('Independent educational portfolio · NHSBSA monthly PCA · Fixed history Jan 2023–Dec 2025. NIC is ingredient cost; items are not patients.')
    except (DataError,ValueError,OSError) as exc:
        logging.exception('Dashboard cannot render requested view')
        st.error(str(exc) if isinstance(exc,DataError) else 'This view could not be calculated. Check the selected inputs or restore validated runtime data.')
        st.info('No replacement or fabricated observations were used.')

if __name__=='__main__': main()
