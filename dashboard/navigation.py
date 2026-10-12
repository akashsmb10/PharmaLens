import streamlit as st
import importlib

PAGES=[('executive','Executive Overview'),('regional','Regional Intelligence'),('presentations','Presentation Intelligence'),
       ('forecasting','Forecasting & Model Evaluation'),('decision_intelligence','Decision Intelligence'),('scenario_simulator','Scenario Simulator')]

def navigation():
    pages=[st.Page(importlib.import_module('dashboard.pages.'+name).render,
                   title=title,url_path=name,default=i==0)
           for i,(name,title) in enumerate(PAGES)]
    return st.navigation(pages)
