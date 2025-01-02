from bokeh.plotting import figure, save
from bokeh.models import CustomJS, CustomJSTickFormatter, FixedTicker, Slider, Range1d, DataRange, DataRange1d
from bokeh.events import RangesUpdate
from bokeh.transform import linear_cmap
from bokeh.palettes import Turbo256
from bokeh.themes import Theme
from bokeh.models import NumericInput
from bokeh.layouts import column, row
from bokeh.embed import components
from bokeh.resources import Resources
from jinja2 import Template
import pandas as pd

def save_html_wJSResources(bk_obj,fname,resources_list_dict,html_title='Bokeh Plot',theme=None
    ,icon_url='https://aquainsight.sharepoint.com/sites/AquaInsight/_api/siteiconmanager/getsitelogo?type=%271%27&hash=637675014792340093'):
    '''function to save a bokeh figure/layout/widget but with additional JS resources imported at the top of the html
        resources_list_dict is a dict input of where to import additional JS libs/scripts so they can be utilized into CustomJS etc in bokeh work
        e.g. {'sources':['http://d3js.org/d3.v6.js'],'scripts':[var_storing_jsscript]}
        theme arg is to pass a yaml-based theme -->use getTheme() function to retrieve dictionary of custom themes, and pass the yaml key
        icon_url --> point to a url for an image for the icon url
        '''
    if theme is None:
        script, div = components(bk_obj)
        theme={'yaml':None,'css':''}
    else:
        script, div = components(bk_obj, theme=theme)
    print(icon_url)
    if icon_url is None:
        template = Template('''<!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>'''+html_title+'''</title>
                {{ resources }}
                {{ script }}
            </head>
            <body>
                <div>
                {{ div }}
                </div>
            </body>
        </html>
        ''')
    else:
        template = Template('''<!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <link rel="icon" href="'''+icon_url+'''">
                <title>'''+html_title+'''</title>
                {{ resources }}
                {{ script }}
            </head>
            <body>
                <div>
                {{ div }}
                </div>
            </body>
        </html>
        ''')

    
    resources = Resources().render()
    
    for r in resources_list_dict['sources']:
        resources = resources +'''\n<script type='text/javascript' src="'''+r+'''"></script>'''
    for r in resources_list_dict['scripts']:
        resources = resources +'''\n<script type='text/javascript'> '''+r+'''</script>'''  
    
    html = template.render(resources=resources,
                           script=script,
                           div=div)
    print('writing '+fname+'...')
    with open(fname, mode="w", encoding="utf-8") as f:
        f.write(html)

