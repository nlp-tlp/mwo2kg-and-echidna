# Retrieve the list of classes from a node query result
def get_node_classes(data):
	node_classes = {}
	for d in data:
		for t in d['types']:
			if t == "Document" or t == "Instance":
				continue
			if t not in node_classes:
				node_classes[t] = 0
			node_classes[t] += 1

	print(node_classes)

	class_tree = {}
	#for node_class in sorted(node_classes.keys()):


	for k in sorted(node_classes.keys()):
		#k, v = l
		*f, l = k.split('/')

		t = class_tree
		if len(f) == 0:
			class_tree[k] = {}
		else:
			for k in f:
				t = t.setdefault(k, {})
		#t[l] = int(v)   # don't perform a conversion if your values aren't numeric

	print(class_tree)


	node_classes_list = sorted(node_classes, key = node_classes.get, reverse=True)
	return node_classes_list