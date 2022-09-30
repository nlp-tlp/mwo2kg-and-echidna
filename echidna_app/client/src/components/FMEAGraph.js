import React, {Component} from 'react';
import * as d3 from 'd3';
import {ForceGraph2D} from 'react-force-graph';
import ToggleButton from 'react-toggle-button'



// Makes the lines around aggregated nodes rotate.
// Very necessary.
var lineDashOffset = 0;
window.setInterval(function() {
	lineDashOffset -= 0.1;
}, 1);



// The FMEA Graph.
class Graph extends Component {

	constructor(props) {
		super(props);
		this.NODE_SIZE = 50;
		this.state = { graph2D: true, relationships: {}, selectedNode: null }
	};

	// Adjust the forces of the graph so it displays in a somewhat tree-like manner.
	resetGraphForces() {
		this.buildRelationshipsDictionary();
		if(this.state.graph2D) {
			this.fg.d3Force('charge').strength(-2200);
			this.fg.d3Force('link').distance(50);
        	this.fg.d3Force('collide', d3.forceCollide(d => { return Math.min(this.getSizeMultiplier(d), 3) * this.NODE_SIZE }));
		}
	}

	// Only update this component if either the mode has changed (2D or 3D) or the graph data has changed.
	shouldComponentUpdate(nextProps, nextState){
    	return this.state.graph2D !== nextState.graph2D ||
    		JSON.stringify(nextProps.data) !== JSON.stringify(this.props.data); // TODO: Replace with proper comparison function
	}

	// Reset the forces when this component updates.
	componentDidUpdate() {
		this.resetGraphForces();
	}

	// Reset the forces when this component mounts.
	componentDidMount() {
		this.resetGraphForces();
	}

	// Switch between 2D and 3D.
	toggle2D() {
		this.setState({
			graph2D: !this.state.graph2D
		})
	}

	getSizeMultiplier(node) {

		if(node.types[0] === "AMPLA_Event") {
			
			var eff_duration = node['effective_duration']
			var lost_feed = node['lost_feed'];

			var eff_duration_times_lost_feed = (eff_duration / 500) *
											   (lost_feed / 50);

			return 3 + eff_duration_times_lost_feed

		} else {



		var linkFrequencyTotal = 0;
		for(var i in this.state.relationships[node.id].linkFrequencies) {
			var freq = this.state.relationships[node.id].linkFrequencies[i];
			linkFrequencyTotal += freq;
		}
		// this.state.relationships[node.id].nodes.size

        return 1 + (0.1 * Math.min(linkFrequencyTotal - 1, 50)) // TODO: Sum of frequencies

		}
    }

	 // Store relationships between each node and each other node,
     // And with each node and each link
    buildRelationshipsDictionary() {
     	var nodes = this.props.data.nodes;
     	var links = this.props.data.links;

     	//console.log(this.props.data.nodes, this.props.data.links)

    	var relationships = {}
    	for(var i = 0; i < nodes.length; i++) {
    		relationships[nodes[i].id] = {nodes: new Set(), links: new Set(), linkFrequencies: {}}
    	}
    	for(var i = 0; i < links.length; i++) {
    		var l = links[i];
    		if(l.source.hasOwnProperty('id')) {
				var source = l.source['id'];
			} else {
				var source = l.source;
			}
			if(l.target.hasOwnProperty('id')) {
				var target = l.target['id'];
				//console.log('target', target)
			} else {
				var target = l.target;
			}




    		var n1 = source;
    		var n2 = target;

    		if(!relationships.hasOwnProperty(n1)) relationships[n1] = {nodes: new Set(), links: new Set(), linkFrequencies: {}}
    		if(!relationships.hasOwnProperty(n2)) relationships[n2] = {nodes: new Set(), links: new Set(), linkFrequencies: {}}
    		
    		relationships[n1].nodes.add(n2);
    		relationships[n2].nodes.add(n1);
    		relationships[n1].links.add(i);
    		relationships[n2].links.add(i);
    		relationships[n1].linkFrequencies[n2] = l.frequency;
    		relationships[n2].linkFrequencies[n1] = l.frequency;
    	}
    	//console.log(relationships)
    	this.setState({
    		relationships: relationships
    	});
    }