def setDynamicUnitScale(fig,ins_df,ranges='both'):
    '''function to set a dynamic unit scale on a figure. 
    ins_df is a dataframe containing 'minRange' (giving the minimum range required), 'unitName' (axis label)
    , and 'scaleFactor' (factor to divide the base units by at the particular threshold/interval)
    ranges = 'x','y' or 'both' to apply on x/y axis of plot
    example ins_df for time:
        
        ins_df = pd.DataFrame(data={'minRange':[0,300,60*120,60*60*24*2,60*60*24*365]
                                   ,'unitName':['Seconds','Minutes','Hours','Days','Years']
                                   ,'scaleFactor':[1,60,60*60,60*60*24,60*60*24*365]})
    
    '''
    if ranges == 'x':
        m = [{'range':fig.x_range,'ax':fig.xaxis[0]}]
        
    elif ranges == 'y':
        m = [{'range':fig.x_range,'ax':fig.xaxis[0]}]
    else:
        m = [{'range':fig.x_range,'ax':fig.xaxis[0]}
         ,{'range':fig.y_range,'ax':fig.yaxis[0]}]
        
    for r in m:
        r['tks'] = FixedTicker()
        r['ax'].ticker = r['tks']
        
              
    cb = CustomJS(args=dict(fmt_oa = ins_df.to_dict('records')
                                          ,m=m
                                          )
                                ,code='''
                                for (var ri = 0; ri < m.length; ri++){ 
                                        var xr = m[ri]['range'] 
                                        var d = xr.end - xr.start
                                        for (var i = 0; i < fmt_oa.length-1; i++){
                                                if (d>=fmt_oa[i]['minRange'] && d < fmt_oa[i+1]['minRange']){
                                                        var sel = fmt_oa[i]                                                    
                                                        break
                                                        }
                                                }
                                        if (i == fmt_oa.length-1){
                                                var sel = fmt_oa[i]                                            
                                                }
                                        var tks = d3.ticks(xr.start/sel['scaleFactor']
                                                           ,xr.end/sel['scaleFactor'],6)
                                        var upd_tks = tks.map(x=>x*sel['scaleFactor'])
                                        m[ri]['tks'].ticks = upd_tks
                                        m[ri]['ax'].axis_label = sel['unitName']
                                        }
                                '''                            
                                )
    # fig.js_on_event(RangesUpdate,cb)
    if ranges == 'x':
        fig.x_range.js_on_change('start',cb)
        fig.x_range.js_on_change('end',cb)
    elif ranges == 'y':
        fig.y_range.js_on_change('start',cb)
        fig.y_range.js_on_change('end',cb)
    else:
        print(ranges)
        fig.x_range.js_on_change('start',cb)
        fig.x_range.js_on_change('end',cb)
        fig.y_range.js_on_change('start',cb)
        fig.y_range.js_on_change('end',cb)
        

    for r in m:
        fmt = CustomJSTickFormatter(args=dict(fmt_oa = ins_df.to_dict('records')
                                              ,rng = r['range']
                                              )
                                    ,code='''
                                    var d = rng.end-rng.start
                                    for (var i = 0; i < fmt_oa.length-1; i++){
                                            if (d>=fmt_oa[i]['minRange'] && d < fmt_oa[i+1]['minRange']){
                                                    var sel = fmt_oa[i]                                                    
                                                    break
                                                    }
                                            }
                                    if (i == fmt_oa.length-1){
                                            var sel = fmt_oa[i]                                            
                                            }
                                    return tick/sel['scaleFactor']
                                    '''                            
                                    )
        r['ax'].formatter = fmt

def setIntervalRange(fig,renderers,dims=['x','y'],scale_bins=[{'thresh':10000,'x0':-5000,'x1':5000}
                                                              ,{'thresh':20000,'x0':-10000,'x1':10000}
                                                              ,{'thresh':100000,'x0':-50000,'x1':50000}
                                                              ]):
    '''
    NOT WORKING YET because bounds is not consistent.
    function to set a figure to follow particular "range bins" based on the extent of a set of renderers.
    dims = ['x','y'] or ['x'] or ['y']
    scale_bins = list of dictionaries, with each dictionary holding "thresh" (i.e. if bounds is under this threshold range), set 'x0' and 'x1' as the start/end of the range.
    
    '''
    xr = fig.x_range
    yr = fig.y_range
    rend_dict = {x.id:x for x in renderers}
    cb = CustomJS(args=dict(xr=xr,yr=yr,fig=fig
                            ,rend_dict=rend_dict
                            ,sb = scale_bins
                            ,dims=dims)
                  ,code='''
                  
                //var ctr = Bokeh.Models._known_models.get('Range1d')
                //var xr = new ctr()
                //var yr = new ctr()
                if (dims.includes('x')){
                        fig.x_range= xr
                        }
                if (dims.includes('y')){
                        fig.y_range = yr
                        }
                let result = {'x0':Infinity, 'x1':-Infinity,'y0':Infinity,'y1':-Infinity}
                for (var [k,v] of Object.entries(rend_dict)){     
                        const rect = Bokeh.index.get_one_by_id(k).bounds()                                            
                        console.log(k)
                        console.log(v.glyph.type)
                        console.log(rect)
                        if (rect != null && v.visible){
                                for (var k of ['x0','y0']){
                                    if (rect[k]<result[k]){
                                      result[k] = rect[k]
                                      }
                                    }
                                  for (var k of ['x1','y1']){
                                    if (rect[k]>result[k]){
                                      result[k] = rect[k]
                                      }
                                    }
                                }
                        }

                if (dims.includes('x')){
                        for (var i = 0; i < sb.length; i++){
                            if (result['x1']-result['x0'] < sb[i]['thresh']){
                                    xr.start = sb[i]['x0']
                                    xr.end = sb[i]['x1']
                                    break
                                    }
                            }
                        if (i == sb.length){
                                xr.start = result['x0']
                                xr.end = result['x1']
                                }
                        }
                if (dims.includes('y')){
                    for (var i = 0; i < sb.length; i++){
                        if (result['y1']-result['y0'] < sb[i]['thresh']){
                                yr.start = sb[i]['x0']
                                yr.end = sb[i]['x1']
                                break
                                }
                        if (i == sb.length){
                                yr.start = result['y0']
                                yr.end = result['y0']
                                }
                        }
                    }

                  '''
                  )
    for rend in renderers:
        rend.data_source.js_on_change('data',cb)
        
