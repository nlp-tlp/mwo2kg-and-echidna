import csv
import json
import configparser
import os
import sys
import pathlib

try:
	from flair.models import TextClassifier
	from flair.data import Sentence
except:
	print("WARNING: Flair is not installed. Running Failure mode classifier will not work.")

from utils import LexicalNormaliser

import jsonlines
from nltk.stem import WordNetLemmatizer

CURRENT_PATH = current_path = pathlib.Path(__file__).parent.resolve()

taxonomy_folders = {
	"Item": {
		"folder": 'taxonomy/items',
	},
	"Activity": {
		"folder": 'taxonomy/activities',		
		#"lemmatize": True,
		#"pos_type": "v"
	},
}

MAX_DEPTH = 3
MAX_ROWS = 100000

def classify_failure_mode(text, context, failure_mode_classifier):
	#sent = Sentence(text.replace('_', " ").lower() + " " + context)
	sent = Sentence(text.replace('_', " ").lower()) # + " " + context)
	#print(sent)
	failure_mode_classifier.predict(sent)
	return sent.labels[0].to_dict()['value'].replace("/", "or")


def adjust_labels_of_mention(text, labels, d, context, failure_mode_classifier = None):
	new_labels = [] #labels[:]
	new_observation_labels = []
	if(len(text) == 0): return
	for l in labels:

		if l == "Observation" and failure_mode_classifier:
			# Classify via Flair
			new_observation_label = "Observation/" + classify_failure_mode(text, context, failure_mode_classifier)
			if new_observation_label not in new_observation_labels:
				new_observation_labels.append(new_observation_label)
			#if 'leak' in text:
			print(text.replace('_', ' ').lower(), "X", context)
			print(new_observation_label)
			print()
			continue

		if l in d:
			x = text

			if l == "Activity":
				found = False
				for cat in d[l]:							
					if x in cat or cat.lower().replace("_", " ") in x.lower().replace("_", " "):
						new_labels.append(d[l][cat])
						found = True
						break								
				if not found:
					new_labels.append("Uncategorised")
			else:
				if x not in d[l]:
					x = text.split("_")[-1] # Check the last word, e.g. 'hydraulic pump' could be a type of pump
					if x not in d[l]:
						labels.append(l + "/Uncategorised")
						break

				new_labels.append(x)						
				# Check through the dictionary to build up a list of parents
				while x in d[l]:						
					x = d[l][x]				
					if x in new_labels:
						break # prevent loops
					if x != "Activity":
						new_labels.append(x)					
			
			# Reverse the list and add all the categorised to the labels list
			c = [l]
			i = 0

			for n in new_labels[::-1]:
				if i > MAX_DEPTH:
					continue
				#print(new_labels[-1])
				if l == "Activity" and i == 1:
					continue
				c.append(n)
				labels.append("/".join(c))
				i += 1

	for ol in new_observation_labels:
		labels.append(ol)

def normalise_row(row, lexical_normaliser):
	tokens = lexical_normaliser.normalise(row['tokens'])
	row['tokens'] = tokens
	return row

def postprocess_data(data_file, d, output_file, failure_mode_classifier = None):

	lexical_normaliser = LexicalNormaliser()

	data = []	
	with jsonlines.open(data_file, 'r') as f:
		for line in f:
			data.append(line)

	postprocessed_data = []
	for row in data[:MAX_ROWS]:

		# TODO: Normalise
		#row = normalise_row(row, lexical_normaliser)

		mentions = row['mentions']
		tokens   = row['tokens']

		for m in mentions:
			start = m['start']
			end = m['end']
			labels = m['labels']
			if "Typo" in labels:
				labels.remove("Typo")
			if len(labels) == 0:
				mentions.remove(m)
				if len(mentions) == 0:
					del mentions
					break
				continue

			mention_text_1 = " ".join(tokens[start:end])

			mention_text_2 = lexical_normaliser.normalise_text(mention_text_1)
			mention_text_3 = mention_text_2.lower().replace(" ", "_").title()

			#print("%s, %s, %s" % (mention_text_1, mention_text_2, mention_text_3))

			#text = "_".join([t.replace(" ", "_") for t in tokens[start:end]]).title()
			#print(text)
			labels = adjust_labels_of_mention(mention_text_3, labels, d, " ".join(tokens), failure_mode_classifier)

			
		postprocessed_data.append(row)

	with jsonlines.open(output_file, 'w') as f:
		for row in postprocessed_data:
			f.write(row)
	print("Postprocessed data saved to %s" % output_file)
	return postprocessed_data

