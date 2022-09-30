import json, time
from py2neo import Graph
from colorama import Fore, Back, Style

from .queries import document_query, floc_query, ampla_query, build_query
from .QueryResult import QueryResult


from echidna_app import app

class KnowledgeGraph():

	""" A model representing a Knowledge Graph.
	"""
	

	def __init__(self, graph_password, logger):
		""" Creates a Knowledge Graph
		
		Args:
		    graph_password (TYPE): The password of the Neo4j graph.
		    logger (TYPE): app.logger, to log things to.
		"""
		self.graph = Graph(password = graph_password)
		self.logger = logger

		self.default_result = []
		self.default_result_ampla = []
		self.default_result_floc = []

		self.structured_fields = []
		self.documents_name = "Document"

		self.get_metadata()


	def query_graph(self, query, aggregated_fields):
		""" Query the graph and return the result of the query in JSON format.
		If a query is specified, the graph will be queried accordingly.
		If aggregated fields is populated, then the result will be aggregated
		on those particular fields.
		
		Args:
		    query (str): A query to run on the graph.
		    aggregated_fields (list): A list of field names to aggregate on.
		
		Returns:
		    dict: A JSON representation of the query result, which looks like:

			{
				"totalDocuments": The number of documents returned.
				"nodes": A list of nodes.
				"links": A list of links.
				"entityClasses": A list of entity classes.
				"entityClassTree": A dictionary representing the class tree.
				"entityClassChildren": A dict of all entity classes and their
									   descendants.
				"structuredFields": A list of the structured fields.
				"documentsName": The name of documents e.g. "work orders"
			}



		"""
		where_clause = ''
		if query:
			where_clause = build_query(query, self.structured_fields)

		self.logger.debug("Querying graph...")
		start_time = time.time()
		
		cursor = self.graph.run(document_query(where_clause))
		cursor_flocs = self.graph.run(floc_query(where_clause))
		cursor_ampla = self.graph.run(ampla_query())

		self.logger.debug("Done. (%.2fs)" % (time.time() - start_time))
		start_time = time.time()
		self.logger.debug("Calculating result...")


		query_result = QueryResult(self.structured_fields, self.documents_name)
		query_result.build(
			cursor, cursor_flocs, cursor_ampla, aggregated_fields
		)

		self.logger.debug("Done. (%.2fs)" % (time.time() - start_time))
		self.logger.debug("Getting class tree...")

		self.logger.info(
			"Query returned %d nodes and %d edges from %d documents." %
			(len(query_result.nodes), len(query_result.links),
				query_result.total_documents))


		return query_result.to_json()

	def get_metadata(self):
		"""Get the metadata (structured fields and name of documents
		(e.g. "Work Order")) from metadata.json.
		TODO: Store this in the graph table in SQL and grab it from there
		in views.py.
		"""
		with open('echidna_app/data/metadata.json') as f:
			metadata = json.load(f)
			self.structured_fields = metadata['structured_fields']
			self.documents_name = metadata['documents_name']