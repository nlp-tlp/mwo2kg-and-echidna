import React, {Component} from 'react';
import logo from './logo.svg';
import './App.scss';

import Table from './components/FMEATable';
import Graph from './components/FMEAGraph';

import nlp_tlp_logo from './images/nlp-tlp-logo.png'
import centre_logo from './images/DSTM-Logo-RGB.png'

import DatePicker from "react-datepicker";
 
import "react-datepicker/dist/react-datepicker.css";

import ReactAutocomplete from 'react-autocomplete';

import { createMuiTheme, ThemeProvider } from "@material-ui/core";
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Slider from '@material-ui/core/Slider';

import echidna_logo from './images/echidna_logo.png';


// Header: The Component for the dark header row at the top of the page.
class Header extends Component {
	render() {
		return (
			<header>
      			<div class="app-title"><img src={echidna_logo}/></div>        
      		</header>
		)
	}
}

// SidePanel: The Component for the side panel on the left, encompassing the controls/navigation.
// Displays either View or Manage FMEA, depending on this.props.view.
class SidePanel extends Component {
	constructor(props) {
		super(props);
		this.state = {
			view: "Documents"
		}
	}

	changeView(view) {
		this.setState({
			view: view
		})
	}

	render() {
		return (
			<div class="padded" id="side-panel">
				<Tabs 
					  tabNames = {[this.props.documentsName + "s", "Entities"]}
					  view = {this.state.view}
					  changeView = {this.changeView.bind(this)}/>
				<GraphControls 
					 		   documentsName={this.props.documentsName}
							   view={this.state.view}
							   entityClassTree={this.props.entityClassTree}
							   toggleEntityFilter={this.props.toggleEntityFilter}
							   toggleAggregation={this.props.toggleAggregation}
							   currentEntityFilters={this.props.currentEntityFilters}
							   currentAggregationFilters={this.props.currentAggregationFilters}
							   currentAggregationFiltersDisabled={this.props.currentAggregationFiltersDisabled}
							   structuredFields={this.props.structuredFields}
							   applyFilter={this.props.applyFilter}
							   clearFilter={this.props.clearFilter}
							   currentStructuredFieldFilters={this.props.currentStructuredFieldFilters}
							   loadingStage={this.props.loadingStage}
							   showDisconnectedEntities={this.props.showDisconnectedEntities}
							   toggleDisconnectedEntities={this.props.toggleDisconnectedEntities}
				 />
				<Logo/>
			</div>
		)
	}
}

// The search controls (i.e. "Ask me anything" box on the left panel)
class SearchControls extends Component {
	render() {
		return (
			<div class="search-controls">
				<input class="search-box" placeholder="Coming soon"></input>
				<button class="search"><i class="fa fa-search"></i></button>
			</div>
		)
	}
}

// Representation button: the "Graph" or "Table" button.
class RepresentationButton extends Component {
	render() {
		var active = (this.props.name == this.props.representation) ? " active" : "";
		return (			
			<div class="button-wrapper" onClick={() => this.props.changeRepresentation(this.props.name)}>
				<div class={"fmea-view-control-button" + active}>
					<i class={"fa " + this.props.icon}></i>{this.props.name}
				</div>
			</div>

		)
	}
}

// Representation controls: a wrapper for the "Graph" and "Table" selection buttons.
class RepresentationControls extends Component {
	render() {

		var representations = [
			["Graph", "fa-share-alt"],
			["Table", "fa-table"]
		]
		return ( 
			<div class="fmea-view-controls">
				{ representations.map((r, i) => 
					<RepresentationButton name={r[0]}
										  icon={r[1]}										  
										  representation={this.props.representation}
										  changeRepresentation = {this.props.changeRepresentation}/>)}
				
				
			</div>

		)
	}
}

// View FMEA Controls: the contents of the "View FMEA" tab on the left.
class ViewFMEAControls extends Component {
	render() {
		return (
			<div class="inner-side-panel padded-sm">

				<section>
					<h3 class="centered">Ask me something:</h3>
					<SearchControls/>	
				</section>
				<section>

					<h3 class="centered">FMEA view</h3>
					<RepresentationControls changeRepresentation = {this.props.changeRepresentation}
											representation={this.props.representation} />
				</section>

			</div>
		)
	}
}

class StructuredFieldStringFilter extends Component {

	render () {
		return (
			<li>
				<span class="field-name">{this.props.name}</span>
				<input></input>
				<button class="disabled">Apply</button>
			</li>
		)
	}
}

const theme = createMuiTheme({
   palette: {
      primary: {
         main: "#273043" // This is an orange looking color
                },
      secondary: {
         main: "#ffcc80" //Another orange-ish color
                 }
            },
});

class StructuredFieldIntegerFilter extends Component {

	constructor(props) {
		super(props);
		this.state = {
			min: -1,
			max: -1,
			canBeApplied: false,
			canBeCleared: false,
		}
	}

	componentDidMount() {
		this.setState({
			min: this.props.min,
			max: this.props.max,
		})
	}



	handleChange(e, newValue) {
		this.setState({
			min: newValue[0],
			max: newValue[1],
			canBeApplied: true,

		})
	}

	onMinChange(e) {
		this.setState({
			min: e.target.value,
			canBeApplied: true,
		})
	}