class Hierarchy:

	def __init__(self):
		self.categories = {}

	def add_category(self, category):
		s = category.split('/')
		cc = self.categories
		for i, c in enumerate(s):
			#for j in s[:i]:
			a = "/".join(s[:i + 1])
			if a not in cc:
				cc[a] = {}
			cc = cc[a]
			#self.categories.setdefault(j, "/".join(s[:i]))


		

	def save_to_file(self, output_file):

		lines = []
		# https://stackoverflow.com/questions/3860813/recursively-traverse-multidimensional-dictionary-dimension-unknown
		def walk_dict(d, depth=0):
			for k,v in sorted(d.items(),key=lambda x: x[0]):
				if isinstance(v, dict) and len(v.keys()) > 0:
					lines.append((" " * depth) + k)
					walk_dict(v,depth+1)
				else:
					lines.append((" ") * depth + k) 

		walk_dict(self.categories)

		with open(output_file, 'w') as f:
			f.write("\n".join(lines))
		

def build_hierarchy(data, output_file):
	hierarchy = Hierarchy()

	for row in data:
		for m in row['mentions']:
			for l in m['labels']:
				hierarchy.add_category(l)

	hierarchy.save_to_file(output_file)
	return hierarchy


def build_dictionary():
	d = {}
	lemmatizer = WordNetLemmatizer()

	for entity_class, cf in taxonomy_folders.items():
		d[entity_class] = {}
		folder = cf['folder']
		lemmatize = cf['lemmatize'] if 'lemmatize' in cf else False
		single_words_only = cf['single_words_only'] if 'single_words_only' in cf else False
		if lemmatize:
			pos_type = cf['pos_type']
		for filename in os.listdir(os.path.join(CURRENT_PATH, folder)):
			
			if not filename.endswith('.csv'): continue
			with open(os.path.join(CURRENT_PATH, '%s/%s' % (folder, filename)), 'r') as f:
				reader = csv.DictReader(f)
				print(filename)
				print("----")
				for row in reader:
					child = row['Unique name']
					parent = row['superclass 1']

					

					if parent == "physical object":
						parent = filename.title()[:-4]
						#print(parent)
					#if filename == "heat_transfer.csv":
					#	print(parent, child)
					if single_words_only:
						if " " in child or " " in parent:
							if filename == "heat_transfer.csv":
								print(child, parent, "<<<")
							continue
					if lemmatize:
						child = lemmatizer.lemmatize(child, pos_type)
						parent = lemmatizer.lemmatize(parent, pos_type)

					child = child.title().replace(" ", "_")
					parent = parent.title().replace(" ", "_")

					# if filename == "heat_transfer.csv":
					# 	print(parent, child)
					
					d[entity_class][child] = parent
	#exit()
	#print(d["Item"]["Air_Conditioner"])
	return d

def postprocess(input_filename, output_filename, output_filename_hierarchy, run_failure_mode_grouping = True):

	current_path = pathlib.Path(__file__).parent.resolve()

	flair_classifier = None
	if run_failure_mode_grouping:
		try:
			flair_classifier = TextClassifier.load(os.path.join(CURRENT_PATH.parent, 'failure_mode_classification/resources/taggers/failure-mode-classifier/final-model.pt'))
		except FileNotFoundError:
			print("Error: the failure mode classification model was not found. Please check the README for how to train it.")
			exit()


	d = build_dictionary()
	#with open('test.txt', 'w') as f:
	#	f.write(json.dumps(d, indent = 1))
	postprocessed_data = postprocess_data(input_filename, d, output_filename, flair_classifier)

	print(len(postprocessed_data))
	hierarchy = build_hierarchy(postprocessed_data, output_filename_hierarchy)


if __name__ == "__main__":
	main()