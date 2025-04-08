// js function equivalent to np.linspace
function makeArr(startValue, stopValue, cardinality) {
  var arr = [];
  var step = (stopValue - startValue) / (cardinality - 1);
  for (var i = 0; i < cardinality; i++) {
	arr.push(startValue + (step * i));
  }
  return arr;
}

//given bnds {xmin: , xmax: , ymin: , ymax: }, Xdim = number of columns, Ydim number of rows
// returns an array of coordinate objects in a grid  
function genGridPts(bnds,Xdim,Ydim){
  var xa = makeArr(bnds.xmin,bnds.xmax,Xdim)
  var ya = makeArr(bnds.ymin,bnds.ymax,Ydim)
  var cx = d3.cross(ya,xa).map(v=>{return {'x':v[1],'y':v[0]}})
  return cx
    }
//builds an array of n points, from bnds [min,max] centered on value ptX (ptX is between min and max)
function arrayCenteredOnPt(bnds,n,ptX){
    var step = (bnds[1] - bnds[0] )/ (n - 1);
       //step forward
       var f = []
       var i = 0
       do {
       	var xn = ptX+i*step
        f.push(xn)
        i++
       	} while (xn<bnds[1])
       //step backward
       var b = []
       var i = 1
       do {
       	var xn = ptX+i*-step
        b.push(xn)
        i++
       	} while (xn>bnds[0])
    b.reverse()
    return b.concat(f)
    	}
		
//transforms columndatasource data to array of objects
function cds_to_objarray(cds_data){
  var keys = Object.keys(cds_data)
  var z = d3.transpose(Object.values(cds_data))
  var o = z.map(x=>Object.assign(...keys.map((k, i) => ({[k]: x[i]}))))
  return o}
  
//transforms array of objects to columndatasource "dictionary"/object 
function objarray_to_cds(objarray){
  var a = d3.transpose(objarray.map(x=>Object.values(x)))
  if (a.length>0){
    var d = Object.assign(...Object.keys(objarray[0]).map((k, i) => ({[k]: a[i]})))
    }
  return d
  }
  
//translates a d3 contour result into multiline-ready CDS data
function contours_to_cds(d3_contour){
    var cxs = []
    var cys = []
    var cv = []
    for (var vi=0;vi<d3_contour.length;vi++){                       
     		   for (var pi=0; pi<d3_contour[vi].coordinates.length;pi++){
     			  for (var ppi = 0; ppi<d3_contour[vi].coordinates[pi].length;ppi++){                                  
     					  var xy = d3.transpose(d3_contour[vi].coordinates[pi][ppi])
     					  cxs.push(xy[0])
     					  cys.push(xy[1])
     					  cv.push(d3_contour[vi].value)
     					  }
     					  }
     				   }
    return {'z':cv,'xs':cxs,'ys':cys}
    }
//numpy.clip equiv to bound a number
function clamp(num, lower, upper) {
		  return Math.min(Math.max(num, lower), upper);
	  }

//piecewise 1D interp
//given xx and yy  arrays, and xx is ascending, finds where xnew fits in xx, and interpolates a y
function interp(xnew,xx,yy){
   var fb = getFirstBetween(xnew,xx)
   if (fb['il']==undefined){
		   return yy[0]
		   }
   else if (fb['ir'] == undefined){
	   return yy[yy.length-1]
	   }
   else {
	   var p = (xnew-fb['xl'])/(fb['xr']-fb['xl'])
	   var r = d3.interpolateNumber(yy[fb['il']],yy[fb['ir']])(p)
	   return r
	   }
   }
   
// array xx is ascending --> returns the first occurence of x being in between two values in xx
// returns {'il':left side index, 'ir',right side index, 'xl': value on left, 'xr',value on right}
function getFirstBetween(x,xx){
  if (x<xx[0]){
    return {'il':undefined,'ir':0,'xl':undefined,'xr':xx[0]}
    }
  for (var i = 0; i < xx.length-1; i++){
    if (x >= xx[i] && x<xx[i+1]){
      return {'il':i, 'ir':i+1, 'xl':xx[i],'xr':xx[i+1]}
      }  
    }
  return {'il':xx.length-1, 'ir':undefined,'xl':xx[xx.length-1],'xr':undefined}
  }