	onMaxChange(e) {
		this.setState({
			max: e.target.value,
			canBeApplied: true,
		})
	}


	getText(value) {
		return value;
	}

	submit() {
		var filter = {
			name: this.props.name,
			value: {
				min: this.state.min,
				max: this.state.max,
			}
		}
		this.setState({
			canBeApplied: false,
			canBeCleared: true,
		}, () => this.props.applyFilter(filter));
	}

	submitClear() {
  		this.setState({
  			min: this.props.min,
  			max: this.props.max,
  			canBeApplied: false,
  			canBeCleared: false
  		}, () => this.props.clearFilter(this.props.name))
	}

	render () {
		var marks = [
			{
				value: this.props.min,
				label: this.props.min,
			}, 
			{
				value: this.props.max,
				label: this.props.max,
			}
		]
		return (
			<li class={this.state.canBeCleared ? "active-filter" : ""}>
				<span class="field-name">{this.props.name}</span>

				<div className="date-group">
					<span>Min:</span>
					<input onChange={this.onMinChange.bind(this)} min={this.props.min} max={Math.min(this.props.max, this.state.max)} value={this.state.min} type="number"></input>
				</div>
				<div className="date-group">
					<span>Max:</span>
					<input onChange={this.onMaxChange.bind(this)} min={Math.max(this.props.min, this.state.min)} max={this.props.max} value={this.state.max} type="number"></input>
			    </div>

				


				<div class={"buttons" + (this.state.canBeApplied || this.state.canBeCleared ? " visible" : "")}>
					<button class={this.state.canBeApplied ? "" : "disabled"} onClick={this.submit.bind(this)}><i class="fa fa-check"></i>&nbsp;Apply</button>
					<button class={"clear-filter" + (this.state.canBeCleared ? "" : " disabled")} onClick={this.submitClear.bind(this)}><i class="fa fa-times"></i>&nbsp;Clear</button>
				</div>
			</li>
		)
	}
}
/* 
<ThemeProvider theme={theme}>
					<Slider
				        value={[this.state.min, this.state.max]}
				        onChange={this.handleChange.bind(this)}
				        valueLabelDisplay="auto"
				        aria-labelledby="range-slider"
				        getAriaValueText={this.getText}
				        min={this.props.min}
				        max={this.props.max}
				        valueLabelDisplay="auto"
				        marks={marks}
				      />
				    </ThemeProvider>*/
/* 
<div class="date-group">
					<span>Min:</span>
					<input onChange={this.onMinChange.bind(this)} min={this.props.min} max={this.props.max} value={this.state.min} type="number"></input>
				</div>
				<div class="date-group">
					<span>Max:</span>
					<input onChange={this.onMaxChange.bind(this)} min={this.props.min} max={this.props.max} value={this.state.max} type="number"></input>
				</div>
*/

class StructuredFieldCategoricalRadioFilter extends Component {
	constructor(props) {
		super(props);
	
		this.state = {
			selectedValue: 'all',
			canBeApplied: false,
			canBeCleared: false,
		}
	}

	async onChange(e) {		
		await this.setState({
			selectedValue: e.target.value,
			canBeApplied: true,
		})


		
	}

	submit() {
		if(this.state.selectedValue === "all") {
			this.submitClear();
		} else {
			var filter = {
				name: this.props.name,
				value: this.state.selectedValue
			}
		
			this.setState({
				canBeApplied: false,
				canBeCleared: true,
			}, () => this.props.applyFilter(filter))
		}
	}

	submitClear() {
  		this.setState({
  			selectedValue: 'all',
  			canBeApplied: false,
  			canBeCleared: false
  		}, () => this.props.clearFilter(this.props.name))
		
	}

	render() {
		console.log(this.props.options)
		return (
			<li class={this.state.canBeCleared ? "active-filter" : ""}>
				<span class="field-name">{this.props.name}</span>

				<form class="categorical-field-container" onSubmit={e => e.preventDefault()}>
					<div className="radio-group">
						<input type="radio" name={"input-" + this.props.name + '-all'} id={"input-" + this.props.name + '-all'} value="all" checked={this.state.selectedValue === "all"} onChange={this.onChange.bind(this)}/>
						<label for={"input-" + this.props.name + '-all'}>All</label>
					</div>

					{this.props.options.map((option, index) => 
						<div className="radio-group">
							<input type="radio" name={"input-" + this.props.name + '-' + option} id={"input-" + this.props.name + '-' + option} value={option} checked={this.state.selectedValue === option} onChange={this.onChange.bind(this)}/>
							<label for={"input-" + this.props.name + '-' + option}>{option}</label>
						</div>
					)}
				</form>

				<div class={"buttons" + (this.state.canBeApplied || this.state.canBeCleared ? " visible" : "")}>
					<button class={this.state.canBeApplied ? "" : "disabled"} onClick={this.submit.bind(this)}><i class="fa fa-check"></i>&nbsp;Apply</button>
					<button class={"clear-filter" + (this.state.canBeCleared ? "" : " disabled")} onClick={this.submitClear.bind(this)}><i class="fa fa-times"></i>&nbsp;Clear</button>
				</div>




			</li>



		)
	}
}

class StructuredFieldCategoricalFilter extends Component {

