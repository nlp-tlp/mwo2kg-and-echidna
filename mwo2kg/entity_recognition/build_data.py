import jsonlines, random, copy

random.seed(123)

# Any docs with < min_agreement will not be included
min_agreement = 0.5

# A set of ignored labels, i.e. entity classes we are not interested in
# when building the knowledge graph.
ignored_labels = set(["Typo", "Unsure", "Abbreviation", "Spelling_error",
					  "Suggest_tag", "Identifier/Item_ID",
					  "Identifier", "Noise"])

# A dictionary containing simple mappings from classes in the NEW hierarchy back
# to the old one.
# i.e. "Observation/Observed_state" is replaced by "Observed_state".
label_mapping = {
 "Observation/Observed_state": "Observation",
 "Observation/Qualitative": "Observed_state",
 "Observation/Quantitative": "Observed_state",
 "Location/Absolute_loc": "Location",
 "Location/Relative_loc": "Location",
 "Consumable_or_commodity/Commodity": "Consumable",
 "Consumable_or_commodity/Consumable": "Consumable",
 "Consumable_or_commodity/Waste_biproduct": "Consumable",
 "Action/Function": "Observation",
 "Action/Malfunction": "Observation",
 "Attribute/Attribute_desc": "Attribute",
 "Attribute/Attribute_value": "Attribute",
 "Time/Relative_time": "Time",
 "Time/Absolute_time": "Time",
 "Observed_state": "Observation",
 "Identifier/Make": "Item",
 "Code": None,
 "Negation": None,
}

# A tuple containing the compound mappings from more than one entity class to
# another. For example, "Negation" + "Function" = "Observed_state".
# This is required to go from the NEW hierarchy back to the OLD one.
rule_mapping = (
	(("Negation", "Action/Function"),    ("Observation")),
	(("Negation", "Action/Malfunction"), ("Observation")),
	(("Speficier", "Item"), ("Item")),
	(("Action/Function", "Item"), ("Item")),
)



# A simple function to retrieve the first label of a mention that is NOT
# present in ignored_labels.
def get_mention_first_label(mention):
	labels = mention['labels']
	all_labels = [x for x in labels if x not in ignored_labels]
	first_label = all_labels[0] if len(all_labels) > 0 else None
	return first_label


def apply_compound_rules(mentions, rule_mapping):
	""" A complicated function that applies a list of compound rules to a list
	of mentions. The idea is that we want to translate the new hierarchy back
	into the old one prior to constructing the knowledge graph. i.e. rather than
	"Negation" + "Function", we want "Observed_state".
	
	Args:
	    mentions (TYPE): A list of mentions for a particular document
	    rule_mapping (TYPE): A tuple of tuples containing the compound entity
	    					 class mapped to a singular
	    					 entity class
	
	Returns:
	    list: mentions, the updated list of mentions
	"""
	new_mentions = []

	# Maintain a set of indices of mentions that are NOT present in any compound
	# rule
	mentions_in_rules = set()
	

	for i, m in enumerate(mentions):
		start = m['start']
		end = m['end']
		
		first_label = get_mention_first_label(m)
		if not first_label:
			continue

		
		# Check every rule in rule_mapping to see whether the mention contains a
		# rule. To do this, start at this particular mention, and search the
		# next n mentions (where n is the length of the rule).
		for rule in rule_mapping:

			lhs = rule[0]
			rhs = rule[1]
			joint_rule = True

			for j, entity_class in enumerate(lhs):
				if (i + j) >= len(mentions):
					break
				if get_mention_first_label(mentions[i + j]) != entity_class:					
					joint_rule = False
					break
				joint_rule_end = mentions[i + j]['end']

			if j >= 1 and joint_rule:
				new_mention = copy.deepcopy(m)
				new_mention['end'] = joint_rule_end
				new_mention['labels'] = [rhs]

				new_mentions.append(new_mention)
				mentions_in_rules.add(i)

				# print("Rule: %s" % " ".join(tokens))
				# print(mentions[i: i+j+1])
				# print(new_mention)
				# print()

		if i not in mentions_in_rules:
			new_mentions.append(m)

	return new_mentions

def convert_mentions_to_conll(json_file):
	""" Convert the mentions from Redcoat (which are in JSON format) to 
	CONLL-format, i.e. single-class Named Entity Recognition.
	
	Args:
	    json_file (string): The filename of the json file.
	
	Returns:
	    list: output_data: The output data
	    dict: label_counts: A dictionary containing the labels and their counts
	"""
	# Maintain a dict of (label, frequency) for printing
	label_counts = {}

	output_data = []

	removed_docs = 0
	with jsonlines.open(json_file, 'r') as f:

		for line in f:
			if 'annotator_agreement' in line and line['annotator_agreement'] \
			   < min_agreement:
				removed_docs += 1
				continue

			tokens = [t.lower() for t in line['tokens']]
			mentions = line['mentions']

			output_labels = ["O" for x in range(len(tokens))]

			# Before looking at each mention individually, we need to check the
			# rule_mapping for compound rules such as "negation" + "function" =
			# "observed_state"
			mentions = apply_compound_rules(mentions, rule_mapping)


			for m in mentions:
				start = m['start']
				end = m['end']

				first_label = get_mention_first_label(m)
				if not first_label:
					continue

				#all_labels = [x for x in labels if x not in ignored_labels]
				#if len(all_labels) == 0:
				#	continue
				#first_label = all_labels[0]
				if first_label in label_mapping:

					if label_mapping[first_label] is None:
						del m 
						continue
					first_label = label_mapping[first_label]

				for i in range(start, end):
					bio_tag = "B" if i == start else "I"
					output_labels[i] = bio_tag + '-' + first_label

				if first_label not in label_counts:
					label_counts[first_label] = 0
				label_counts[first_label] += 1

			output_data.append([*zip(tokens, output_labels)])

	print("Output data contains %d docs (%d removed due to low agreement)" % 
		  (len(output_data), removed_docs))
	return output_data, label_counts

# Save the dataset to the specified filename.
def save_dataset(dataset, dataset_name, output_folder):
	with open(output_folder + "/" + dataset_name + ".txt", 'w') as f:
		for tagged_sent in dataset:
			for (word, tag) in tagged_sent:
				f.write("%s %s\n" % (word, tag))
			f.write("\n")

# Save the test sentences (strings) to the corresponding file.
def save_test_sents(dataset):
	with open("data/processed/test_sents.txt", 'w') as f:
		for tagged_sent in dataset:
			f.write(" ".join(w[0] for w in tagged_sent))
			f.write('\n')

# Print a sorted list of labels and the number of times they appear in the
# processed data.
def print_label_counts(label_counts):
	print()
	print("Label counts: ")
	print('-' * 30)
	for (label, count) in sorted(label_counts.items(), 
								 key=lambda x: x[1], reverse=True):
		print("%s %s" % (label.ljust(20)[:20], count))
	print()


def build_data(train_filename, dev_filename, test_filename, output_folder):

	filenames = {
		"train": train_filename,
		"dev": dev_filename,
		"test": test_filename
	}

	# Run the script on each train, dev and test dataset.
	for dataset_name in ['train', 'dev', 'test']:		
		json_file = filenames[dataset_name]
		print("Building %s dataset... (%s)" % (dataset_name, json_file))

		output_data, label_counts = convert_mentions_to_conll(json_file)
		random.shuffle(output_data)
		save_dataset(output_data, dataset_name, output_folder)

		#if dataset_name == "test":
		#	save_test_sents(output_data)

		print_label_counts(label_counts)


if __name__=="__main__":
	build_data()