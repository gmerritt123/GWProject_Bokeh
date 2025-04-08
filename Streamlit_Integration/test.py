# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 15:04:13 2025

@author: Gaelen
"""

from bokeh.plotting import figure
from bokeh.models import CustomJS, ColumnDataSource, Slider
from bokeh.layouts import column
import streamlit as st
from streamlit_bokeh import streamlit_bokeh

src = ColumnDataSource(dict(x=[1,2,3],y=[1,2,3]))

f = figure(title="Testing",
                           x_axis_label="x",
                           y_axis_label="y")
f.line(x='x', y='y', legend_label="Trend", line_width=2,source=src)

bk_sl = Slider(start=0,end=4,step=1,value=1,title='Bokeh Slider')

cb = CustomJS(args=dict(src=src,bk_sl=bk_sl)
              ,code='''
              src.data['y'] = src.data['x'].map(x=>x**bk_sl.value)
              src.change.emit()
              ''')
bk_sl.js_on_change('value',cb)            


def st_cb():
    sv = st.session_state.streamlit_slider_key
    bk_sl.value=sv


st_sl = st.slider('Streamlit Slider',0,4,1,1,key='streamlit_slider_key'
                  ,on_change=st_cb)


streamlit_bokeh(column(f,bk_sl), use_container_width=True
                ,theme="streamlit", key="Application"
                
                )


    