	constructor(props) {
		super(props);
		//console.log('constructor')
		this.state = {
			searchTerm: '',
			canBeApplied: false,
			canBeCleared: false
		}
	}

	updateSearchTerm(val) {
		var canBeApplied = val.length > 0
    	this.setState({
    	  canBeApplied: canBeApplied,
    	  searchTerm: val
    	})
  	}

  	submit() {
		var filter = {
			name: this.props.name,
			value: this.state.searchTerm
		}
		this.setState({
			canBeApplied: false,
			canBeCleared: true,
		}, () => this.props.applyFilter(filter))
		
  	}

  	submitClear() {
  		this.setState({
  			searchTerm: '',
  			canBeApplied: false,
  			canBeCleared: false
  		}, () => this.props.clearFilter(this.props.name))
  	}

	render () {
		return (
			<li class={this.state.canBeCleared ? "active-filter" : ""}>
				
				<span class="field-name">{this.props.name}</span>

				


				<form class="categorical-field-container" onSubmit={e => e.preventDefault()}>
					<ReactAutocomplete
			            items={this.props.autocompleteSuggestions}
			            shouldItemRender={ (item, value) => 
			              value.length >= 1 && item.toLowerCase().startsWith(value.toLowerCase())
			            }
			            getItemValue={item => item}
			            renderItem={(item, highlighted) => 
			              <div key={item} class={"suggestion " + (highlighted ? 'highlighted' : '')}> {item}</div>
			            }
			            autoHighlight={false}
			            renderMenu= {
			              function(items, value, style) {
			                return <div class="autocomplete-suggestions" style={{ ...style, ...this.menuStyle }} children={items}/>
			              }
			            }
			            wrapperStyle={{
			              display: 'block',
			              width: '100%',              
			            }}
			            value={this.state.searchTerm}
			            id="documentSearch"
			            inputProps={{placeholder: "Search"}}
			            onChange={(event) => this.updateSearchTerm(event.target.value)}
			            onSelect={value => this.updateSearchTerm(value)}
			          />
			    </form>

				<div class={"buttons" + (this.state.canBeApplied || this.state.canBeCleared ? " visible" : "")}>
					<button class={this.state.canBeApplied ? "" : "disabled"} onClick={this.submit.bind(this)}><i class="fa fa-check"></i>&nbsp;Apply</button>
					<button class={"clear-filter" + (this.state.canBeCleared ? "" : " disabled")} onClick={this.submitClear.bind(this)}><i class="fa fa-times"></i>&nbsp;Clear</button>
				</div>
			</li>
		)
	}
}

class StructuredFieldDateFilter extends Component {

	constructor(props) {
		super(props);
		this.state = {
			minDate: this.props.minDate,
			maxDate: this.props.maxDate,
			startDate: this.props.minDate,
			endDate: this.props.maxDate,

			canBeApplied: false,
			canBeCleared: false
		}

		console.log(this.props, "<<<<XXXX")
	}


	updateStartDate(date) {
		this.setState({
			startDate: date,
			canBeApplied: true,
		})
	}

	updateEndDate(date) {
		this.setState({
			endDate: date,
			canBeApplied: true,
		})
	}

	submitClear() {
		this.setState({
			startDate: this.props.minDate,
			endDate: this.props.maxDate,
			canBeApplied: false,
			canBeCleared: false,
		}, () => this.props.clearFilter(this.props.name));
		
	}

	submit() {
		var sd = this.state.startDate;
		var ed = this.state.endDate;
		var filter = {
			name: this.props.name,
			earliest: {year: sd.getFullYear(), month: sd.getMonth() + 1, day: sd.getDate()},
			latest: {year: ed.getFullYear(), month: ed.getMonth() + 1, day: ed.getDate()}
		}
		//console.log("Start", this.state.startDate)
		//console.log("Start", this.state.endDate)
		//console.log("Filter", filter)
		this.setState({
			canBeApplied: false,
			canBeCleared: true,

		}, () => this.props.applyFilter(filter));
		
	}

	render() {
		return (
			<li class={this.state.canBeCleared ? "active-filter" : ""}>
				<span class="field-name">{this.props.name}</span>
				<div class="date-group">
					<span>From:</span>
					<DatePicker className={!this.state.canBeApplied && !this.state.canBeCleared ? "default-date" : ""} showMonthDropdown showYearDropdown dropdownMode="select" dateFormat="dd/MM/yyyy" minDate={this.state.minDate} maxDate={this.state.maxDate} selected={this.state.startDate} onChange={this.updateStartDate.bind(this)}/>
				</div>
				<div class="date-group">
					<span>To:</span>
					<DatePicker className={!this.state.canBeApplied && !this.state.canBeCleared ? "default-date" : ""} showMonthDropdown showYearDropdown dropdownMode="select" dateFormat="dd/MM/yyyy" minDate={this.state.minDate} maxDate={this.state.maxDate} selected={this.state.endDate} onChange={this.updateEndDate.bind(this)}/>
				</div>
				<div class={"buttons" + (this.state.canBeApplied || this.state.canBeCleared ? " visible" : "")}>
					<button class={this.state.canBeApplied ? "" : "disabled"} onClick={this.submit.bind(this)}><i class="fa fa-check"></i>&nbsp;Apply</button>
					<button class={"clear-filter" + (this.state.canBeCleared ? "" : " disabled")} onClick={this.submitClear.bind(this)}><i class="fa fa-times"></i>&nbsp;Clear</button>
				</div>
			</li>
		)
	}
}

