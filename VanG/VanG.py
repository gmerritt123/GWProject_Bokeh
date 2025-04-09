# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 14:05:46 2021

@author: Gaelen
"""
import pandas as pd
import numpy as np

import sys
sys.path.append(r'C:\Repo\GWProject_Bokeh')
import Bokeh_Util
import os
os.chdir(r'C:\Repo\GWProject_Bokeh\VanG')


from bokeh.plotting import figure, save
from bokeh.layouts import layout,row,column
from bokeh.models import Line, CustomJS, Slider, RangeSlider, ColumnDataSource, CustomJSTickFormatter, HoverTool, Div, Select

theme_dict = Bokeh_Util.getTheme('Aqua_Base')


def thetaFunction(psi,pars):
  Se=(1+abs(psi*pars['alpha'])**pars['n'])**(-pars['m'])
  Se[psi>=0]=1.
  return pars['thetaR']+(pars['thetaS']-pars['thetaR'])*Se
  
def KFunction(psi,pars):
  Se=(1+abs(psi*pars['alpha'])**pars['n'])**(-pars['m'])
  Se[psi>=0]=1.
  return pars['Ks']*Se**pars['neta']*(1-(1-Se**(1/pars['m']))**pars['m'])**2

def KFunction_mod(psi,pars):
    theta = thetaFunction(psi,pars)
    return (theta/pars['thetaS'])**pars['delta']*pars['Ks']


def Sand():
  pars={}
  pars['name'] = 'Sand'
  pars['thetaR']=0.01
  pars['thetaS']=0.26
  pars['alpha']=3.24
  pars['n']=6.66
  pars['m']=1-1/pars['n']
  pars['Ks']=1e-4
  pars['neta']=0.5
  pars['delta'] = 2.5
  return pars

def Loam():
  pars={}
  pars['name'] = 'Loam'
  pars['thetaR']=0.05
  pars['thetaS']=0.37
  pars['alpha']=1.61
  pars['n']=2.6632
  pars['m']=1-1/pars['n']
  pars['Ks']=1e-6
  pars['neta']=0.5
  pars['delta'] = 4
  return pars

def Clay():
  pars={}
  pars['name'] = 'Clay'
  pars['thetaR']=0.16
  pars['thetaS']=0.47
  pars['alpha']=0.6
  pars['n']=1.8601
  pars['m']=1-1/pars['n']
  pars['Ks']=1e-8
  pars['neta']=0.5
  pars['delta'] = 7
  return pars
  

class VanGBokeh:
    '''class to handle vanG bokeh figure making'''
    def __init__(self,line_color,ini_pars=Sand(),fig_dict=None):
        self.ini_pars = ini_pars
        self.fig_dict = fig_dict
        self.genFigures(lc=line_color)
        self.slider_dict = self.genSliders()       
        self.slider_cb = self.genSliderCB()
        self.dd = self.genDropDown()

        print('generated!')
        
    def genFigures(self,lc):
        if self.fig_dict is None:
            th_p = figure(height=700,width=560,title='Suction Head ----> Water Content Relationship')
            th_p.yaxis.axis_label = 'Water Content'
            th_p.xaxis.axis_label = 'Suction Head (m)'
            k_th = figure(height=700,width=560,title='Water Content ----> K Relationship',y_axis_type='log')
            k_th.yaxis.axis_label = 'Effective K (m/s)'
            k_th.xaxis.axis_label = 'Water Content'
        else:
            print(self.fig_dict)
            th_p = self.fig_dict['Theta_P']
            k_th = self.fig_dict['K_Theta']
            
        psi = np.linspace(-10,0,1000)
        src = ColumnDataSource({'psi':psi
                                    ,'theta':thetaFunction(psi,self.ini_pars)
                                    ,'k':KFunction(psi,self.ini_pars)
                                    ,'km':KFunction_mod(psi,self.ini_pars)
                                    })
        
        th_p_glyph = Line(x='psi',y='theta',line_color=lc,line_width=3)
        th_p_rend = th_p.add_glyph(src,th_p_glyph)
        th_p_hvr = HoverTool(renderers=[th_p_rend],tooltips=[('Suction Head (m)','@psi'),('Water Content','@theta')]
                              ,formatters={'Suction Head (m)':'printf','Water Content':'printf'})
        th_p.add_tools(th_p_hvr)
        

        k_th_glyph = Line(x='theta',y='k',line_color=lc,line_width=3)
        k_th_rend = k_th.add_glyph(src,k_th_glyph)
        k_th_hvr = HoverTool(renderers=[k_th_rend],tooltips=[('Water Content','@theta'),('K (m/s)','@k')]
                              ,formatters={'K (m/s)':'printf','Water Content':'printf'})
        k_th.add_tools(k_th_hvr)
        
        k_th_glyph_m = Line(x='theta',y='km',line_color=lc,line_width=3,line_dash='dashed')
        k_th_rend_m = k_th.add_glyph(src,k_th_glyph_m)
        k_th_hvr_m = HoverTool(renderers=[k_th_rend_m],tooltips=[('VanG Modified',''),('Water Content','@theta'),('K (m/s)','@km')]
                              ,formatters={'K (m/s)':'printf','Water Content':'printf'})
        k_th.add_tools(k_th_hvr_m)
        self.src = src
        self.fig_dict = {'Theta_P':th_p,'K_Theta':k_th}
       
        
        
        
    def genSliders(self):
        ini_pars = self.ini_pars
        thetaSlider = RangeSlider(value=(ini_pars['thetaR'],ini_pars['thetaS']),start=.01,end=0.99,step = .01,title='Residual Water Content ---- > Saturated Water Content'
                                  ,width=560)
        alphaSlider = Slider(value=ini_pars['alpha'],start=.1,end=6,step=.01,title='Alpha (/m)'
                             ,width=thetaSlider.width
                             )
        nSlider = Slider(value=ini_pars['n'],start=1.01,end=8,step=.1,title='n',width=thetaSlider.width)
        kSlider = Slider(value=np.log10(ini_pars['Ks']),start=-10, end=0, step=0.1, format=CustomJSTickFormatter(code="return 'Ksat: '+ (10**tick).toExponential(2).toString()"),width=thetaSlider.width)
        lSlider = Slider(value=ini_pars['neta'],start=0.1,end=1,step=.1,title='l',width=thetaSlider.width)
        dSlider = Slider(value=ini_pars['delta'],start=0,end=10,step=.1,title='Delta (Modified Van G)',width=thetaSlider.width)
        return {'Theta':thetaSlider,'Alpha':alphaSlider,'N':nSlider,'K':kSlider,'L':lSlider,'Delta':dSlider}
    
    def genSliderCB(self):
        slider_cb = CustomJS(args=dict(slider_dict=self.slider_dict,src=self.src)
                    ,code='''
                    const tr = slider_dict['Theta'].value[0]
                    const ts = slider_dict['Theta'].value[1]
                    const a = slider_dict['Alpha'].value
                    const n = slider_dict['N'].value
                    const k = 10**slider_dict['K'].value
                    const l = slider_dict['L'].value
                    const d = slider_dict['Delta'].value
                    
                    const psi = src.data['psi']
                    
                    function thetaFunc(p,tr,ts,n){
                        if (p>=0){return ts}
                        else {
                            const m = 1-1/n
                            const Se = (1+Math.abs(p*a)**n)**-m
                            return tr+(ts-tr)*Se
                            }
                        }
                    
                    function kFunc(p,a,n,k,l){
                        if (p>=0){return k}
                        else {
                            const m = 1-1/n
                            const Se = (1+Math.abs(p*a)**n)**-m
                            return k*Se**l*(1-(1-Se**(1/m))**m)**2
                            }                            
                        }
                    
                    function kFunc_m(p,tr,ts,n,k,d){
                       if (p>=0){return k}
                        else {
                            const m = 1-1/n
                            const Se = (1+Math.abs(p*a)**n)**-m
                            const theta = tr+(ts-tr)*Se
                            return (theta/ts)**d*k
                            }
                        }
                    
                    var theta_arry = psi.map(function(x) {return thetaFunc(x,tr,ts,n)})
                    var k_arry = psi.map(function(x) {return kFunc(x,a,n,k,l)})
                    var k_arry_m = psi.map(function(x) {return kFunc_m(x,tr,ts,n,k,d)})
                    src.data['theta']= theta_arry
                    src.data['k'] = k_arry
                    src.data['km'] = k_arry_m
                    src.change.emit()
                    '''
                    )
        
        for sl in self.slider_dict.keys():
            self.slider_dict[sl].js_on_change('value',slider_cb)
        return slider_cb
        
    def genDropDown(self):
        dd = Select(title='Select Prebuilt Material Type',value=self.ini_pars['name'],options=['Sand','Loam','Clay'])
        dd.js_on_change('value',CustomJS(args=dict(slider_dict = {k:v for k,v in self.slider_dict.items()},
                                                    pardict = {'Sand':Sand(),'Loam':Loam(),'Clay':Clay()}
                                                    )
                                                ,code = '''
                                                
                                                const d = pardict[this.value]
                                                slider_dict['Theta'].value = [d['thetaR'],d['thetaS']]
                                                slider_dict['Alpha'].value = d['alpha']                                                
                                                slider_dict['N'].value = d['n']
                                                slider_dict['L'].value = d['neta']
                                                slider_dict['K'].value = Math.log10(d['Ks'])
                                                slider_dict['Delta'].value = d['delta']
                                                '''
                                                          ))
        return dd
        
        
par1 = Sand()
par2 = Clay()
vg = VanGBokeh(line_color='blue',ini_pars=par1)
vg2 = VanGBokeh(line_color='red',ini_pars=par2,fig_dict = vg.fig_dict)


title = Div(text="<b>Van Genuchten Parameters Tool</b>"
            , stylesheets=[theme_dict['DivTitle']]
            # ,width=1200,height=100
            )

subtitle = Div(text = '''Use the sliders to adjust <a href= 'https://www.ars.usda.gov/arsuserfiles/20360500/pdf_pubs/p0682.pdf'>Van Genuchten (1980)</a> parameters for two different materials
               OR select prebuilt materials based on <a href = 'https://www.researchgate.net/figure/Van-Genuchten-Parameters-Regular-and-Modified-for-Sand-Loam-Clay-and-the_tbl1_40120567'>Hilberts et al (2005)</a> from the drop down menus.'''
               ,width=2000)


mat1 = Div(text='<p style="font-size:12pt;color:blue;font-weight:bold">Material 1</p>'
           # , style={'font-size': '200%', 'color': 'blue'}
           # ,width=800,height=100
           )
mat2 = Div(text='<p style="font-size:12pt;color:red;font-weight:bold">Material 2</p>'
           )

lo = layout(row(column([title,subtitle])),
            row([vg.fig_dict['Theta_P'],vg.fig_dict['K_Theta']])
            ,row(column([row([mat1,vg.dd])]
                        +[vg.slider_dict[x] for x in vg.slider_dict.keys()])
                ,column([row([mat2,vg2.dd])]
                        +[vg2.slider_dict[x] for x in vg2.slider_dict.keys()]))  
            )




Bokeh_Util.save_html_wJSResources(bk_obj=lo, fname=r'VanG.html'
                                  ,resources_list_dict={'sources':[
                                       'https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.0/d3.min.js'
                                      ]
                                                         ,'scripts':[]}
                                  ,html_title='Van Genuchten Explorer'
                                  ,theme=theme_dict['yaml'])


        
        
        



