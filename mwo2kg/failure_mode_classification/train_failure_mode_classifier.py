from flair.datasets import CSVClassificationCorpus
from flair.data import Sentence
from flair.embeddings import WordEmbeddings, FlairEmbeddings, PooledFlairEmbeddings, DocumentRNNEmbeddings
from typing import List
from flair.models import TextClassifier
import torch


import pathlib, os


def train_failure_mode_classifier():
  current_path = pathlib.Path(__file__).parent.resolve()
  #
  # 2. what tag do we want to predict?
  column_name_map = {1: "label_failure_mode", 0: 'text'}


  data_folder = os.path.join(current_path, 'input_data')

  corpus: Corpus = CSVClassificationCorpus(data_folder, column_name_map,
                                delimiter=",",
                                )





  # 2. create the label dictionary
  label_dict = corpus.make_label_dictionary()


  # 4. initialize embeddings
  word_embeddings = [

      #FlairEmbeddings('resources/taggers/geo_language_model/best-lm.pt')

      # comment in this line to use character embeddings
      #CharacterEmbeddings(),
      #BertEmbeddings(),

      # comment in these lines to use flair embeddings
      PooledFlairEmbeddings('mix-forward'),
      PooledFlairEmbeddings('mix-backward'),
  ]


  document_embeddings = DocumentRNNEmbeddings(word_embeddings, hidden_size=512)
  #document_embeddings = TransformerDocumentEmbeddings('distilbert-base-uncased', fine_tune=True)

  #embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)

  # 5. initialize sequence tagger


  tagger: TextClassifier = TextClassifier(
                                          document_embeddings,
                                          label_dictionary=label_dict,
                                          )

  # 6. initialize trainer
  from flair.trainers import ModelTrainer

  trainer: ModelTrainer = ModelTrainer(tagger, corpus)

  # 7. start training
  trainer.train(os.path.join(current_path, 'resources/taggers/failure-mode-classifier'),
                learning_rate=0.1,
                mini_batch_size=32,
                #anneal_factor=0.5,
                max_epochs=20,
                patience=5,
                embeddings_storage_mode='gpu')

  # 8. plot weight traces (optional)
  from flair.visual.training_curves import Plotter
  plotter = Plotter()
  plotter.plot_weights(os.path.join(current_path, 'resources/taggers/failure-mode-classifier/weights.txt'))


def test_failure_mode_classifer():


	model = TextClassifier.load('resources/taggers/failure-mode-classifier/final-model.pt')

	test_sents = []
	with open('input_data/test.txt', 'r') as f:
		for line in f:
			phrase = line.split(',')[0].strip()
			label = line.split(',')[1].strip()
			test_sents.append({ 'input': phrase, 'ground_truth': label})

	for sent in test_sents:
		s = Sentence(sent['input'])
		model.predict(s)


		label = str(s.labels[0]).split(' (')[0]
		conf = str(s.labels[0]).split(' (')[1].split(')')[0]

		sent['prediction'] = label
		sent['confidence'] = conf

	with open('output.csv', 'w') as f:
		f.write(','.join(test_sents[0].keys()))
		f.write('\n')
		for sent in test_sents:
			f.write(','.join(sent.values()))
			f.write('\n')



if __name__=="__main__":
	#train_failure_mode_classifier()
	test_failure_mode_classifer()