import csv
import pathlib
import os

CURRENT_PATH = current_path = pathlib.Path(__file__).parent.resolve()

class LexicalNormaliser:
	def __init__(self, gazetteer_filename = None):		

		if gazetteer_filename is None:
			gazetteer_filename = os.path.join(CURRENT_PATH, 'gazetteers/corrections.csv')

		self.replacement_dictionary = {}
		with open(gazetteer_filename, 'r') as f:
			reader = csv.reader(f)
			for row in reader:
				self.replacement_dictionary[row[0]] = row[1].strip()


	def normalise_text(self, text):
		if text in self.replacement_dictionary:
			text = self.replacement_dictionary[text]
		text = text.strip('.').strip('-')
		if text.endswith('s') and len(text) > 1 and text[-2] != 's':
			text = text[:-1]

		if text in self.replacement_dictionary:
			text = self.replacement_dictionary[text]

		final_text = []
		for word in text.split():
			if word in self.replacement_dictionary:
				final_text.append(self.replacement_dictionary[word])
			else:
				final_text.append(word)

		return ' '.join(final_text)

	def normalise(self, document):
		def normalise_token(t):
			t = t.strip('.').strip('-')
			if t in self.replacement_dictionary:
				t = self.replacement_dictionary[t]
			#t = self.stemmer.stem(t)
			return t

		print(document)
		normalised_sent = [normalise_token(t) for t in document]
		print(normalised_sent)
		print('--')
		
		return normalised_sent