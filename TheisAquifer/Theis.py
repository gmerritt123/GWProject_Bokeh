# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 11:23:09 2024

@author: Gaelen
"""
import os
os.chdir(r'C:\Repo\GWProject_Bokeh')
import Bokeh_Util
import sys

import numpy as np
from bokeh.plotting import figure, save, curdoc
from bokeh.models import CustomJS, HoverTool, ColumnDataSource, Slider, CustomJSTickFormatter, InlineStyleSheet, Div, Range1d
from bokeh.models import VeeHead, Arrow, Label, PointDrawTool, AnnularWedge, ColorBar, Annulus
from bokeh.transform import linear_cmap
from bokeh.palettes import Turbo256
from bokeh.themes import Theme
from bokeh.layouts import column, row
import pandas as pd

#style/theming loading
thm = Theme(filename=r'Bokeh_Styles.yaml') #read yaml file for some styling already hooked up
with open('Bokeh_Styles.css','r') as f:
    css = f.read()
sl_style = InlineStyleSheet(css=css)

#slider layout
slider_dict = {
    'Q': Slider(title='Pumping rate (m³/s)', value=0, start=0, end=0.2, step = 0.001
                       ,format='0.000'
                       )
    ,'T':Slider(title='Aquifer Transmissivity (m²/s)',value = -2, start = -7, end = 0, step = 0.1
                        ,format=CustomJSTickFormatter(code="return (10**tick).toExponential(2).toString()") #handling log scale slider)
                        )
    ,'S':Slider(title='Storativity',value = -4, start = -7, end = 0, step = 0.1
                        ,format=CustomJSTickFormatter(code="return (10**tick).toExponential(2).toString()") #handling log scale slider)
                        )
    ,'Time':Slider(title='Time (s)',value = 1, start = 1, end = 7, step = 0.1
                        ,format=CustomJSTickFormatter(code="return (10**tick).toExponential(2).toString()") #handling log scale slider)
                        )
    }

#three figures
#1) plan view with well @0,0

pv = figure(height=600,width=800
           ,title='Plan View'
            # ,match_aspect=True
            # ,aspect_scale = 1
           )

#well renderer
wr = pv.scatter(x=0,y=0,size=10,legend_label='Pumping Well')
pv.xaxis[0].axis_label = 'x (m)'
pv.yaxis[0].axis_label = 'y (m)'

#drawdown contours
hr_src = ColumnDataSource(data={'r':[],'dd':[],'ir':[]})

dd_cmap = linear_cmap(field_name='dd',palette=Turbo256,low=None,high=None)
hr = pv.circle(x=0,y=0,radius='r'
                ,line_color=dd_cmap
                ,line_alpha=0.3
                ,fill_alpha=0.0
                ,source=hr_src
                )


aw_glyph = Annulus(x=0,y=0,inner_radius = 'ir', outer_radius='r'
                       ,fill_color=dd_cmap
                       ,line_alpha=0
                       ,fill_alpha=0.3
                       )
aw_r = pv.add_glyph(hr_src,aw_glyph)

color_bar = ColorBar(color_mapper=dd_cmap.transform,title='Drawdown (m)')
pv.add_layout(color_bar,'right')


#2) drawdown vs radius
ddr = figure(height=400,width=400
             ,title='Drawdown VS. Distance'
             )
ddr.yaxis[0].axis_label='Drawdown (m)'
ddr.y_range.flipped = True

ddr.xaxis[0].axis_label='Distance From Well (m)'

ddr_src = ColumnDataSource(data={'x':[],'dd':[]})
ddr_r = ddr.line(x='x',y='dd',source=ddr_src)


#3) observation point dd vs time
#pv obs point
pt_rel = pv.scatter(x=[],y=[],size=10,marker='*',legend_label='Observation Point')
pt_d = PointDrawTool(renderers=[pt_rel], num_objects=1)
pv.add_tools(pt_d)

#add obs point to drawdown vs distance
obs_ddr = ddr.scatter(x='r',y='dd',marker='*',size=10
                      # ,legend_label='Observation Point'
                      ,source=pt_rel.data_source)


ddt = figure(height=400,width=400
             ,title='Drawdown VS. Time\n@Observation Point'
             )
ddt.yaxis[0].axis_label='Drawdown (m)'
ddt.y_range.flipped = True

ddt.xaxis[0].axis_label='Time (s)'

ddt_src = ColumnDataSource(data={'t':[],'dd':[]})
ddt_r = ddt.line(x='t',y='dd',source=ddt_src)

cb = CustomJS.from_file(path=r'TheisAquifer/cb.mjs', hr_src=hr_src,ddr_src=ddr_src
                        ,obs_src = pt_rel.data_source, ddt_src=ddt_src,
                        sl_dict=slider_dict)

#execute this callback when slider value changes
for sl in slider_dict.values():
    sl.js_on_change('value',cb)
    sl.stylesheets = [sl_style]
    sl.width=pv.width
pv.js_on_event('tap',cb)
pv.toolbar.active_tap = pt_d



#range bins on plan view, one off implementation for now.
pv.x_range = Range1d(start=-250,end=250)
pv.y_range = Range1d(start=-250,end=250)

rng_cb = CustomJS(args=dict(src=hr_src, pv = pv
                            ,sb=[250,500,1500]
                            ,xr = pv.x_range, yr=pv.y_range)
                  ,code='''
                  //only one data source to follow...
                  var mr = d3.max(src.data['r'])
                  
                  var ar = pv.inner_height/pv.inner_width
                  //where ar is height/width, and v is value
                  function applyRange(xr,yr,ar,v){
                      if (ar<1){
                              yr.start = -v
                              yr.end = v
                              xr.start = -v/ar
                              xr.end = v/ar
                              }
                      else {
                          xr.start = -v
                          xr.end = v
                          yr.start = -v*ar
                          yr.end = v*ar
                          }
                      }
                  
                for (var i = 0; i < sb.length; i++){
                          if (mr < sb[i]){
                                applyRange(xr,yr,ar,sb[i])
                                break
                                }
                        }
                if (i == sb.length){
                        applyRange(xr,yr,ar,mr)
                        }
                  ''')
hr_src.js_on_change('data',rng_cb)                  


#adding dynamic axis scales
# time
t_ins_df = pd.DataFrame(data={'minRange':[0,300,60*120,60*60*24*2,60*60*24*365]
                                    ,'unitName':['Time (seconds)','Time (minutes)','Time (hours)','Time (days)','Time (years)']
                                    ,'scaleFactor':[1,60,60*60,60*60*24,60*60*24*365]})
Bokeh_Util.setDynamicUnitScale(fig=ddt,ins_df=t_ins_df,ranges='x')
# distance
pv_ins_df = pd.DataFrame(data={'minRange':[0,3000],'unitName':['Meters','Kilometers'],'scaleFactor':[1,1000]})
Bokeh_Util.setDynamicUnitScale(fig=pv,ins_df=pv_ins_df,ranges='both')


d_ins_df = pd.DataFrame(data={'minRange':[0,3000],'unitName':['Distance From Well (m)','Distance From Well (km)'],'scaleFactor':[1,1000]})
Bokeh_Util.setDynamicUnitScale(fig=ddr,ins_df=d_ins_df,ranges='y')


#layout
lo = column([sl for sl in slider_dict.values()]+[pv,row([ddr,ddt])]
            # ,sizing_mode = 'stretch_both'
            )


#read in bokeh_util.js
with open(r'Bokeh_Util.js','r') as jsFile:
    bku_js = jsFile.read() 

Bokeh_Util.save_html_wJSResources(bk_obj=lo
                                  ,fname=r'TheisAquifer\Theis.html'
                                  ,resources_list_dict={'sources':['http://d3js.org/d3.v6.js'],'scripts':[bku_js]}
                                  ,html_title='Theis Drawdown',theme=thm
    )
# save(lo,wdir+r'\\Theis_Testing.html',title='Theis Drawdown')