class EntityClassFilter extends Component {

	constructor(props) {
		super(props);
		this.state = {
			filteredChildren: (this.props.name === "Rotating_Equipment" || this.props.name === "Item") ? 1 : 0,
			droppedDown: this.props.name === "Item" ? true : false,
			firstUpdate: true, // Just for the demo
		}
		
	}

	toggleDropdown() {
		this.setState({
			droppedDown: !this.state.droppedDown,
		}, this.props.toggleChildrenVisible);
	}

	adjustFilteredChildren(i) {
		if(!this.props.adjustFilteredChildren) return;
		this.setState({
			filteredChildren: Math.max(0, this.state.filteredChildren + i)
		}, () => { this.props.adjustFilteredChildren(i)})
	}
	resetFilteredChildren() {
		this.setState({
			filteredChildren: 0
		})
	}

	// Bad code but it works! Puts the line on the left of the category so you know which ones have been filtered
	// Without it you'd have no idea which nodes are being displayed if you hid the category you were filtering
	componentDidUpdate(prevProps) {

		// if(this.state.filteredChildren === 0) {
		// 	return;
		// }


		if(prevProps.checked && !this.props.checked && this.props.canToggle ) {
			if(this.props.name === "Item" && this.state.firstUpdate) {
				this.setState({
					firstUpdate: false,
				});
				return;
			}
			this.adjustFilteredChildren(-this.state.filteredChildren);
			return;
		}
		if(!prevProps.checked && this.props.checked && this.props.canToggle) {
			this.adjustFilteredChildren(1);
			return;
		}
		// Subsumed (top level category was clicked while this one had active filters)
		if(prevProps.checked && this.props.checked && prevProps.canToggle && !this.props.canToggle) {
			this.adjustFilteredChildren(-this.state.filteredChildren);
			return;
		}



		// if(prevProps.checked && !prevProps.canToggle) return
		// if(prevProps.checked != this.props.checked) {
		// 	if(this.props.adjustFilteredChildren && this.props.canToggle) {
		// 		this.adjustFilteredChildren((this.props.checked) ? 1 : -1)
		// 		this.props.adjustFilteredChildren((this.props.checked) ? 1 : -1);
		// 	}
			
		// }
	}

	render() {
		var hasSubfilters = this.props.entityClass !== "Document" && Object.keys(this.props.children).length > 0;
		if(hasSubfilters) {
			var subfilters = <EntityClassFilters
							 entityClassTree={this.props.children}
							 toggleEntityFilter={this.props.toggleEntityFilter}
							 toggleAggregation={this.props.toggleAggregation}
							 currentEntityFilters={this.props.currentEntityFilters}			
							 currentAggregationFilters={this.props.currentAggregationFilters}			
							 currentAggregationFiltersDisabled={this.props.currentAggregationFiltersDisabled}			
							 ulClass={"subfilters" + (this.state.droppedDown ? "" : " hidden")}
							 parentEntityClass={this.props.full_name}
							 adjustFilteredChildren={this.adjustFilteredChildren.bind(this)}

							 />	
			
		} else {
			var subfilters = '';
		}
		if(this.props.entityClass !== "Document") {
			var aggregation = <span class={"checkbox aggregation-checkbox" + (this.props.canAggregate ? "" : " disabled")} id={"aggregate-" + this.props.full_name}						
							onClick={this.props.canAggregate ? () => this.props.toggleAggregation(this.props.full_name) : null}></span>
		}

		var displayName = this.props.name;
		if(displayName.length > 20 && displayName !== "Show work order nodes") {
			displayName = displayName.slice(0, 20) + "..."
		}
		var dropdown = hasSubfilters ? 
				(<span class="dropdown" onClick={this.toggleDropdown.bind(this)}>
					<i class={"fa fa-caret-" + (this.state.droppedDown ? "up" : "down")}></i>
				</span>) : <span class="dropdown dropdown-empty"></span>
		var base_class = this.props.full_name.split("/")[0]
		return (
			<li
				class={"entity-filter colour-" + base_class + " border-" + base_class + "" + (this.props.checked ? " checked" : "") + (this.props.aggregated ? " aggregated" : "") + (this.state.filteredChildren > 0 ? " child-has-filter" : "")}>
				<span class="li-inner">
					{dropdown}
					<span class="text" title={this.props.name}>
						{displayName}
					</span>
					<span class="frequency">
						{this.props.frequency}
					</span>
					<span class={"checkbox filter" + (this.props.canToggle ? "" : " disabled")} id={"filter-" + this.props.full_name}					title={this.props.canToggle ? "" : "This filter cannot be disabled while the parent filter is enabled."}
							onClick={this.props.canToggle ? () => {this.props.toggleEntityFilter(this.props.full_name);} : null}></span>
					{aggregation}
				</span>

				{subfilters}



			</li>
		)
	}
}

class EntityClassFilters extends Component {

	constructor(props) {
		super(props);
		this.state = {
			childrenVisible: false,
		}
	}

