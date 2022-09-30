class DictionaryTagger:

	def __init__(self, hierarchy):
		self.hierarchy = hierarchy
		self.entity_classes = self.get_entity_classes(hierarchy.entity_classes)


	# Returns a mapping from each entity class to its position in the hierarchy, 
	# e.g. { 'arm': X} because ['body_part', 'arm'] is at position X in the hierarchy.
	def get_entity_classes(self, hierarchy):
		entity_class_mapping = {h.name : i for i, h in enumerate(hierarchy)}
		return entity_class_mapping

	# Tag the paragraph automatically using the lexicon.
	# To be used to train a model.
	def tag(self, tokens):
		mentions = []

		max_ngram_size=5

		for w in range(1, max_ngram_size + 1):

			for i in range(0, len(tokens) - w + 1):
				window = [str(t) for t in tokens[i:i+w]]

				#print(window)

				if "_".join(window) in self.entity_classes:
					mentions.append({'start': i, 'end': i + w, 'labels': [self.hierarchy.entity_classes[self.entity_classes["_".join(window)]]]})




		#for i, t in enumerate(tokens):
		#	if t in self.entity_classes:
		#		mentions.append({'start': i, 'end': i + 1, 'labels': [self.hierarchy.entity_classes[self.entity_classes[t]]]})

		# Clean up mentions to remove nested tags from the same part of the tree, e.g. "left leg" and "leg" should just be "left leg" because leg is longer

		invalid_mentions = set()
		for m in mentions:
			m_split = m['labels'][0].name.split('_')
			if len(m_split) <= 1:
				continue
			for m2 in mentions:
				m2_split = m2['labels'][0].name.split('_')				
				if len(m2_split) >= len(m_split):
					continue
				if m2['start'] >= m['start'] and m2['end'] <= m['end']:

					invalid_mentions.add(m2['labels'][0].name)					

		#if len(invalid_mentions) > 0:
		#	print(invalid_mentions)

		return [m for m in mentions if m['labels'][0].name not in invalid_mentions]

	def __str__(self):
		return "Dictionary Tagger"
	