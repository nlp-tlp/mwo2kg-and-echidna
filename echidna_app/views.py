import json
from flask import Flask, render_template, Response, request, jsonify

from echidna_app import app
from echidna_app.models.knowledge_graph.KnowledgeGraph import KnowledgeGraph

KnowledgeGraph = KnowledgeGraph(graph_password = app.config["GRAPH_PASSWORD"], logger = app.logger)

@app.route('/', methods=['GET'])
def get_homepage():
	return render_template("index.html")


@app.route('/graph', methods=['GET'])
def get_graph():

	query       = json.loads(request.args['query']) if 'query' in request.args else None
	aggregated_fields = json.loads(request.args['aggregation']) if 'aggregation' in request.args else []

	graph_result = KnowledgeGraph.query_graph(
		query = query,
		aggregated_fields = aggregated_fields,		
	)	

	res = jsonify(graph_result)
	return res, 200;
