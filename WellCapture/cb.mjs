//import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7.9/+esm"
//import * as d3Contour from 'https://cdn.jsdelivr.net/npm/d3-contour@4.0.2/+esm'

export default function({src,sl_dict,f,w_src,w_lbl,c_src,c_lbl
                        ,hr_src,color_bar,rb,pt_cb
                        }){
	//collect slider values
	var q = sl_dict['Pumping'].value/10**9 //cubic km/s 
	var k = 10**sl_dict['Conductivity'].value/1000 //km/s
	var i = 10**sl_dict['Gradient'].value
	var b = sl_dict['Thickness'].value/1000 //km

	//get ymax and x0_conf
	var ymax = q/(2*k*i*b)
	var x0 = q/(2*Math.PI*k*i*b)

	//calculate array for y based on ymax
	var ya = makeArr(-ymax*0.999,ymax*0.999, 1000)
	//calculate array for x based on ya
	var xa = ya.map(y=>y/(Math.tan(2*Math.PI*k*i*b*y/q))) //convert m to km

	//update src
	src.data = {'x':xa, 'y':ya}
	src.change.emit()
	//calculate figure bounds
	//hard set x range based on x0.
	var sbs = [0.25,1,5,25,50,100].map(x=>x/25) // 
	
	for (var ib = 0; ib < sbs.length; ib++){
    	if (x0<sbs[ib]){
        	var x0v = sbs[ib]
        	break
        	}
    	}
    if (ib==sbs.length){
        var x0v = x0
        }
	var xr = [x0v*-25,x0v*1.1]
	
	f.x_range.start = xr[0]
	f.x_range.end = xr[1]
	//aspect ratio
	var ar = f.inner_height/f.inner_width
    var r = xr[1]-xr[0]
    f.y_range.start = -r/2*ar
    f.y_range.end = r/2*ar

	
	//calculate max width
	var w = q/(k*i*b)
	
	//update max width annotation
	w_src.data={'x0':[x0*-22],'x1':[x0*-22],'y0':[-w/2], 'y1':[w/2]}
    w_lbl.visible = true
    w_lbl.text = 'Max Width = '+w.toFixed(2).toString()+' km'
    w_lbl.x = x0*-21.25
    
    //update culm pt annotation
    c_src.data={'x0':[0],'x1':[x0],'y0':[0], 'y1':[0]}
    c_lbl.visible = true
    c_lbl.text = 'X₀ =\n'+x0.toFixed(2).toString()+' km'
    c_lbl.x = -x0*1.7
    c_lbl.y = w*0.05
    
    //build and evaluation grid for drawdown
    var xr = f.x_range.end-f.x_range.start
    var yr = f.y_range.end-f.y_range.start
    var bnds = {'xmin':f.x_range.start-xr*0.5,'xmax':f.x_range.end+xr*0.5
        ,'ymin':f.y_range.start-yr*0.5,'ymax':f.y_range.end+yr*0.5}
    var nx  = 200
    var ny = 200


    function calcH(x,y,i,q,b,k){
        var rgt = -i*(x-1000) 
        var wt = q/(2*Math.PI*b*k)*Math.log((x**2+y**2)**0.5/1000)
        return {'rgt':rgt,'wt':wt, 'h':rgt+wt}
        }
        
    //calc head at well
    var hwell = calcH(1e-20,1e-20,i,q,b,k)
    hwell = hwell['h']*1000

    //get arrays for grid --> centered on .01,.01 (reasonable distance)
    var xa = arrayCenteredOnPt([bnds['xmin'],bnds['xmax']],nx,0)
    var ya = arrayCenteredOnPt([bnds['ymin'],bnds['ymax']],ny,0)

    var grd = []

    for (var yi = 0; yi < ya.length; yi++){
        for (var xi = 0; xi < xa.length; xi++){
            var h = calcH(xa[xi],ya[yi],i,q,b,k)
            var obj = {'x':xa[xi],'y':ya[yi],'wt':h['wt']*1000,'h':h['h']*1000-hwell}
            grd.push(obj)
            }
        }

    var ctr = d3.contours().thresholds(25).size([xa.length,ya.length])
    //var ctr = d3Contour.contours().thresholds(25).size([nx,ny])
    if (rb.active==0){
        var contours = contours_to_cds(ctr(grd.map(x=>x.wt)))
        color_bar.title = 'Drawdown Contours (m)'
        }
    else {
        var contours = contours_to_cds(ctr(grd.map(x=>x.h)))
        color_bar.title = 'Hydraulic Head Contours (m, relative to well)'
        }
    
    //back to coords
    contours['xs'] = contours['xs'].map(x=>x.map(xx=>xx/xa.length*(xa[xa.length-1]-xa[0])+xa[0]))
    contours['ys'] = contours['ys'].map(y=>y.map(yy=>yy/ya.length*(ya[ya.length-1]-ya[0])+ya[0]))
    hr_src.data=contours  
    pt_cb.execute()        	
}