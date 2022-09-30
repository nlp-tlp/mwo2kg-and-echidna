"""
QueryResult
@author Michael Stewart

A class for processing a query result from the graph into a data structure
suitable for the Echidna visualisation.
"""

import time
from collections import OrderedDict

class QueryResult():

	def __init__(self, structured_fields, documents_name):
		self.total_documents = 0
		self.nodes = []
		self.links = []
		self.entity_classes = []
		self.entity_class_tree = {}
		self.entity_class_children = {}
		self.structured_fields = structured_fields
		self.documents_name = documents_name


	def build(self, cursor, cursor_flocs, cursor_ampla, aggregated_fields):
		nodes_dict = {}
		unaggregated_nodes_dict = {}
		links_dict = {}
		links_dict_a = {}
		documents_set = set()
		node_frequencies = {}

		start_time = time.time()

		# A map of original node IDs to the aggregated node IDs,
		# such as the ID for "centrifugal pump" -> the ID for "pump".
		aggregation_map = {}
		
		i = 0
		
		for result in cursor:
			result = cursor.current
			i += 1		

			#print(result)
			id_d = result['id_d']
			id_1 = result['id_1']
			id_2 = result['id_2']
			id_1_aggregated = False
			id_2_aggregated = False
			name_1 = result['name_1']
			name_2 = result['name_2']
			types_1 = [i for i in result['types_1'] if i != "Instance"]
			types_2 = [i for i in result['types_2'] if i != "Instance"]		


			if id_1 not in unaggregated_nodes_dict:
				unaggregated_nodes_dict[id_1] = {'id': id_1, 'name': name_1, 'types': types_1}
			if id_2 not in unaggregated_nodes_dict:
				unaggregated_nodes_dict[id_2] = {'id': id_2, 'name': name_2, 'types': types_2}

			
			for a in aggregated_fields:
				for x, t in enumerate(types_1):				
					if t == a:
						name_1 = "<" + a.split("/")[-1] + ">"
						aggregation_map[id_1] = a
						id_1 = a
						id_1_aggregated = True		
						types_1 = types_1[:x+1]			
						break
				for x, t in enumerate(types_2):
					if t == a:					
						name_2 = "<" + a.split("/")[-1] + ">"
						aggregation_map[id_2] = a
						id_2 = a
						id_2_aggregated = True
						types_2 = types_2[:x+1]
						break
						
			if id_1 == id_2:
				continue

			#id_1, id_2 = sorted([str(id_1), str(id_2)])

			documents_set.add(id_d)
			if id_d not in nodes_dict:
				#fields = dict({d: str(result['fields'][d]) for d in result['fields'] if d not in ['doc_id', 'tokens']})
				nodes_dict[id_d] = {'id': id_d, 'name': str(result['doc_id']), 'tokens': result['tokens'], 'types': result['types_d']}
				#print(nodes_dict[id_d])
			if id_1 not in nodes_dict:
				nodes_dict[id_1] = {'id': id_1, 'name': name_1, 'types': types_1}
			if id_2 not in nodes_dict:
				nodes_dict[id_2] = {'id': id_2, 'name': name_2, 'types': types_2}

			if id_d not in links_dict_a:
				links_dict_a[id_d] = {}

			if id_1 not in links_dict_a[id_d]:
				links_dict_a[id_d][id_1] = { 'source': id_1, 'target': id_d, 'frequency': 1, 'link_name': result['link_name_a']}
				#print(id_d, id_1, 'x')

			if id_2 not in links_dict_a[id_d]:
				links_dict_a[id_d][id_2] = { 'source': id_2, 'target': id_d, 'frequency': 1, 'link_name': result['link_name_a']}
				#print(id_d, id_2, 'y')

			if id_1 not in links_dict:
				links_dict[id_1] = {}
			if id_2 not in links_dict[id_1]:
				links_dict[id_1][id_2] = { 'source': id_2, 'target': id_1, 'frequency': 1, 'link_name': result['link_name']}
			else:
				links_dict[id_1][id_2]['frequency'] += 1

		#print("Adding FLOC links...")
		#print(len(links_dict))
		with_sf = 0
		without_sf = 0

		for result in cursor_flocs:
			result = cursor.current

			id_f1 = result['id_f1']
			name_f1 = result['name_f1']
			types_f1 = [i for i in result['types_f1'] if i != "Instance"]
			id_r = result['id_r']
			id_f2 = result['id_f2']
			name_f2 = result['name_f2']		
			types_f2 = [i for i in result['types_f2'] if i != "Instance"]

			#sf_name_f1 = ''
			#sf_name_f2 = ''
			#if(len(result['sort_field_name_f1']) > 0):
			sf_name_f1 = result['sort_field_name_f1']
			#if(len(result['sort_field_name_f2']) > 0):
			sf_name_f2 = result['sort_field_name_f2']

			if len(sf_name_f1) > 0:
				with_sf += 1
			else:
				without_sf += 1
			if len(sf_name_f2) > 0:
				with_sf += 1
			else:
				without_sf += 1


			#print(sf_name_f1)

			for a in aggregated_fields:
				for x, t in enumerate(types_f1):				
					if t == a:
						name_f1 = "<" + a.split("/")[-1] + ">"
						aggregation_map[id_f1] = a
						id_f1 = a
						id_f1_aggregated = True		
						types_f1 = types_f1[:x+1]			
						break
				for x, t in enumerate(types_f2):
					if t == a:					
						name_f2 = "<" + a.split("/")[-1] + ">"
						aggregation_map[id_f2] = a
						id_f2 = a
						id_f2_aggregated = True
						types_f2 = types_f2[:x+1]
						break


			if id_f1 == id_f2:
				continue

			

			#if id_f1 not in nodes_dict:
			nodes_dict[id_f1] = {'id': id_f1, 'pingu': 5, 'name': name_f1, 'sort_field_name': sf_name_f1, 'types': types_f1}
			#if id_f2 not in nodes_dict:
			nodes_dict[id_f2] = {'id': id_f2, 'pingu': 7, 'name': name_f2, 'sort_field_name': sf_name_f2, 'types': types_f2}

			if id_f1 not in links_dict:
				links_dict[id_f1] = {}
			if id_f2 not in links_dict[id_f1]:
				links_dict[id_f1][id_f2] = { 'source': id_f1, 'target': id_f2, 'frequency': 1, 'link_name': result['link_name_r']}

		# Add the AMPLA nodes
		#print("Adding AMPLA nodes...")
		for result in cursor_ampla:
			result = cursor.current

			id_x = result['id_x']
			if id_x in aggregation_map:
				id_x = aggregation_map[id_x]
			#print(result)
			id_am = result['id_am']
			name_am = result['name_am']
			types_am = result['types_am']
			effective_duration = result['effective_duration']
			lost_feed = result['lost_feed']

			if id_am not in nodes_dict:
				nodes_dict[id_am] = {'id': id_am, 'name': name_am, 'types': types_am, 'effective_duration': effective_duration, 'lost_feed': lost_feed}

			if id_x not in links_dict:
				links_dict[id_x] = {}
			if id_am not in links_dict[id_x]:
				links_dict[id_x][id_am] = { 'source': id_x, 'target': id_am, 'frequency': 1, 'link_name': result['link_name_r']}


		#print(len(links_dict))


		#print("\nDone (%.2fs)" % (time.time() - start_time))
		#print("\nBuilding nodes list...")
		nodes_list = []
		for key, value in nodes_dict.items():
			nodes_list.append(value)

		# Calculate node frequencies using the unaggregated list of nodes
		for node in unaggregated_nodes_dict.values():
			for t in node['types']:
				if t == "Document" or t == "Instance":
					continue
				if t not in node_frequencies:
					node_frequencies[t] = 0
				node_frequencies[t] += 1

		if "Observation/Qualitative" in node_frequencies:
			node_frequencies["Observation/Qualitative/Testing"] = 1

		#print(node_frequencies)


		links_list = []
		for source in links_dict:
			for target in links_dict[source]:
				links_list.append(links_dict[source][target])



		for source in links_dict_a:

			for target in links_dict_a[source]:
				#print(source, target)
				links_list.append(links_dict_a[source][target])

		self.nodes = nodes_list
		self.links = links_list
		self.node_frequencies = node_frequencies
		self.total_documents = len(documents_set)

		self.get_node_class_tree(self.nodes, self.node_frequencies)


	# Retrieve the list of classes from a node query result
	def get_node_class_tree(self, data, node_classes):

		class_tree = OrderedDict({"Entity": {"children": {}}})
		#for node_class in sorted(node_classes.keys()):


		# Create the class tree.
		def nested_set(dic, parents, value, full_name, frequency):
			for parent in parents[:-1]:
				dic = dic[parent]["children"]

			dic[parents[-1]]["children"][value] = {
				"name": value,
				"full_name": full_name,
				"frequency": frequency,
				"children": {}
			}

		# A dict of all entity classes and their descendents
		class_children_dict = {} 
		for k, i in sorted(node_classes.items(), key=lambda x: x[1], reverse=True):
			#k, v = l
			s = k.split('/')
			parents = ["Entity"] + s[:-1]
			entity_class = s[-1]

			nested_set(class_tree, parents, entity_class, k, i)			
			for x in range(1, len(s)):
				parent = "/".join(s[:x])
				if parent not in class_children_dict:
					class_children_dict[parent] = set()
				class_children_dict[parent].add(k)
			

		for k in class_children_dict:
			class_children_dict[k] = list(class_children_dict[k])

		node_classes_list = sorted(node_classes,
			key = node_classes.get,
			reverse=True)

		self.class_tree = class_tree["Entity"]["children"]
		self.class_children_dict = class_children_dict


	def to_json(self):

		return {
			"totalDocuments": self.total_documents,
			"nodes": self.nodes,
			"links": self.links,
			"entityClasses": self.node_frequencies,
			"entityClassTree": self.class_tree,
			"entityClassChildren": self.class_children_dict,
			"structuredFields": self.structured_fields,
			"documentsName": self.documents_name
		}
