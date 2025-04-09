# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 14:33:45 2023

@author: Gaelen
"""

import pandas as pd
import numpy as np

import sys
sys.path.append(r'C:\Repo\GWProject_Bokeh')
import Bokeh_Util
import os
os.chdir(r'C:\Repo\GWProject_Bokeh\EquivK')

from bokeh.models import ColumnDataSource, CustomJS, NumericInput, Select, LogColorMapper, CustomJSTickFormatter, Arrow, NormalHead, Label, Div, HoverTool
from bokeh.transform import log_cmap, transform
from bokeh.plotting import figure, show
from bokeh.palettes import Turbo256
from bokeh.layouts import column, row

theme_dict = Bokeh_Util.getTheme('Aqua_Base')
ni = NumericInput(title='Number of Materials',low=1)
src = ColumnDataSource(data={'mat':[],'x':[],'w':[],'k':[]})
perpow = Arrow(x_start=-1,x_end=-1,y_start=0,y_end=0,start=None,end=NormalHead(size=25),visible=False)
perp_lbl = Label(x=-1,y=0,text="$$K_perp$$",angle=np.pi/2
                 ,x_offset= -0.1,y_offset=-20,visible=False)
parrow = Arrow(x_start=-1,x_end=1,y_start=-0.25,y_end=-0.25,start=None,end=NormalHead(size=25),visible=False)
par_lbl = Label(x=-0.9,y=-0.65,text=''
                 ,x_offset= 0,y_offset=0,visible=False)

fig = figure(x_range=[-1.5,1.5],y_range=[-1,4],height=800,width=400)
fig.yaxis[0].axis_label='Thickness (m)'
fig.xaxis[0].visible=False

ft = CustomJSTickFormatter(code="return 'Material x K (m/s): '+ (10**tick).toExponential(2).toString()")
mlc = column([])
mkc = column([])
nd_cb = CustomJS(args=dict(src=src,ni=ni,mlc=mlc,mkc=mkc,ft=ft,perpow=perpow,perp_lbl=perp_lbl,parrow=parrow,par_lbl=par_lbl,yr=fig.y_range)
                 ,code='''

                 var new_mlc = []
                 var new_mkc = []
                 var xc = 0
                 var upd_src = []
                 for (var i =0; i< ni.value; i++){
                         var mat = (i+1).toString()
                         //if more than current number of materials, need to make new widgets
                         if (i+1 > mlc.children.length){
                             new_mlc.push(new Bokeh.Widgets.NumericInput({width:150,value:1,low:0,title:'Layer '+mat+' Thickness (m)',mode:'float'}))
                             new_mlc[i].js_property_callbacks = ni.js_property_callbacks //assigns this callback to trigger on change of new widget
                             //clone the log tick formatter and splice in the Mat number
                             var nft = ft.clone()
                             var pre = nft.code.slice(0,17)
                             var suf = nft.code.slice(18,nft.code.length)
                             nft.code = pre+mat+suf                    
                             new_mkc.push(new Bokeh.Widgets.Slider({start:-12,end:0,step:0.1,value:-4,format:nft,height:50})) 
                             new_mkc[i].js_property_callbacks = ni.js_property_callbacks
                             }
                         else {
                             new_mlc.push(mlc.children[i])
                             new_mkc.push(mkc.children[i])
                             }
                         var r = {'w':new_mlc[i].value,'x':xc+new_mlc[i].value/2,'k':10**new_mkc[i].value,'mat':i+1}
                         xc = xc+new_mlc[i].value
                         upd_src.push(r)
                         }
                 mlc.children = new_mlc
                 mkc.children = new_mkc
                 var am = d3.sum(upd_src,d=>d.w*d.k)/d3.sum(upd_src,d=>d.w)
                 var hm = d3.sum(upd_src,d=>d.w)/d3.sum(upd_src,d=>d.w/d.k)
                 //update stuff
                 yr.end = xc*1.1
                 yr.start = 0-xc*0.15
                 perpow.y_end=xc
                 var perp_pre = '$$Equiv. K_{perpendicular} = '
                 var perp_v = hm.toExponential(2).toString()+'$$'
                 perp_lbl.text = perp_pre+perp_v                 
                 perp_lbl.y = xc/3                 
                 par_lbl.text = '$$Equiv. K_{parallel} = '+ am.toExponential(2).toString()+'$$'
                 par_lbl.y = yr.start
                 parrow.y_start = 0-xc*0.05
                 parrow.y_end = 0-xc*(0.05)
                 src.data = objarray_to_cds(upd_src)
                 perpow.visible = true
                 parrow.visible=true
                 perp_lbl.visible=true
                 par_lbl.visible=true
                 ''')
ni.js_on_change('value',nd_cb)


cmap = LogColorMapper(palette=Turbo256,low=1e-12,high=1)

r = fig.rect(x=0,y='x',width=1,height='w',source=src,fill_color=transform(field_name='k',transform=cmap),line_color='black')
fig.add_layout(perpow)
fig.add_layout(perp_lbl)
fig.add_layout(parrow)
fig.add_layout(par_lbl)

hvr = HoverTool(renderers=[r]
                ,tooltips = [('Layer','@mat')
                             ,('K (m/s)', '@k')
                             ,('Thickness (m)','@w')]
                ,attachment='right'
                             )
fig.add_tools(hvr)


title = Div(text='Equivalent Hydraulic Conductivity in a Layered System',stylesheets=[theme_dict['DivTitle']])
hdr = Div(text='''Calculate the equivalent hydraulic conductivity both parallel and perpendicular to an n-layered system.
          <br /><br /> Enter the number of layers (and hit enter) to get started.
          <br /><br />For more background, see <a href="https://books.gw-project.org/hydrogeologic-properties-of-earth-materials-and-principles-of-groundwater-flow/chapter/equation-derivation-for-equivalent-k-and-a-4-layer-application/">Hydrogeologic Properties of Earth Materials and Principles of Groundwater Flow (Woessner & Poeter 2020) </a>
          <br />''')

co = column([ni,row([mlc,mkc])]) 
lo = column([title,hdr,row([co,fig])])
#save to html file
with open(r'C:\Repo\GWProject_Bokeh\Bokeh_Util.js') as f:
    bk_util = f.read()


Bokeh_Util.save_html_wJSResources(bk_obj=lo, fname=r'EquivK.html'
                                  ,resources_list_dict={'sources':[
                                       'https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.0/d3.min.js'
                                      ]
                                                         ,'scripts':[
                                                             bk_util
                                                             ]}
                                  ,html_title='Equivalent K'
                                  ,theme=theme_dict['yaml'])