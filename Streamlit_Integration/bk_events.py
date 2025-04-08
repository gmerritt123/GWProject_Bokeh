# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 09:51:13 2025

@author: Gaelen
"""
import streamlit as st
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.plotting import figure
import pandas as pd
import numpy as np
from streamlit_bokeh3_events import streamlit_bokeh3_events

@st.cache_data
def data():
    df = pd.DataFrame({"x": np.random.rand(500), "y": np.random.rand(500), "size": np.random.rand(500) * 10})
    return df

df = data()
source = ColumnDataSource(df)

st.subheader("Select Points From Map")

plot = figure( tools="lasso_select,reset", width=500, height=500)
plot.circle(x="x", y="y", size="size", source=source, alpha=0.6)

source.selected.js_on_change(
    "indices",
    CustomJS(
        args=dict(source=source),
        code="""
        document.dispatchEvent(
            new CustomEvent("TestSelectEvent", {detail: {indices: cb_obj.indices}})
        )
    """,
    ),
)

event_result = streamlit_bokeh3_events(
    events="TestSelectEvent",
    bokeh_plot=plot,
    key="foo1",
    debounce_time=100,
    refresh_on_update=False
)

# some event was thrown
if event_result is not None:
    # TestSelectEvent was thrown
    if "TestSelectEvent" in event_result:
        st.subheader("Selected Points' Pandas Stat summary")
        indices = event_result["TestSelectEvent"].get("indices", [])
        st.table(df.iloc[indices].describe())

st.subheader("Raw Event Data")
st.write(event_result)
        
        
# from bokeh.plotting import figure
# from bokeh.models import CustomJS, ColumnDataSource, Slider
# from bokeh.layouts import column
# import streamlit as st
# from streamlit_bokeh import streamlit_bokeh
# from streamlit_bokeh3_events import streamlit_bokeh3_events

# src = ColumnDataSource(dict(x=[1,2,3],y=[1,2,3]))

# f = figure(title="Testing",
#                            x_axis_label="x",
#                            y_axis_label="y")
# f.line(x='x', y='y', legend_label="Trend", line_width=2,source=src)

# bk_sl = Slider(start=0,end=4,step=1,value=1,title='Bokeh Slider')

# cb = CustomJS(args=dict(src=src,bk_sl=bk_sl)
#               ,code='''
#               src.data['y'] = src.data['x'].map(x=>x**bk_sl.value)
#               src.change.emit()
#               ''')
# bk_sl.js_on_change('value',cb)            

# st_sl = st.slider('Streamlit Slider',0,4,1,1,key='streamlit_slider_key'
#                   ,on_change=st_cb)

# streamlit_bokeh(column(f,bk_sl), use_container_width=True
#                 ,theme="streamlit", key="Application"
                
#                 )
