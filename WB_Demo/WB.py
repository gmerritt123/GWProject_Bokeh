# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 11:09:01 2025

@author: Gaelen
"""


import pandas as pd
import numpy as np

import sys

sys.path.append(r'C:\Repo\GWProject_Bokeh')
import Bokeh_Util 

from bokeh.models import CustomJSTickFormatter, DataRange1d, Range1d, LinearAxis
from bokeh.plotting import figure, show, save
from bokeh.layouts import column, row
from bokeh.palettes import Colorblind
from bokeh.models import ColumnDataSource, LinearColorMapper, LinearAxis, CustomJS, Slider, ColorBar
from bokeh.models import HoverTool, GroupFilter,CDSView, Band, CustomJSTransform, DateRangeSlider
from bokeh.models import CustomJSTickFormatter
from bokeh.models import Div, InlineStyleSheet, Tooltip, HelpButton
from bokeh.models.dom import HTML
from bokeh.io import curdoc
import os
os.chdir(r'C:\Repo\GWProject_Bokeh\WB_Demo')

df = pd.read_csv('Data.csv')
df['date'] = pd.to_datetime(df['date'])
df['AET'] = 0
df['Shallow Groundwater'] = 0
df['V'] = 0
df['Depth'] = 0
#Climate plot
cdf = pd.read_csv('ClimateData.csv').rename(columns={'PET':'cPET'})
cdf['date'] = pd.to_datetime(cdf['date'])
df= df.merge(cdf,how='inner',on='date')

#%% dummy depth-volume relationship and surface-area volume relationship
import matplotlib.pyplot as plt
fig,ax = plt.subplots()
v = np.arange(0,5000,5)
d = 0.1*v**0.4
sa = v*1000/d
ax.plot(v,d)
ax.set_xlabel('Volume (ML)')
ax.set_ylabel('Mean Depth (m)')
fig,ax = plt.subplots()
ax.plot(v,sa/10000)
ax.set_xlabel('Volume (ML)')
ax.set_ylabel('Surface Area (Ha)')
stg_df = pd.DataFrame(data={'Volume':v,'Depth':d,'Surface Area':sa}).fillna(0)


src = ColumnDataSource(data = df)
stg_src = ColumnDataSource(stg_df)

title_div = Div(text='Reservoir Water Balance',stylesheets=[Bokeh_Util.getTheme('Aqua_Base')['DivTitle']])

with open(r'DescDiv.txt') as f:
    desc_str = f.read()

desc_div = Div(text=desc_str)

#main Water Balance Figure Diagram
fig = figure(height=500,width=1300,x_axis_type='datetime'
             ,y_range=[-100,100],title='Simulated Reservoir Water Balance')
fig.y_range.bounds=[-100,100]
fig.yaxis[0].axis_label = 'Outflow (-) / Inflow (+) Rate (ML/d)'
# fig.yaxis[0].axis_label = 'Outflow (ML/d)   |    Inflow (ML/d)'
# from bokeh.models import CustomJSTickFormatter
# tck_fmt = CustomJSTickFormatter(code='''
#                                 return tick > 0 ? tick : tick*-1
#                                 ''')
# fig.yaxis[0].formatter = tck_fmt

in_rs = fig.vbar_stack(stackers=['Shallow Groundwater','Direct Precip','Runoff','Creek Inflow'],x='date'
                     ,color=Colorblind[6][0:4]
                     ,legend_label = ['Groundwater Inflow Rate (Simulated)','Direct Precipitation Inflow Rate (Observed)'
                                      ,'Runoff Inflow Rate (Simulated)','Creek Inflow Rate (Observed)']
                     ,source=src,width=pd.to_timedelta('1D')
                     )

out_rs = fig.vbar_stack(stackers=['AET','Dam Outflow','Seepage'],x='date'
                     ,color=Colorblind[7][4:7]
                     ,legend_label = ['Evaporation Outflow Rate (Simulated)','Dam Outflow Rate (Observed)','Groundwater Outflow Rate (Simulated)']
                     ,source=src,width=pd.to_timedelta('1D')
                     )

fig.x_range.range_padding = 0.01
fig.xaxis[0].axis_label='Year'


fig.extra_y_ranges['d'] = Range1d(0,4
                                   ,bounds=(0,4)
                                  )
ax2 = LinearAxis(y_range_name='d',axis_label='Reservoir Depth (m)')
fig.add_layout(ax2,'right')
fig.line(x='date',y='Depth'
         ,line_color='blue',line_width=3,legend_label = 'Simulated Reservoir Depth (m)',source=src,y_range_name='d')
fig.line(x='date',y='Obs'
         ,line_color='blue',line_width=3, line_dash='dotted'
         ,legend_label = 'Observed Reservoir Depth (m)',source=src,y_range_name='d')
fig.extra_y_ranges['v'] = Range1d(0,5000
                                   # ,bounds=(-5000,5000)
                                  )
ax2 = LinearAxis(y_range_name='v',axis_label='Reservoir Volume (ML)')
fig.add_layout(ax2,'right')
fig.line(x='date',y='V'
         ,line_color='black',line_width=3,legend_label = 'Simulated Reservoir Volume (ML)',source=src,y_range_name='v',visible=False)

leg = fig.legend[0]
leg.click_policy = 'hide'
fig.add_layout(leg,'right')

# csrc = ColumnDataSource(data=cdf)

cfig = figure(height=600,width=1600,x_axis_type='datetime'
             ,y_range=[0,25],title='Climate',x_range=fig.x_range)

cfig.extra_y_ranges['sp'] = Range1d(0,150)
ax2 = LinearAxis(y_range_name='sp',axis_label='Snowpack (mm)')
cfig.add_layout(ax2,'right')

sr = cfig.varea(x='date',y1='snowpack',y2=0,fill_color='grey',legend_label='Snowpack (mm)'
                ,source=src,fill_alpha=0.25,y_range_name='sp')
sm = cfig.vbar_stack(['snowmelt','rain'],x='date',width=pd.to_timedelta('1D')
            ,fill_color=['cyan','blue'],fill_alpha=0.5,source=src,legend_label=['Snowmelt (mm)','Rain (mm)'],line_alpha=0)
petr = cfig.line(x='date',y='cPET',line_color='salmon'
                 ,legend_label = 'Potential Evapotranspiration (mm)',line_width=3,source=src)


pw = 65
dsl = DateRangeSlider(start=pd.to_datetime('Jan 1, 2019')
                      ,end=pd.to_datetime('September 29, 2023')
                      # ,step=pd.to_timedelta('1D')
                      ,value=[pd.to_datetime('Jan 1, 2019'),pd.to_datetime('September 29, 2023')]
                      ,width=1600-int(pw*2.8))


bd = Div(width=pw,text='')


ksl = Slider(value=-8,start=-9,end=-6,step=0.1,width=fig.width-200,title='Groundwater Outflow Coefficient (m/s)'
                          , format=CustomJSTickFormatter(code="return (10**tick).toExponential(2).toString()") 
                          )
kdesc = Tooltip(content=HTML("The volume of groundwater outflow leaving a reservoir is a function of reservoir depth, reservoir surface area, and material permeability. This slider controls that permeability."
            ),position='right')
khelp = HelpButton(tooltip=kdesc)

bsl = Slider(value=0.5,start=0,end=1.0,step=0.01,width=fig.width-200,title='Fraction of Catchment Recharge routed to Reservoir')
bdesc = Tooltip(content=HTML("Some fraction of recharge within the reservoir's catchment area will reach the reservoir as baseflow/interflow (the rest will travel deeper to more regional flow features). This slider controls that fraction."
            ),position='right')
bhelp = HelpButton(tooltip=bdesc)


d3_divTitle = Div(height=25,width=1000,text='Simulated Reservoir Water Balance: 2019-2023',stylesheets=[Bokeh_Util.getTheme('Aqua_Base')['DivTitle']])
d3_div = Div(text='',width=1000,height=500)

cb = CustomJS(args=dict(src=src,dsl=dsl,d3_div=d3_div
                        ,pl =Colorblind[7]
                        ,ksl = ksl, bsl = bsl, stg_src= stg_src)
              ,code='''
              var oa = cds_to_objarray(src.data)
              
              var kseep = 10**ksl.value
              var bff = bsl.value
              var mvol = d3.max(stg_src.data['Volume'])
              var mdep = d3.max(stg_src.data['Depth']) 
              var i = 0
              for (var i = 0; i<oa.length; i++){
                      var v = oa[i]                        
                      var dV = v['Runoff']+v['Baseflow']*bff+v['Direct Precip']+v['Creek Inflow']
                      //volume pre aer
                      if (i ==0){
                              var vps = dV+1000
                              }
                      else {
                          var vps = clamp(oa[i-1]['V']+dV,0,mvol)
                          }
                      //get area
                      var a = interp(vps,stg_src.data['Volume'],stg_src.data['Surface Area'])
                      var aet = v['cPET']/1000*a/1000 //open water surface area = AET (mm-->m-->ML)
                      //volume post aet
                      vps = clamp(vps-aet,0,mvol)
                      //get depth and area post aet
                      var d = interp(vps,stg_src.data['Volume'],stg_src.data['Depth'])
                      a = interp(vps,stg_src.data['Volume'],stg_src.data['Surface Area'])
                      var spg = d*kseep*60*60*24
                      var vspg = spg * a /1000 //volume seepage
                      //volume and sa post seepage
                      vps = clamp(vps-vspg,0,mvol)
                      a = interp(vps,stg_src.data['Volume'],stg_src.data['Surface Area'])
                      //depth post seepage
                      var d = interp(vps,stg_src.data['Volume'],stg_src.data['Depth'])
                      v['AET'] = -aet
                      v['Seepage'] = -vspg
                      v['V'] = vps+v['Dam Outflow'] //all catchment inflows and dam outflow
                      v['Depth'] = d
                      v['Shallow Groundwater'] = bff*v['Baseflow']
                      v['Surface Area'] = a
                      }

              src.data = objarray_to_cds(oa)
              
              var oa = cds_to_objarray(src.data).filter(x=>(x.date>dsl.value[0])&&(x.date<dsl.value[1]))
              //sankey
              var ru = d3.rollup(oa,
                                 d=>{
                                     var result = {}
                                     for (var k of ['Shallow Groundwater', 'Runoff', 'Direct Precip', 'AET', 'Creek Inflow',
                                            'Dam Outflow','Seepage']){
                                                result[k] = d3.sum(d,v=>v[[k]])                                                
                                                }
                                     return result
                                                })
            var imbal = d3.sum(Object.values(ru))                                   
            console.log(ru)
            console.log(imbal)
            var link_data = [
                          {'source':'Direct Precip','target':'Reservoir','value':ru['Direct Precip']}
                          ,{'source':'Runoff','target':'Reservoir','value':ru['Runoff']}
                          ,{'source':'Creek Inflow','target':'Reservoir','value':ru['Creek Inflow']}
                          ,{'source':'Groundwater Inflow','target':'Reservoir','value':ru['Shallow Groundwater']}
                          ,{'source':'Reservoir','target':'AET','value':ru['AET']*-1}
                          ,{'source':'Reservoir','target':'Dam Outflow','value':ru['Dam Outflow']*-1}
                          ,{'source':'Reservoir','target':'Groundwater Outflow','value':ru['Seepage']*-1}
                        ]
            
            link_data.push({'source':'Reservoir','target':'Imbalance/Change In Storage','value':Math.abs(imbal)})
                    
                        
            var node_data = [{'name':'Direct Precip','Category':'Inflow'}
                             ,{'name':'Runoff','Category':'Inflow'}
                             ,{'name':'Creek Inflow','Category':'Inflow'}
                             ,{'name':'Groundwater Inflow','Category':'Inflow'}
                             ,{'name':'AET','Category':'Outflow'}
                             ,{'name':'Dam Outflow','Category':'Outflow'}
                             ,{'name':'Groundwater Outflow','Category':'Outflow'}
                             ,{'name':'Reservoir','Category':'Reservoir'}
                             ,{'name':'Imbalance/Change In Storage','Category':'Imbalance'}
                            ]
            
            const format = d3.format(",.0f");
            const width = d3_div.width
            const height = d3_div.height
             // Create a SVG container.
             const svg = d3.create("svg")
                 .attr("width", width)
                 .attr("height", height)
                 .attr("viewBox", [0-25, -25, width+50, height+50])
                 .attr("style", "max-width: 100%; height: auto; font: 10px arial;");
                 
               // Constructs and configures a Sankey generator.
           const sankey = d3.sankey()
               .nodeId(d => d.name)
               .nodeAlign(d3.sankeyLeft)
               .nodeWidth(25)
               .nodePadding(60)
               .extent([[1, 10], [width - 10, height - 50]]);
          
           const data = {'nodes':node_data,'links':link_data}
           // Applies it to the data. We make a copy of the nodes and links objects
           // so as to avoid mutating the original.
           const nds = data.nodes.map(d => Object.assign({}, d))
           const lnks = data.links.map(d => Object.assign({}, d))


           const {nodes, links} = sankey({
              nodes: nds,
               links: lnks
             });
           
           const color = d3.scaleOrdinal(d3.schemeCategory10)
           const cmap = {'Direct Precip':pl[1],'Runoff':pl[2],'Groundwater Inflow':pl[0], 'Creek Inflow':pl[3]
                         ,'AET':pl[4],'Dam Outflow':pl[5],'Reservoir':'#2ca02c','Groundwater Outflow':pl[6]
                         }
           if (imbal > 0){
                   cmap['Imbalance/Change In Storage'] = 'green'}
           else {
               cmap['Imbalance/Change In Storage']='red'
               }
           
           // Creates the rects that represent the nodes.
          const rect = svg.append("g")
              .attr("stroke", "#000")
            .selectAll()
            .data(nodes)
            .join("rect")
              .attr("x", d => d.x0)
              .attr("y", d => d.y0)
              .attr("height", d => d.y1 - d.y0)
              .attr("width", d => d.x1 - d.x0)
              .attr('fill',d=>cmap[d.name])
              
           // Adds a title on the nodes.
           rect.append("title")
               .text(d => {if (d.name == 'Imbalance/Change In Storage'){
                           return d.name+'\\n' + imbal.toFixed().toString() + ' ML'    
                           }
                   
                           else { return d.name+'\\n'+d.value.toFixed().toString()+' ML'}
                           }
                   )
               
           // Creates the paths that represent the links.
           const link = svg.append("g")
             .attr("fill", "none")
             .attr("stroke-opacity", 0.5)
           .selectAll()
           .data(links)
           .join("g")
             .style("mix-blend-mode", "multiply");
             
           link.append("path")
             .attr("d", d3.sankeyLinkHorizontal())
             .attr("stroke"
                 , (d) => {return d.target.name === 'Reservoir' ? cmap[d.source.name] : cmap[d.target.name]}
                 )
             .attr("stroke-width", d => Math.max(1, d.width));
           
           svg.append("g")
             .selectAll()
             .data(nodes)
             .join("text")
             .attr("x",d=> d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)                 
               .attr("y", d => (d.y1 + d.y0) / 2)
               .attr("dy", "-1.0em")
               .attr("text-anchor",d=> d.x0 < width / 2 ? "start" : "end")
               .attr('font-size','11pt')
               .text(d => d.name);
               
           svg.append("g")
             .selectAll()
             .data(nodes)
             .join("text")
             .attr("x",d=>d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
               .attr("y", d => (d.y1 + d.y0) / 2)
               .attr("dy", "0.4em")
               .attr("text-anchor",d=> d.x0 < width / 2 ? "start" : "end")                         
               .attr('font-size','11pt')
               .text(d => {
                           if (d.name == 'Reservoir'){                                  
                               return 'Inflows: '+format(d3.sum(d.targetLinks,v=>v.value)) +' ML'      
                               }
                           else if (d.name == 'Imbalance/Change In Storage'){                               
                               return imbal.toFixed().toString() + ' ML'
                               }
                           else {return format(d.value) +' ML'}
                           }
                   )
               
           svg.append("g")
             .selectAll()
             .data(nodes)
             .join("text")
             .attr("x",d=>d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
               .attr("y", d => (d.y1 + d.y0) / 2)
               .attr("dy", "1.9em")
               .attr("text-anchor",d=> d.x0 < width / 2 ? "start" : "end")                         
               .attr('font-size','11pt')
               .text(d => {
                           if (d.name == 'Reservoir'){
                                   return 'Outflows: '+format(d3.sum(d.sourceLinks,v=>v.value)-Math.abs(imbal)) +' ML'
                               }
                           else {return ''}
                           }
                   )
                                                
              d3_div.text = svg._groups[0][0].outerHTML                                  
              
              '''
              )
dsl.js_on_change('value',cb)
bsl.js_on_change('value',cb)
ksl.js_on_change('value',cb)


with open(r'C:\Repo\GWProject_Bokeh\Bokeh_Util.js') as f:
    d3_util = f.read()

Bokeh_Util.save_html_wJSResources(bk_obj=column([title_div,desc_div,
    # row([bd,dsl]),
                                                 row([bsl,bhelp]),row([ksl,khelp]),fig,d3_divTitle,d3_div])
                                  , fname='WB.html'
                                  , resources_list_dict={'sources':['https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.0/d3.min.js'
                                                                    ,'https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js']
                                                          ,'scripts':[d3_util]}
                                  ,html_title='Reservoir Water Balance'
                                  ,theme=Bokeh_Util.getTheme('Aqua_Base')['yaml'])
#%%