	render() {
		// TODO: These may need to change if there are more relationship types later on.
		// const linkColors = {
  //       	"SPO": "rgb(247, 151, 103)",
  //       	"SCO": "rgb(201, 144, 192)",
  //       	"RANGE": "rgb(241, 102, 103)",
  //       	"DOMAIN": "rgb(255, 196, 84)",
  //       }

        const nodeColours = {
        	"FLOC": 		["rgb(167, 232, 123)", "rgb(137, 209, 88)", "#222"],
        	"Item": 		["rgb(144, 206, 147)", "rgb(98, 184, 101)", "#222"],
        	"Activity": 	["rgb(91, 136, 218)" , "rgb(78, 123, 208)" , "white"],
        	"Observation": 	["rgb(234, 105, 104)", "rgb(230, 67, 65)", "white"],
        	"Location": 	["rgb(213, 113, 149)", "rgb(200, 64, 112)", "white"],
        	"Consumable": 	["rgb(233, 181, 201)", "rgb(213, 113, 152)", "#222"],
        	"Cardinality": 	["rgb(104, 197, 227)", "rgb(68, 176, 215)", "#222"],
        	"Time": 		["rgb(249, 200, 86)" , "rgb(210, 164, 26)" , "#222"],
        	"Agent": 		["rgb(241, 154, 104)", "rgb(236, 110, 41)", "white"],
        	"Attribute": 	["rgb(199, 142, 192)", "rgb(181, 104, 171)", "white"],
        	"Event": 		["rgb(215, 201, 174)", "rgb(197, 176, 138)", "222"],
        	"Specifier": 	["rgb(186, 191, 255)", "rgb(132, 135, 181)", "222"],
        	"AMPLA_Event": 	["rgb(70, 70, 70)", "rgb(60, 60, 60)", "#eee"],
        }	

        function getFLOCLabel(d) {

        	var s = '';
        	if(d.sort_field_name && d.sort_field_name.length > 0) {
        		s += d.sort_field_name;
        		s += "<br/>"
        	}
        	s += d.name        	
        	return s;
        }

        function getHTMLLabel(d) {
        	var s =  d.name + " (" + d.types[0] + ")<br/>"
        	s += d.tokens
        	s += "<hr/>"
        	for(var f in d.fields) {
        		s += "<span class='field-name'>" + f + ":</span> " + d.fields[f] + "<br/>";
        	}
        	return s
        }

		var graph;
		graph = <ForceGraph2D
			ref={el => this.fg = el}
			graphData={this.props.data}
			width={1420}
			height={810}
			nodeRelSize={this.NODE_SIZE}
			nodeVal={d => {
				return this.getSizeMultiplier(d);
			}}			
			d3AlphaDecay={0.03}
			d3VelocityDecay={0.8}
			d3AlphaMin={0.05}
			d3AlphaTarget={0.9}
			dagMode={'zout'}
			//dagLevelDistance={200}
			dagNodeFilter={
				function(n) {
					return n.types[0] === "FLOC";
				}
			}
			onEngineTick={ () => {this.props.graphLoaded(); }}
			nodeLabel={d => { 
				if(this.state.selectedNode) {
					return null;
				}
				if(d.types[0] === "Document") {
					return getHTMLLabel(d)
				}
				if(d.types[1] === "FLOC" || d.types[0] === "FLOC") {
					return getFLOCLabel(d)
				}

				return d.name + " (" + d.types.slice(0, d.types.length).join(", ") + ")" + ((d.name[0] === "<") ? " (aggregated)" : "");
				}
			}		
			nodeAutoColorBy={d => d.types}
			// linkLabel={d => { 
			// 	if(this.state.selectedNode) {
			// 		return null;
			// 	}
			// 	return "pingu" + d.link_name }// + " (" + d.frequency + ")" }
			// }			
	        linkCanvasObjectMode={() => 'after'}
	        //linkDirectionalParticles={ d => {return 5}}// (this.state.selectedNode ? 5 : 0); }}//this.state.selectedNode ? 5 : 0}}
	        //linkDirectionalParticleSpeed={0.002}

	        //linkDirectionalParticleWidth={11}
	        linkColor={d=> { 
	        	var linkColor = "#ccc";

	        	//var opacity = 0.2 + Math.min(0.3, (0.05 * (d.frequency - 1)));

	        	//var linkColor = "rgba(0, 0, 0, " + opacity + ")";
	        	
	            if(d.frequency >= 2) {
	            	linkColor = "#aaa";
	            }
	            if(d.frequency >= 3) {
	            	linkColor = "#999";
	            }
	            if(d.frequency >= 4) {
	            	linkColor = "#888";
	            }
	            if(d.frequency >= 5) {
	            	linkColor = "#777";
	            }
	            if(d.frequency >= 6) {
	            	linkColor = "#666";
	            }
	            if(d.frequency >= 7) {
	            	linkColor = "#555";
	            }
	            if(d.frequency >= 8) {
	            	linkColor = "#444";
	            }
	            if(d.link_name === "HAS_AMPLA_EVENT") {
	             	linkColor = "#333";
	            }
	            if(d.link_name === "SCO") {
	            	linkColor = "rgba(137, 209, 88, 0.5)";
	            }
	          
	        	return linkColor;
	        }}
	        linkLineDash={
	        	function(link) {
	        		if(link.link_name === "HAS_AMPLA_EVENT") {
	        			return [4, 3]
	       			} else if (link.link_name === "SCO") {
	       				return [12, 12]
	       			} else {
	       				return false
	       			}
	       		}
	    	}
	        linkWidth={d => {
	        	
	        	if(this.state.selectedNode && !this.state.relationships[this.state.selectedNode.id].links.has(d.index)) {
					return 0.000000001;
				}
				if(d.link_name === "HAS_AMPLA_EVENT") { 
	        		return 2;
	        	}
	        	return 1 * Math.min(d.frequency ** 0.8, 5)
	        }}
	        linkDirectionalArrowLength={d => {
	        	if(this.state.selectedNode && !this.state.relationships[this.state.selectedNode.id].links.has(d.index)) {
					return 0.000000001;
				}
	        	return 8 + 2 * Math.min(d.frequency, 5) 
	       	}}
	        linkDirectionalArrowRelPos={1}
	        onNodeHover ={node => {
	        	if(node) {
	        		document.getElementById("graph-wrapper").classList.add("hovered-node");
	        	} else {
	        		document.getElementById("graph-wrapper").classList.remove("hovered-node");
	        	}
	        }}
	        onNodeDrag={ node => {
	        	this.setState({
	        		selectedNode: node
	        	});
	        }}
	        onNodeDragEnd={node => {
            	// node.fx = node.x;
            	// node.fy = node.y;
            	// node.fz = node.z;
            	this.setState({
            		selectedNode: null
            	})
            	//this.state.selectedNode = null;
          	}}
          	onNodeClick={node => {
          		this.setState({
            		selectedNode: null
            	})
          	}}
	        nodeCanvasObject={(node, ctx, globalScale) => {

	        	// if(this.props.currentEntityFilters.has(node.types[0])) {
	        	// 	return;
	        	// }

	        	
	        	

	        	if(this.state.selectedNode && !(this.state.selectedNode === node || this.state.relationships[this.state.selectedNode.id].nodes.has(node.id))) {
	        		return;
	        	}

	        	//const thisNodeSize = this.NODE_SIZE * this.getSizeMultiplier(node);


	        	var thisNodeSize = Math.sqrt(Math.max(0, this.getSizeMultiplier(node) || 1)) * this.NODE_SIZE;

	        	const node_name = node.name.replace("_", " ");
	        	const node_words = node_name.split(" ");
	        	
	        	const nodeSortField = node['sort_field_name'];

	        	



	            //const label = node.name.length > 10 ? node.name.slice(0, 10) + '\n...' : node.name;
	            const fontSize = 13/(globalScale ** 0.6);

	            ctx.beginPath();
			    ctx.arc(node.x, node.y, thisNodeSize, 0, 2 * Math.PI, false);
			    //console.log(node)
			   
			   // if(!this.state.selectedNode || this.state.selectedNode === node || relationships[this.state.selectedNode.id].nodes.has(node.id)) {
	            ctx.fillStyle = nodeColours[node.types[0]] ? nodeColours[node.types[0]][0] : "#eee";
	            //} else {
	            //	ctx.fillStyle = '#e6e8ed';
	            //}
	            
			    ctx.fill();

			    ctx.beginPath();
			    ctx.arc(node.x, node.y, thisNodeSize-2, 0, 2 * Math.PI, false);
			   // if(!this.state.selectedNode || this.state.selectedNode === node || relationships[this.state.selectedNode.id].nodes.has(node.id)) {
			    ctx.strokeStyle = nodeColours[node.types[0]] ? nodeColours[node.types[0]][1] : "#ddd";
			   // } else {
			    //	ctx.strokeStyle = '#dfe1e6';
			    //}
			    ctx.lineWidth = 4;
			    if(node_name[0] === "<") {
			    	ctx.lineWidth = 8;
			    	ctx.save();
			    	ctx.setLineDash([5, 5]);
			    	ctx.lineDashOffset = lineDashOffset;
			    }
			    ctx.stroke();
			    ctx.restore();


	            ctx.font = `${fontSize}px Open Sans`;
	            if(node_name[0] === "<") {
	            	ctx.font = `italic ${fontSize}px Open Sans`;
	            }
	            ctx.textAlign = 'center';
	            ctx.textBaseline = 'middle';
	            ctx.fillStyle = '#222';
	           // if(!this.state.selectedNode || this.state.selectedNode === node || relationships[this.state.selectedNode.id].nodes.has(node.id)) {
	            ctx.fillStyle = nodeColours[node.types[0]] ? nodeColours[node.types[0]][2] : "#222";
	            //} else {
	            //	ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
	            //}
	            // if(this.state.relationships[node.id].nodes.size === 0) {
	            // 	ctx.fillStyle = '#222';
	            // }
	            
	            
	            var maxNodeWordLen = 9;
	            if(thisNodeSize > 40) {
	            	maxNodeWordLen = 15;
	            }

	            var nodeLabelLines = [];

	            for(var i = 0; i < Math.min(4, node_words.length); i++) {
	            	var word = node_words[i];
	            	if(word.length > maxNodeWordLen) {
	            		word = word.slice(0, maxNodeWordLen) + "..."
	            	}
	            	nodeLabelLines.push(word);
	            }

	            // Draw the frequency if a related node is selected
	            var drawFrequency = false;
	            if(this.state.selectedNode && this.state.selectedNode !== node && node.types[0] !== "AMPLA_Event" && node.types[0] !== "FLOC") {
	            	drawFrequency = true;
	            	nodeLabelLines.push(this.state.relationships[this.state.selectedNode.id].linkFrequencies[node.id])
	            }

	            if(node.types[0] === "AMPLA_Event") {
	            	nodeLabelLines.push("")
	            	nodeLabelLines.push("Eff dur: " + node['effective_duration'])
	            	nodeLabelLines.push("Lost feed: " + node['lost_feed'])
	            }
	            if(node.types[0] === "FLOC") {
	          
	            	nodeLabelLines = [];

	            	//console.log(nodeSortField)
	            	if(node['sort_field_name'] && node['sort_field_name'].length > 0) {
	            		nodeLabelLines.push(node['sort_field_name'])
	            	} else {
	            		nodeLabelLines.push(node.name)
	            	}
	            	
	            	
	            }

	            var yStart = -(fontSize/2) * (nodeLabelLines.length - 1);
	            for(var i = 0; i < nodeLabelLines.length; i++) {
	            	if(drawFrequency && i === nodeLabelLines.length - 1) {
	            		ctx.font = `bold ${fontSize}px Open Sans`;
	            	}
	            	ctx.fillText(nodeLabelLines[i], node.x, yStart + node.y + (fontSize + 2) * i);
	            }




	           	// if(node_words.length == 1) {
	           	// 	ctx.fillText(node_words[0].length > maxNodeWordLen ? node_words[0].slice(0, maxNodeWordLen) + "..." : node_words[0], node.x, node.y);
	           	// } else if (node_words.length == 2) {
	           	// 	ctx.fillText(node_words[0], node.x, node.y - ((fontSize + 2)/2));
	           	// 	ctx.fillText(node_words[1].length > maxNodeWordLen ? node_words[1].slice(0, maxNodeWordLen) + "..." : node_words[1], node.x, node.y + (fontSize + 2)/2);
	           	// }
	           	//  else if (node_words.length > 2) {
	           	// 	ctx.fillText(node_words[0], node.x, node.y - (fontSize + 2));
	           	// 	ctx.fillText(node_words[1], node.x, node.y);
	           	// 	ctx.fillText(node_words[2].length > maxNodeWordLen ? node_words[2].slice(0, maxNodeWordLen) + "..." : node_words[2], node.x, node.y + (fontSize + 2));
	           	// }

	           	// if(this.state.selectedNode && this.state.selectedNode !== node) {
	           	// 	ctx.font = `bold ${fontSize}px Open Sans`;
	           	//  	ctx.fillText(this.state.relationships[this.state.selectedNode.id].linkFrequencies[node.id], node.x, node.y + (fontSize));
	           	// }
	            
	        }}
			linkCanvasObject={(link, ctx, globalScale) => {

				if(!this.state.selectedNode) {
					return;
				}
				if(this.state.selectedNode && !this.state.relationships[this.state.selectedNode.id].links.has(link.index)) {
					return;
				}


	            const label = link.link_name;
	            const fontSize = 8/globalScale;
	            const textWidth = ctx.measureText(label).width;

	            const r = 60
	            
	            var linkColor = "#ccc";
	            
	            
	            //console.log(link)
	            const x1 = link.source.x
	            const x2 = link.target.x
	            const y1 = link.source.y
	            const y2 = link.target.y

	            const x = (x1 + x2) / 2
	            const y = (y1 + y2) / 2

	            const bgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

	            ctx.fillStyle = '#f1f3f7';
	            ctx.fillRect(x - bgDimensions[0] / 2, y - bgDimensions[1] / 2, ...bgDimensions);

	            ctx.font = `${fontSize}px Open Sans`;
	            ctx.textAlign = 'center';
	            ctx.textBaseline = 'middle';
	            ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
	            ctx.fillText(label, x, y); // + " (" + link.frequency + ")", x, y);		            
	          }}




		/>
	

		return (
			<div id="graph-wrapper">
				{graph}
			</div>
		)	

		
	}
}

