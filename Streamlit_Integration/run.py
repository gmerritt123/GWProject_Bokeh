import streamlit as st
from mycomponent import mycomponent
value = mycomponent(my_input_value="hello there")
st.write("Received", value)
st.slider('Streamlit Slider',0,4,1,1,key='streamlit_slider_key')