	toggleChildrenVisible() {
		this.setState( {
			childrenVisible: !this.state.childrenVisible,
		})
	}

	render() {


		return (
			<ul class={this.props.ulClass}>

				{ this.props.ulClass ==="filters" ? (
				
				<li	class={"header-row entity-filter"}>
					<span class="li-inner">
						
						<span class="text">
							Entity class
						</span>
						<span class="frequency" title="Frequency">
							#
						</span>
						<span class={"icon filter"} ><i class="fa fa-eye" title="Visible"></i></span>
						<span class={"icon aggregate"} ><i class="fa fa-database" title="Aggregate"></i></span>
					</span>

				</li>) : ""}


			{ Object.keys(this.props.entityClassTree).map((entityClass, i) => 
				<EntityClassFilter 
					name={this.props.entityClassTree[entityClass]["name"]}
					full_name={this.props.entityClassTree[entityClass]["full_name"]}
					entityClass={entityClass}
					toggleEntityFilter={this.props.toggleEntityFilter}
					toggleAggregation={this.props.toggleAggregation}
					checked={!this.props.currentEntityFilters.has(this.props.entityClassTree[entityClass]["full_name"])}
					aggregated={this.props.currentAggregationFilters.has(this.props.entityClassTree[entityClass]["full_name"])}
					children={this.props.entityClassTree[entityClass]["children"]}
					frequency={this.props.entityClassTree[entityClass]["frequency"]}
				 	currentEntityFilters={this.props.currentEntityFilters}
				 	currentAggregationFilters={this.props.currentAggregationFilters}
				 	currentAggregationFiltersDisabled={this.props.currentAggregationFiltersDisabled}
				 	canToggle={this.props.parentEntityClass === "Entity" || this.props.currentEntityFilters.has(this.props.parentEntityClass)}
				 	canAggregate={!this.props.currentAggregationFiltersDisabled.has(this.props.entityClassTree[entityClass]["full_name"])
				 		&& !this.props.currentEntityFilters.has(this.props.entityClassTree[entityClass]["full_name"])
				 	}
				 	adjustFilteredChildren={this.props.adjustFilteredChildren}
				 	
				/>) }
			</ul>
			)

	}

}

// Convert the day/month/year string into a Date object
function parseDateString(dateStr) {
	var splitStr = dateStr.split('/');
	return new Date(splitStr[2] + "-" + splitStr[1] + "-" + splitStr[0]);
}

// Manage FMEA Controls: the contents of the "Manage FMEA" tab on the left.
class GraphControls extends Component {



	renderSFFilter(structuredField) {
			var t = structuredField.type;
			if (t === "Date") {

				return (
					<StructuredFieldDateFilter 
						name={structuredField.name}
						minDate={parseDateString(structuredField.earliest)}
						maxDate={parseDateString(structuredField.latest)}
						applyFilter={this.props.applyFilter}
						clearFilter={this.props.clearFilter}
					/>
				)
			} else if (t === "Integer") {
				return (
					<StructuredFieldIntegerFilter 
						name={structuredField.name}
						min={structuredField.min}
						max={structuredField.max}
						applyFilter={this.props.applyFilter}
						clearFilter={this.props.clearFilter}

					/>
				)
			} else if (t === "String") {
				return (
					<StructuredFieldStringFilter 
						name={structuredField.name}
						applyFilter={this.props.applyFilter}
						clearFilter={this.props.clearFilter}
					/>
				)
			}  else if (t === "Categorical") {


				if(structuredField.options.length >= 10) {


					return (
						<StructuredFieldCategoricalFilter 
							name={structuredField.name}
							autocompleteSuggestions={structuredField.options}
							applyFilter={this.props.applyFilter}
							clearFilter={this.props.clearFilter}

						/>
					)
				} else {
					return (
						<StructuredFieldCategoricalRadioFilter 
							name={structuredField.name}
							options={structuredField.options}
							applyFilter={this.props.applyFilter}
							clearFilter={this.props.clearFilter}
						/>
					)
				}



			}

		}


	render() {

		var thiss = this;
		var view;

		// if(this.props.view === "Documents") {
		return (
			<div class={"inner-side-panel padded-sm" + (this.props.loadingStage ? " loading" : "")}>

				<div style={{'display': this.props.view === "Documents" ? "block" : "none"}}>




					<ul class="filters">
						<EntityClassFilter 		name={"Show " + this.props.documentsName.toLowerCase() + " nodes"}
												entityClass={"Document"}
												toggleEntityFilter={this.props.toggleEntityFilter}
												checked={!this.props.currentEntityFilters.has("Document")}
												full_name={"Document"}
												canToggle={true}
												/>
					</ul>

					<ul class="filters structured-fields">
						{ this.props.structuredFields.map((structuredField, i) => 
							thiss.renderSFFilter(structuredField)) }
					</ul>
				</div>
				<div style={{'display': this.props.view === "Entities" ? "block" : "none"}}>
					 	<ul class="filters">
						 	<li
								class={"entity-filter" + (this.props.showDisconnectedEntities ? " checked" : "")} onClick={this.props.toggleDisconnectedEntities}>
								<span class="li-inner">
									
									<span class="text">
										Show disconnected entities
									</span>					
									<span class={"checkbox filter"} id={"filter-show-disconnected-entities"}></span>
								</span>
							</li>
						</ul>
					
					
						<EntityClassFilters entityClassTree={this.props.entityClassTree}
							 toggleEntityFilter={this.props.toggleEntityFilter}
							 toggleAggregation={this.props.toggleAggregation}
							 currentEntityFilters={this.props.currentEntityFilters}
							 currentAggregationFilters={this.props.currentAggregationFilters}
							 currentAggregationFiltersDisabled={this.props.currentAggregationFiltersDisabled}
							 ulClass={"filters"}
							 parentEntityClass={"Entity"}
							 adjustFilteredChildren={() => {}}
						/>
											
				
				</div>
			</div>
		)

		

		
		
	
	}
}