// The toggle control at the top of the graph to switch between 2D and 3D.
class GraphToggle extends Component {
	constructor(props) {
		super(props);
	}

	render() {
		return (
			<div class="row" id="graph-toggle">
				<div><p>Set dimension</p></div>
					<div class="toggle-button">
						<ToggleButton
							inactiveLabel={'3D'}
							activeLabel={'2D'}
							colors={{
								activeThumb: {
									base: 'rgb(250,250,250)',
								},
								inactiveThumb: {
									base: 'rgb(62,130,247)',
								},
								active: {
									base: 'rgb(207,221,245)',
									hover: 'rgb(177, 191, 215)',
								},
								inactive: {
									base: 'rgb(65,66,68)',
									hover: 'rgb(95,96,98)',
								}
							}}
							value={ this.props.graph2D || false }
							onToggle={this.props.toggle2D} />
					</div>
				</div>
		)
	}
}

// The graph details, i.e. the box in the top right corner.
class GraphDetails extends Component {
	render() {
		return (
			<div id="graph-details-wrapper" class="padded">
				<h3>Legend</h3>
				<ul>
					<li>Class <span className="dot color-class"></span></li>
					<li>Relationship <span className="dot color-relationship"></span></li>
					<li>Property <span className="dot color-property"></span></li>
				</ul>
				<h3>Final Failure Effect Details</h3>
				<ul>
					<li>Enclosure heading, ventilation and cooling system
						<ul>
							<li>Heater system
								<ul>
									<li>Heaters</li>
								</ul>
							</li>
						</ul>
					</li>
				</ul>
			</div>
		)
	}
}

export default Graph;