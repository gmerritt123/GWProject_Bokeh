export default function({src,dsl,d3_div,pl ,ksl, bsl, stg_src}){
	var oa = cds_to_objarray(src.data) //converts bokeh CDS.data into array of objects
	//collect slider values
	var kseep = 10**ksl.value
	var bff = bsl.value
	//get max reservoir volume and depth
	var mvol = d3.max(stg_src.data['Volume'])
	var mdep = d3.max(stg_src.data['Depth']) 
	//water balance calc
	//for each time step
	for (var i = 0; i<oa.length; i++){
		  var v = oa[i]
		  //calculate inflows (with baseflow fraction applied)
		  var dV = v['Runoff']+v['Baseflow']*bff+v['Direct Precip']+v['Creek Inflow']
		  //volume pre aet
		  if (i ==0){
				  var vps = dV+1000 //hard-coded initial reservoir volume = 1000 ML, could be adjustable I suppose
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
		  //collect values
		  v['AET'] = -aet
		  v['Seepage'] = -vspg
		  v['V'] = vps+v['Dam Outflow'] //all catchment inflows and dam outflow
		  v['Depth'] = d
		  v['Shallow Groundwater'] = bff*v['Baseflow']
		  v['Surface Area'] = a
		  }
	// update bokeh CDS
	src.data = objarray_to_cds(oa)
	//filter this result by the date range slider (which we aren't currently using, so this filter has no effect).
	var oa = cds_to_objarray(src.data).filter(x=>(x.date>dsl.value[0])&&(x.date<dsl.value[1]))
	
	//build the sankey
	//calculate the sum of inflows/outflows
	var ru = d3.rollup(oa,
					 d=>{
						 var result = {}
						 for (var k of ['Shallow Groundwater', 'Runoff', 'Direct Precip', 'AET', 'Creek Inflow',
								'Dam Outflow','Seepage']){
									result[k] = d3.sum(d,v=>v[[k]])                                                
									}
						 return result
									})
	//calc net imbalancce
	var imbal = d3.sum(Object.values(ru))
	//define sankey links and nodes
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
	//d3 canvas work
	const format = d3.format(",.0f");
	const width = d3_div.width
	const height = d3_div.height
	// Create a SVG container.
	const svg = d3.create("svg")
	 .attr("width", width)
	 .attr("height", height)
	 .attr("viewBox", [0-25, -25, width+50, height+50])
	 .attr("style", "max-width: 100%; height: auto; font: 10px arial;");
	 
	// Constructs and configures the Sankey generator.
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
	//colormap for each component
	const cmap = {'Direct Precip':pl[1],'Runoff':pl[2],'Groundwater Inflow':pl[0], 'Creek Inflow':pl[3]
			 ,'AET':pl[4],'Dam Outflow':pl[5],'Reservoir':'#2ca02c','Groundwater Outflow':pl[6]
			 }
	//conditional colouring for imbalance term
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

	// Adds a hover-title on the nodes.
	rect.append("title")
	.text(d => {if (d.name == 'Imbalance/Change In Storage'){
			   return d.name+'\\n' + imbal.toFixed().toString() + ' ML'    
			   }
	   
			   else { return d.name+': '+d.value.toFixed().toString()+' ML'}
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
	
//labels with values
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
	//update the bokeh-model d3_div's text property to the svg's outerHTML
	d3_div.text = svg._groups[0][0].outerHTML 
}