// Tab: A button to switch between "View" and "Manage" FMEA.
class Tab extends Component {
	render() {
		return (
			<button onClick={() => this.props.changeView(this.props.tabId)}
					class={this.props.view == this.props.tabId ? "active" : ""}>
					{this.props.name}
			</button>
		)
	}
}

// Tabs: a wrapper for the buttons to switch between "View" and "Manage" FMEA.
class Tabs extends Component {

	constructor(props) {
		super(props);
	}

	render() {
		var tabs = ["Documents", "Entities"];
		var tabNames = this.props.tabNames;
		return (
			<div class="button-tabs">
				{ tabs.map((tab, i) => <Tab name={tabNames[i]}
											tabId={tab}
											changeView={this.props.changeView}
											view={this.props.view}/>) }
			</div>
		)
	}
}


// Powered by SHL: the wrapper containing the "Powered by the System Health Lab" footer on the bottom left.
class Logo extends Component {
	render() {
		return (
			<div id="logo-wrapper">
				<a href="http://agent.csse.uwa.edu.au/" target="_blank">
					<img src={nlp_tlp_logo}></img>
				</a>
				<a href="http://maintenance.org.au/" target="_blank">
					<img src={centre_logo}></img>
				</a>
			</div>

		)
	}
}


// MainWindow: The Component for the main panel (encompassing the graph and graph info).
class MainGraphWindow extends Component {

	constructor(props) {
		super(props);
		this.state = {data: {nodes: [], links: [], entityClassTree: {}, entityClasses: [], structuredFields: [], documentsName: "Work order", "totalDocuments": 0}, 
					  filteredData: {nodes: [], links: [], totalDocuments: 0},
					  currentStructuredFieldFilters: {},
					  currentEntityFilters: new Set(["Document"]),
					  currentAggregationFilters: new Set(),
					  currentAggregationFiltersDisabled: new Set(), // These are the aggregation filters that cannot be applied because the parent
					  												// is currently being aggregated over.
					  currentlyVisibleNodes: 0,
					  showDisconnectedEntities: false,
					  loadingStage: "Querying graph" }
		
	}

	async query() {
		const fetchConfig = {
		    method: 'GET',
		    headers: {
		      'Accept': 'application/json',
		      'Content-Type': 'application/json'
		    }
		  };

		//console.log(JSON.stringify(Array.from(this.state.currentAggregationFilters)), "<<<<<<<<<<<")

		await this.setState({
			loadingStage: "Querying graph",
		})

		//fetch('http://agent.csse.uwa.edu.au/maintenance_kg_api/graph?query=' + JSON.stringify(this.state.currentStructuredFieldFilters), fetchConfig) // TODO: move localhost out
		fetch('http://localhost:5000/graph?query=' + JSON.stringify(this.state.currentStructuredFieldFilters) + "&aggregation=" + JSON.stringify(Array.from(this.state.currentAggregationFilters)), fetchConfig) // TODO: move localhost out
			.then(response =>
				response.text())
			.then((data) => {

				
				
				this.setState({data: JSON.parse(data), loadingStage: null}, this.getFilteredData); // TODO: Update filtered data
			});
		


	}

	componentWillMount() {
		//fetch('http://agent.csse.uwa.edu.au/maintenance_kg_api/graph') // TODO: move localhost out

		



		fetch('http://localhost:5000/graph') // TODO: move localhost out
			.then(response =>
				response.text())
			.then((data) => {
				
				console.log(data);

				this.setState({loadingStage: null, data: JSON.parse(data)}, () => {

				

					this.toggleEntityFilter("Item")
					this.toggleEntityFilter("Item/Rotating_Equipment")
					this.toggleEntityFilter("Location")
					this.toggleEntityFilter("Agent")
					this.toggleEntityFilter("Time")
					this.toggleEntityFilter("Cardinality")
					this.toggleEntityFilter("Consumable")
					this.toggleEntityFilter("Specifier")
					this.toggleEntityFilter("Attribute")
					this.toggleEntityFilter("Event")

					//console.log(this.state.data.entityClassTree)
					//for(var key in this.state.data.entityClassTree) {
					//	console.log(key, this.state.data.entityClassTree[key])
					//}
				}); // TODO: Update filtered data
			});
	

	}

