"""
queries.py
@author Michael Stewart

Contains queries for interacting with Neo4j.
"""


def document_query(where_clause):
	return '\
		MATCH (d:Document)<-[a:APPEARS_IN]-(n1:Instance)<-[r]-(n2:Instance)-[:APPEARS_IN]->(d)' + where_clause + '\
		RETURN  DISTINCT \
				ID(d)  as id_d, LABELS(d) as types_d, d.tokens as tokens, d.doc_id as doc_id, \
				ID(n1) as id_1, n1.name as name_1, LABELS(n1) as types_1, \
				ID(n2) as id_2, n2.name as name_2, LABELS(n2) as types_2, \
				ID(r)  as id_r, r.frequency as frequency, type(r) as link_name, \
				ID(a)  as id_a, type(a) as link_name_a'

def floc_query(where_clause):
	return '\
		MATCH (d:Document)<-[a:APPEARS_IN]-(f1:FLOC)-[r:SCO]->(f2:FLOC)-[:APPEARS_IN]->(d)' + where_clause + '\
		RETURN  DISTINCT \
			ID(f1) as id_f1, f1.name as name_f1, f1.sort_field_name as sort_field_name_f1, LABELS(f1) as types_f1,\
			ID(r) as id_r, type(r) as link_name_r,\
			ID(f2) as id_f2, f2.name as name_f2, f2.sort_field_name as sort_field_name_f2, LABELS(f2) as types_f2'

def ampla_query():
	return '\
		MATCH (x:FLOC)-[r:HAS_AMPLA_EVENT]-(am:AMPLA_Event)\
	 	RETURN DISTINCT\
	 		ID(x)  as id_x, \
	 		ID(r) as id_r, type(r) as link_name_r, \
	 		ID(am) as id_am, am.name as name_am, LABELS(am) as types_am, am.effective_duration as effective_duration, am.lost_feed as lost_feed'

def build_query(queries, structured_fields):
	where_clause = '\n'
	structured_fields_dict = {
		d['name']: d for d in structured_fields
	}
	#print(queries)
	for query_field in queries:
		#print('{', query_field, "'....", structured_fields_dict)
		if query_field not in structured_fields_dict:
			continue
		field_type = structured_fields_dict[query_field]['type']

		if where_clause == "\n":
			where_clause += "\nWHERE"
		else:
			where_clause += "\nAND"

		if field_type == "Date":
			earliest = queries[query_field]['earliest']
			latest = queries[query_field]['latest']
			earliest_date_str = '{year:%s, month:%s, day:%s}' % (earliest['year'], earliest['month'], earliest['day'])
			latest_date_str =   '{year:%s, month:%s, day:%s}' % (latest['year'], latest['month'], latest['day'])			
			where_clause += ' date(%s) <= d.%s <= date(%s)\n' % (earliest_date_str, query_field, latest_date_str)
		if field_type == "Categorical":
			where_clause += ' d.%s CONTAINS "%s"\n' % (query_field, queries[query_field]['value'])
		if field_type == "Integer":
			where_clause += ' d.%s >= %d AND d.%s <= %d' % (query_field, int(queries[query_field]['value']['min']), query_field, int(queries[query_field]['value']['max']))

	return where_clause