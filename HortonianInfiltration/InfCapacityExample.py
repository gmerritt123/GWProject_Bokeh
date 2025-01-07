# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 16:00:51 2024

@author: Gaelen Merritt
"""
import os
os.chdir(r'C:\Repo\GWProject_Bokeh')

import Bokeh_Util
import pandas as pd
import numpy as np
from bokeh.plotting import figure, save, curdoc
from bokeh.models import CustomJS, HoverTool, ColumnDataSource, Slider, CustomJSTickFormatter, InlineStyleSheet, Div
from bokeh.themes import Theme
from bokeh.layouts import column

thm = Theme(filename='Bokeh_Styles.yaml') #read yaml file for some styling already hooked up

#alternatively write css to target specific elements and apply as inline stylesheet to widgets
sl_css =   '''div.bk-slider-title{
                font-family: arial;
                font-weight: bold;
                font-size: 14pt;
                color: #17648D;
                '''
sl_iss = InlineStyleSheet(css=sl_css)

#create figure
f = figure(height=600,width=600
           ,title='Infiltration Capacity'
            ,x_range=[0,86400]
           )

#instructions dataframe for time units scale
ins_df = pd.DataFrame(data={'minRange':[0,300,60*120,60*60*24*2,60*60*24*365]
                           ,'unitName':['Seconds','Minutes','Hours','Days','Years']
                           ,'scaleFactor':[1,60,60*60,60*60*24,60*60*24*365]})

Bokeh_Util.setDynamicUnitScale(fig=f,ins_df=ins_df,ranges='x')
sc_cb = f.x_range.js_property_callbacks['change:start'][0] #find the callback this creates (need to trigger manually)

f.yaxis[0].axis_label = 'Rate (cm/hr)'

#create a datasource, which will get updated when user moves sliders
src = ColumnDataSource(data={'t':np.linspace(1,86400,1000) #time
                             ,'I':np.zeros(1000) #infiltration capacity
                             ,'P':np.zeros(1000) #precipitation rate
                             ,'R':np.zeros(1000) #holds the bottom of runoff area
                             ,'Ir':np.zeros(1000) #holds infiltration rate
                             })

#using src as the underlying source, add 3 renderers that run off different columns in src
#area glyph to show precipitation (as area bound by P and 0)
prec_rend = f.varea(x='t',y1='P',y2=0,fill_alpha=0.5,source=src,legend_label='Precipitation') 
#area glyph to show runoff (as area between precip and infiltrative capacity)
ro_rend = f.varea(x='t',y1='R',y2='I',fill_alpha=0.5,fill_color='red',source=src, legend_label='Runoff')
#line glyph to show infiltrative capacity
infcap_rend = f.line(x='t',y='I',source=src,legend_label='Infiltration Capacity',line_width=4)
#line glyph to show infiltration rate
inf_rend = f.line(x='t',y='Ir',source=src,legend_label='Infiltration Rate',line_width=4,line_color='orange',line_dash='dashed')

#creates sliders for the adjustable parameters
slider_dict = {'P':Slider(value=0,start=0,end=20,step=0.01,title='Precipitation Rate (cm/hr)')
               ,'Fc':Slider(value=0,start=0,end=10,step=0.01,title='Equilibrium Infiltration Capacity $$ f_c $$ (cm/hr)')
               ,'F_ini':Slider(value=0,start=0,end=20,step=0.01,title='Initial Infiltration Capacity $$ f_0 $$ (cm/hr)')
               ,'K':Slider(value=np.log10(1e-5)
                           ,start=-5, end=-3
                           , step=0.1
                           , format=CustomJSTickFormatter(code="return (10**tick).toExponential(2).toString()") #handling log scale slider
                           ,title='Decay Coefficient $$ k $$')
               }

#the javascript that executes when user moves a slider
cb = CustomJS(args=dict(slider_dict=slider_dict, src= src 
                        ) #args --> dict passing python things into javascript side
              ,code='''
              //define honrtonian infiltration function
              function hortonian_inf(fc,f0,k,t){
                  return fc + (f0-fc)*Math.exp(-1*k*t)
                  }
              //collect slider values
              var fc = slider_dict['Fc'].value
              var f_ini = slider_dict['F_ini'].value
              var k = 10**slider_dict['K'].value
              var p = slider_dict['P'].value
              //populate infiltration rate by mapping time array to hortonian infiltration function
              var inf_a = src.data['t'].map(x=>hortonian_inf(fc,f_ini,k,x))
              //populate precipitation as simply the slider value repeated by mapping time array to prec slider value
              var p_a = src.data['t'].map(x=>slider_dict['P'].value)
              //calculate the bounds of the runoff area, using an if statement (ternary operator for shorthand)
              //logic is IF prec > infiltrative capacity, set to prec, otherwise set to infiltrative capacity
              var ro_a = inf_a.map((x,i) => p > x ? p : x)
              //calculate infiltration rate using similar logic
              var infr_a = inf_a.map((x,i) => x < p ? x : p)
              //assign these arrays to the src
              src.data['I'] = inf_a
              src.data['P'] = p_a
              src.data['R'] = ro_a
              src.data['Ir'] = infr_a
              src.change.emit()
              '''
              )

#hook up the above js code to execute whenever a slider value changes, and also assign stylesheet while we're looping through
for v in slider_dict.values():
    v.stylesheets=[sl_iss]
    v.js_on_change('value',cb)
    v.width = f.width
    v.js_on_change('value',sc_cb) #trigger dynamic scale range update manually here
    


# d = Div(text='''
# <head>
# <style>
#   h1.title   {color: #17648D;
#               font-family: arial;
#               font-size: 14pt}
#   p.text    {font-family: arial;
#              font-size: 14pt}
#   p.equation    {font-family: arial;
#              font-size: 16pt}
#   ul.bullets {font-family: arial;
#               font-size: 14pt}
#  </style>
# <p class="text">Based on Thomas Reimann's <a href = "https://github.com/gw-inux/Jupyter-Notebooks/tree/main/02_Basic_hydrology">Jupyter Notebook</a>, this application explores soil infiltration rate as a function of time, infiltration capacity and precipitation rate, using <a href="https://acsess.onlinelibrary.wiley.com/doi/10.2136/sssaj1941.036159950005000C0075x">Horton's 1940</a> soil infiltration model:</p>
# <br>
# <p class="equation">$$ f_p = f_c + (f_0 - f_c) e^{-kt}$$</p>
# <br>
# <p class="text">with:</p>
# <ul class="bullets">
# <li>$$ f_p $$ = infiltration rate (cm/hr)</li>
# <li>$$ f_c $$ = equilibrium infiltration capacity (cm/hr)</li>
# <li>$$ f_0 $$ = initial infiltration capacity (cm/hr)</li>
# <li>$$ k $$ = infiltration capacity decrease coefficient (1/hr)</li>
# <li>$$ t $$ = time (hr)</li>
# </ul>
# </head>
#         '''
#         ,width=600)

# curdoc().theme = thm #assigns theme
#builds a layout
lo = column(list(slider_dict.values())+[f])

Bokeh_Util.save_html_wJSResources(bk_obj=lo
                                  , fname = r'HortonianInfiltration\InfiltrationCapacity.html'
                                  , resources_list_dict = {'sources':['https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.0/d3.min.js'],'scripts':[]}
                                  , html_title='Hortonian Infiltration Capacity'
                                  , theme=thm)

#saves to html
# save(lo,r'C:\Projects\GWP\InfCap.html',title='Hortonian Infiltration')



