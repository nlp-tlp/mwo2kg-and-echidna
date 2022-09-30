import React, {Component} from 'react';

// Table pagination
// The row at the top of the table with pagination (page x of y) and a filter selector
class TablePagination extends Component {
  constructor(props) {
    super(props);
    this.state = {
      desiredPage: ''
    }
  }

  handleChange(e) {
    var desiredPage = e.target.value;
    this.setState({
      desiredPage: desiredPage
    })
  }

  submitForm(e) {
    this.props.updatePageNumber(parseInt(this.state.desiredPage));   
    this.setState({desiredPage: ''})
    e.preventDefault();	     
  }

  render() {
    console.log(this.props.pageNumber, this.state.desiredPage)	  
    return (
      <div class="pagination">
      	<div class="table-filter">
      		<label>Filter:</label>
	      	<select onChange={(e) => this.props.updateTableFilter(e.target.value)}>
	      		<option value="All">All</option> 
	      		<option value="Class">Class</option>
	      		<option value="Relationship">Relationship</option>
	      		<option value="Property">Property</option>
	      	</select>
	    </div>
        <button className={ this.props.pageNumber === 1 ? 'disabled': '' }
          onClick = {() => {this.props.updatePageNumber(this.props.pageNumber - 1); }}>
            <i class="fa fa-chevron-left"></i>
        </button>
        <span class="page-x-of-y">Page <form onSubmit={this.submitForm.bind(this)} >
          <input value={ this.state.desiredPage } placeholder={ this.props.pageNumber } onChange={this.handleChange.bind(this)} />
          <input type="submit"/></form> of { this.props.totalPageNumbers }</span>
        <button class={ this.props.pageNumber === (this.props.totalPageNumbers) ? 'disabled': '' } onClick = {() => this.props.updatePageNumber(this.props.pageNumber + 1)}><i class="fa fa-chevron-right"></i></button>
      </div> 
    )
  }
}

// The header row of the table
class TableHeaders extends Component {
	constructor(props) {
		super(props);
	}

	render() {
		return (
			<tr>
				{ this.props.data.map((heading, i) => <th>{heading}</th>)}
			</tr>
		)
	}
}

// A cell of the table, rendered differently depending on its corresponding header
class TableCell extends Component {
	constructor(props) {
		super(props);
	}

	render() {
		var header = this.props.header
		
		var cellValue
		if(header === "uri") {
			cellValue = <a href={this.props.data} class="uri-button"><i class="fa fa-external-link"></i>View</a>
		} else if (header === "labels") {
			cellValue = <span>
				{
					this.props.data.map( (label, i) => 
						<span className={"label color-" + label.toLowerCase()}>{label}</span>
					)
				}
			</span>
		} else {
			cellValue = this.props.data
		}

		return (
			<td>{cellValue}</td>
		)
	}
}

// A row of the table
class TableRow extends Component {
	constructor(props) {
		super(props);
	}

	render() {
		return (
			<tr> { this.props.data.map((column, i) => <TableCell data={column} header={this.props.headers[i]}/> )} </tr>
		)
	}
}

// The FMEA Table.
class Table extends Component {

	constructor(props) {
		super(props)
		this.state = {
			pageNumber: 1,
			rowsPerPage: 15,
			rows: [],
			tableFilter: "All"
		}
	}

	componentDidUpdate(prevProps, prevState) {
		if(prevProps.data.rows.length !== this.props.data.rows.length) {
			this.updateFilteredRows();
		}
	}

	updateFilteredRows() {
		var filter = this.state.tableFilter;
		var filteredRows;
		function sameLabel(row) {
			return row[1][1] === filter; // This should ideally not be hardcoded this way
		}
		if(filter === "All") {
			filteredRows = this.props.data.rows;
		} else {
			filteredRows = this.props.data.rows.filter(sameLabel);
		}
		console.log(filteredRows, filter);
		this.setState({
			rows: filteredRows,
			pageNumber: 1
		})
	}

	updateTableFilter(filter) {
		this.setState({
			tableFilter: filter
		}, this.updateFilteredRows);
	}

	updatePageNumber(pageNumber) {
		this.setState({pageNumber: pageNumber})
	}

	render () {
		var visibleRows = this.state.rows.slice((this.state.pageNumber - 1) * this.state.rowsPerPage, (this.state.pageNumber) * this.state.rowsPerPage,  )

		return (
			<div class="table-wrapper">

				<TablePagination
					pageNumber = { this.state.pageNumber}
					totalPageNumbers={Math.ceil(this.state.rows.length / this.state.rowsPerPage) }
					updatePageNumber = {this.updatePageNumber.bind(this)}
					updateTableFilter = {this.updateTableFilter.bind(this)}
				/>


				<table id="fmea-table">
					<thead>
						<TableHeaders data={this.props.data.headers}/>
					</thead>
					<tbody>
						{ visibleRows.map( (row, i) => <TableRow index={i} data={row} headers={this.props.data.headers}/>)}
					</tbody>
				</table>
			</div>
		)
	}
}

export default Table;