	getFilteredData() {

		

		//console.log(this.state.currentEntityFilters, " <<< ")

		//console.log(this.state.data.links);
		var filteredLinks = [];
		var filteredNodes = [];
		var goodNodeIds = {};
		var goodDocumentNodeIds = {};
		console.log("Getting filtered data")
		console.log(this.state.currentEntityFilters)
		console.log("Document in filters?", this.state.currentEntityFilters.has("Document"))
		for(var i = 0; i < this.state.data.nodes.length; i++) {
			var n = this.state.data.nodes[i];
			//console.log(n)
			for(var t = 0; t < n.types.length; t++) {
				//console.log(n.types[t])
				if(n.types[t] === "Instance") continue;
				
				if(!this.state.currentEntityFilters.has(n.types[t])) {
					if(n.types[t] === "Document" && !this.state.showDisconnectedEntities) {
						goodDocumentNodeIds[n.id] = n;
						break;
					} else {
						filteredNodes.push(n)
						goodNodeIds[n.id] = n;
						break;
					}
				}
			}			
		}
		//console.log(this.state.data.nodes)
		//console.log(goodNodeIds)
		var linkedNodes = new Set()
		//console.log(goodDocumentNodeIds);
		for(var i = 0; i < this.state.data.links.length; i++) {
			var l = this.state.data.links[i];
			//console.log(l, l.source, l.target, l.source.hasOwnProperty('id'))

			if(l.source.hasOwnProperty('id')) {
				var source = l.source['id'];
			} else {
				var source = l.source;
			}
			if(l.target.hasOwnProperty('id')) {
				var target = l.target['id'];
			} else {
				var target = l.target;
			}

			// Only show documents that are related to shown nodes, i.e. don't treat them the same
			if(goodNodeIds.hasOwnProperty(source) && goodNodeIds.hasOwnProperty(target)) {
				filteredLinks.push(l)
				//console.log(source, this.state.data.nodes[source])
				linkedNodes.add(goodNodeIds[source])
				linkedNodes.add(goodNodeIds[target])
			}			
		}
		
		
		var documentSet = new Set();
		for(var i = 0; i < this.state.data.links.length; i++) {
			var l = this.state.data.links[i];
			//console.log(l, l.source, l.target, l.source.hasOwnProperty('id'))

			if(l.source.hasOwnProperty('id')) {
				var source = l.source['id'];
			} else {
				var source = l.source;
			}
			if(l.target.hasOwnProperty('id')) {
				var target = l.target['id'];
			} else {
				var target = l.target;
			}
			if(linkedNodes.has(goodNodeIds[source]) && goodDocumentNodeIds.hasOwnProperty(target)) {
				filteredLinks.push(l)
				linkedNodes.add(goodDocumentNodeIds[target])
				documentSet.add(target);
			}
		}

	
		var linkedNodesList = Array.from(linkedNodes);

		//console.log(filteredLinks)
		//console.log(Array.from(linkedNodes));

		console.log("Retrieved filtered data")
		if(!this.state.showDisconnectedEntities) {
			var nodes = linkedNodesList;
		} else {
			var nodes = filteredNodes;
		}

		console.log(nodes)
		this.setState({
			loadingStage: "Building graph",
			filteredData: {
				nodes: nodes,
				links: filteredLinks,
				totalDocuments: this.state.currentEntityFilters.has("Document") ? this.state.data.totalDocuments : documentSet.size,

			},
		});		
	}	

	clearStructuredFieldFilter(filter_name) {
		var currentStructuredFieldFilters = this.state.currentStructuredFieldFilters;
		delete currentStructuredFieldFilters[filter_name];
		this.setState({
			currentStructuredFieldFilters: currentStructuredFieldFilters
		}, this.query);
	}

	async applyStructuredFieldFilter(filter) {
		//console.log('queried', filter);


		var currentStructuredFieldFilters = this.state.currentStructuredFieldFilters;
		currentStructuredFieldFilters[filter.name] = filter;

		this.setState({
			currentStructuredFieldFilters: currentStructuredFieldFilters
		}, this.query);

		
	}

	// disable: deletes all aggregation filters across this class and all children
	toggleAggregation(entityClass, disable=false) {
		//console.log(this.state.data.entityClassChildren)

		var currentAggregationFilters = Object.assign(this.state.currentAggregationFilters);

		this.setState({
			loadingStage: (disable || currentAggregationFilters.has(entityClass)) ? "Removing aggregation" : "Building aggregation"
		}, () => {
		
		
		var currentAggregationFiltersDisabled = Object.assign(this.state.currentAggregationFiltersDisabled);
		var update = 'add';
		var didSomething = false;


		if(!disable) {
			if(currentAggregationFilters.has(entityClass)) {
				update = 'delete';
				currentAggregationFilters.delete(entityClass);
			} else {
				currentAggregationFilters.add(entityClass);
			}
			didSomething = true;
		} else {
			if(currentAggregationFilters.has(entityClass)) {
				didSomething = true;
			}
			currentAggregationFilters.delete(entityClass);
			update = 'delete';
		}

		for(var i in this.state.data.entityClassChildren[entityClass]) {
			var ec = this.state.data.entityClassChildren[entityClass][i];
			if(update === "add") {
				currentAggregationFiltersDisabled.add(ec); // Add ec to the disabled aggregations so that the tree renders nicely.
			} else {
				if(currentAggregationFilters.has(ec)) {
					didSomething = true;
				}
				currentAggregationFilters.delete(ec);
				currentAggregationFiltersDisabled.delete(ec);

			}
		}

		// if(!didSomething) {
		// 	return;
		// }

		this.setState({
			currentAggregationFilters: currentAggregationFilters,
			currentAggregationFiltersDisabled: currentAggregationFiltersDisabled
		}, () => {  this.query(); console.log(this.state.currentAggregationFilters); console.log(this.state.currentAggregationFiltersDisabled);  }) // TODO: Call API
		});
	}

