import configparser
import jsonlines

config = configparser.ConfigParser()
config.read('../config.ini')

# Convert the results into JSON format so that it can be visualised via Redcoat Curator. 

#test_ground_truth = 'data/processed/ner_data/test.txt'

def conll2json(tagged_sents):
	json_sents = []
	for sent_index, sent in enumerate(tagged_sents):
		json_sent = {}

		tokens = [w[0] for w in sent]

		json_sent['tokens'] = tokens
		json_sent['mentions'] = []
		json_sent['doc_idx'] = sent_index #[" ".join(tokens)]
		current_label = "O"

		current_label = ""
		mention_start = -1
		for i, (word, tag) in enumerate(sent):
			bio_tag = tag[0]
			
			
			if mention_start >= 0 and (bio_tag in ["B", "O"]):
				json_sent['mentions'].append({
					'start': mention_start,
					'end': i,
					'labels': [current_label]
				})
				mention_start = -1
				current_label = ""

			if bio_tag == "B":
				mention_start = i
				current_label = tag[2:]

			if i == (len(sent) - 1) and mention_start >= 0:
				json_sent['mentions'].append({
					'start': mention_start,
					'end': i + 1,
					'labels': [current_label]
				})
		json_sents.append(json_sent)



	return json_sents



def load_dataset(filename):

	tagged_sents = []

	with open(filename, 'r') as f:
		dataset = f.read().strip().split("\n\n")
		for sent in dataset:
			tagged_sents.append([])
			for word_and_tag in sent.strip().split("\n"):
				word, tag = word_and_tag.split()
				tagged_sents[-1].append((word, tag))
	
	return tagged_sents

def results_to_json(input_filename, output_filename):


	#tagged_sents_gt    = load_dataset(test_ground_truth)
	tagged_sents_preds = load_dataset(input_filename)

	#json_gt = conll2json(tagged_sents_gt, sent_indexes)
	json_preds = conll2json(tagged_sents_preds)

	#with jsonlines.open(REDCOAT_INPUT_FOLDER + 'ground_truth.json', 'w') as writer:
	#	for row in json_gt:
	#		writer.write(row)

	with jsonlines.open(output_filename, 'w') as writer:
		for row in json_preds:
			writer.write(row)

if __name__=="__main__":
	results_to_json()