def linkNumericInputToSlider(slider,log=False):
    '''function to create a numeric input that will follow a slider value and vice versa.'''
    model = NumericInput(value=slider.value,low=slider.start,high=slider.end,mode='float')
    if log == True:
        model.value = 10**slider.value
        model.low = 10**slider.start
        model.high = 10**slider.end
        model.mode = 'float'
        if hasattr(model,'step'):
            model.step = slider.step
    else: 
        model.value = slider.value
        model.low = slider.start
        model.high = slider.end
        model.mode = 'float'
        if hasattr(model,'step'):
            model.step = slider.step
    ni = model
    
    ccb = CustomJS(args=dict(ni=ni,sl=slider,log=log)
                    ,code='''
                    sl.tags=[]
                    ni.tags=[]
                                        
                    if (cb_obj === sl){
                            if (log == true){
                                 ni.value = 10**sl.value
                                    }
                            else {
                                ni.value = sl.value
                                }
                            }
                    else {
                        // if ni, need to find nearest slider value
                        if (log == true){
                                var v = Math.log10(ni.value)
                                }
                        else {
                            var v = ni.value
                            }
                        //value input is less than slider start
                        if (v<=sl.start){
                                if (log == true){
                                     sl.value = sl.start
                                     ni.value = 10**sl.start
                                        }
                                else {
                                    sl.value = sl.start
                                    ni.value = sl.start
                                    }
                                }
                        //value is more than slider end
                        else if (v>=sl.end){
                                if (log == true){
                                     sl.value = sl.end
                                     ni.value = 10**sl.end
                                        }
                                else {
                                    sl.value = sl.end
                                    ni.value = sl.end
                                    }
                            }
                        
                        else {
                            var i = 1
                            do {
                                if (v<sl.start+sl.step*i){
                                        //value is now between current notch and previous
                                        if (log==true){
                                            var dl = Math.log10(ni.value)-(sl.start+sl.step*(i-1))
                                            var dr = (sl.start+(sl.step*i))-Math.log(ni.value)
                                            }
                                        else {
                                            var dl = ni.value-(sl.start+sl.step*(i-1))
                                            var dr = (sl.start+(sl.step*i))-ni.value
                                            }
                                        if (dl<=dr){
                                                var v = sl.start+sl.step*(i-1)
                                                }
                                        else {
                                            var v = sl.start+sl.step*i
                                            }
                                        sl.value = v
                                        if (log==true){
                                                ni.value = 10**v
                                                }
                                        else {
                                            ni.value = v
                                            }
                                        break
                                        }
                                i++
                                } while (true)
                            }
                        }
                    ''')
    cb = CustomJS(args=dict(ccb=ccb,sl=slider,ni=ni),
                  code='''

                  if (cb_obj.tags.length>0){
                          return
                          }
                  else {
                      sl.tags = ['run_me']
                      ni.tags = ['run_me']
                      ccb.execute(cb_obj)
                      sl.tags = ['run_me']
                      ni.tags = ['run_me']
                      }
                  '''
                  )

    ni.js_on_change('value',cb)
    slider.js_on_change('value',cb)
    return ni