	toggleDisconnectedEntities() {
		console.log('hello')
		this.setState({
			showDisconnectedEntities: !this.state.showDisconnectedEntities
		}, this.getFilteredData);
	}

	// Toggle the given entity class filter.
	// Will also clear aggregation across this class and any children.
	toggleEntityFilter(entityClass, callback) {
		//console.log(this.state.data.entityClassChildren)


		this.setState({
			loadingStage: "Applying filter"
		}, () => {
			
			var currentEntityFilters = Object.assign(this.state.currentEntityFilters);
			var currentAggregationFilters = Object.assign(this.state.currentAggregationFilters);
			var update = 'add';
			var aggregationRemoved = false;
			console.log(currentEntityFilters.has("Document"));
			if(currentEntityFilters.has(entityClass)) {
				update = 'delete';
				currentEntityFilters.delete(entityClass);
				currentAggregationFilters.delete(entityClass);			
				
				
			} else {
				if(this.state.currentAggregationFilters.has(entityClass)) {
					this.toggleAggregation(entityClass, true);
					aggregationRemoved = true;
				}
				currentEntityFilters.add(entityClass);
			}

			for(var i in this.state.data.entityClassChildren[entityClass]) {
				var ec = this.state.data.entityClassChildren[entityClass][i];
				if(update === "add") {
					currentEntityFilters.add(ec);
				} else {
					currentEntityFilters.delete(ec);
				}
			}


			console.log(currentEntityFilters)
			this.setState({
				currentEntityFilters: currentEntityFilters			
			}, () => { if(!aggregationRemoved) {this.getFilteredData() } });


		});
	}

	graphHasLoaded() {	
		if(this.state.loadingStage === "Building graph") {	
			this.setState({
				loadingStage: null,
			});	
		}	
	}


	render() {		

		//var filteredData = this.getFilteredData()

		var filteredData = this.state.filteredData;

		console.log(filteredData)


		console.log('rendering', this.state.filteredData.nodes.length)

		//console.log(this.state.currentStructuredFieldFilters)
		//console.log(this.state.currentEntityFilters)

		var showingAll = Object.keys(this.state.currentStructuredFieldFilters).length === 0 && 
						(this.state.currentEntityFilters.size === 1 && this.state.currentEntityFilters.has("Document"))
		var fromIncluding = (this.state.currentEntityFilters.has("Document") ? "from" : "(including")
		var includingEnd = (this.state.currentEntityFilters.has("Document") ? "" : ")")

		var graphDetails = "Showing " + (showingAll ? "all " : " ") + 
						   filteredData.nodes.length + " nodes " + fromIncluding + " " + this.state.filteredData.totalDocuments + " " + this.state.data.documentsName.toLowerCase() + "s" + includingEnd + ".";
		if(filteredData.nodes.length === 0) {
			graphDetails = "No results found."
		}
		if(this.state.loadingStage) {
			graphDetails = <span><i class="fa fa-cog fa-spin"></i>&nbsp;&nbsp;{this.state.loadingStage}...</span>
		}

		return (
			<div id="main-container">	
				<SidePanel 
						   documentsName={this.state.data.documentsName}
						   entityClassTree  = {this.state.data.entityClassTree} 
						   toggleEntityFilter   = {this.toggleEntityFilter.bind(this)}
						   toggleAggregation   = {this.toggleAggregation.bind(this)}
						   currentEntityFilters = {this.state.currentEntityFilters}
						   currentAggregationFilters = {this.state.currentAggregationFilters}
						   currentAggregationFiltersDisabled = {this.state.currentAggregationFiltersDisabled}
						   structuredFields  			 = {this.state.data.structuredFields} 
						   applyFilter   = {this.applyStructuredFieldFilter.bind(this)}
						   clearFilter   = {this.clearStructuredFieldFilter.bind(this)}
						   currentStructuredFieldFilters = {this.state.currentStructuredFieldFilters}
						   loadingStage={this.state.loadingStage}
						   showDisconnectedEntities={this.state.showDisconnectedEntities}
						   toggleDisconnectedEntities={this.toggleDisconnectedEntities.bind(this)}
						   

				/>	
				<div id="main-window">
					<div class={"main-window-inner visible"}>
						<div id="graph-details">{graphDetails}</div>
						<Graph data = {filteredData} 
							   currentEntityFilters={this.state.currentEntityFilters}
							   graphLoaded={this.graphHasLoaded.bind(this)}
						/>					
					</div>
				</div>
			</div>
		)
			
	}
}


class App extends Component {

  constructor(props) {
  	super(props);
  	this.state = {
  		representation: "Graph", // or Table
  	}
  }

  changeRepresentation(representation) {
  	this.setState({
  		representation: representation
  	})
  }

  render() {
  	return (
	    <div id="app">
	    	<Header/>	    	      			
			<MainGraphWindow/>
	    </div>
	)
  }
}

export default App;
