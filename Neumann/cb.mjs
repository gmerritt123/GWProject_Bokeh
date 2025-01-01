// js function equivalent to np.linspace
function makeArr(startValue, stopValue, cardinality) {
  var arr = [];
  var step = (stopValue - startValue) / (cardinality - 1);
  for (var i = 0; i < cardinality; i++) {
	arr.push(startValue + (step * i));
  }
  return arr;
}

import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7.9/+esm"
import cephes from 'https://cdn.jsdelivr.net/npm/cephes@2.0.0/+esm'
await cephes.compiled

export default function({src_dict,sl_dict,f}){
	//collect slider values
	var q = sl_dict['Q'].value
	var tr = 10**sl_dict['T'].value
	var b = sl_dict['b'].value
	var r = sl_dict['R'].value
	var ss = 10**sl_dict['Ss'].value
	var sy = sl_dict['Sy'].value
	
    //evaluate well function at 100 points along 1e-5 and 1e4 seconds
	var w_u = makeArr(-5,4,100).map(x=>cephes.expn(1,10**x))
	// same points, get inverse
	var u_inv = makeArr(-5,4,100).map(x=>1/10**x)
	//early curve term
    var t_a_term = r**2 * ss * b / 4 / tr
    console.log(ss)
    //late curve term
    var t_b_term = r**2 * sy / 4 / tr
    
    var s_term = q/(4*Math.PI*tr)
    
    var t_a = u_inv.map(x=>x*t_a_term)
    var t_b = u_inv.map(x=>x*t_b_term)
    var s = w_u.map(x=>x*s_term < 1e-2 ? 'nan' : x*s_term)
    
    //update the theis datasources
    src_dict['EarlyT'].data={'t':t_a,'dd':s}
    src_dict['LateT'].data={'t':t_b,'dd':s}
    f.y_range.start = 0.01
    f.y_range.end = d3.max(s)*10
    f.x_range.start = 1
    f.x_range.end = d3.max(t_a)*10
    
    
}