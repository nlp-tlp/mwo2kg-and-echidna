from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import ELMoEmbeddings, TokenEmbeddings, WordEmbeddings, TransformerWordEmbeddings, FastTextEmbeddings, StackedEmbeddings, FlairEmbeddings, CharacterEmbeddings
from typing import List

import pathlib, os


columns = {0: 'text', 1: 'ner'}


EXPERIMENT_LIST = ["flair"], #"gpt", "roberta", "distilbert", "albert"]


EMBEDDING_TYPES = {
  'flair': [
    FlairEmbeddings('mix-forward'),
    FlairEmbeddings('mix-backward'),
  ],
  # 'bert': [
  #   TransformerWordEmbeddings('bert-base-uncased'),
  # ],
  # 'gpt': [
  #   TransformerWordEmbeddings('gpt2')
  # ],
  # 'roberta': [
  #   TransformerWordEmbeddings('roberta-base')
  # ],  
  # 'distilbert': [
  #   TransformerWordEmbeddings('distilbert-base-uncased')
  # ],
  # 'albert': [
  #   TransformerWordEmbeddings('albert-base-v2')
  # ],
  # 'glove': [
  #   WordEmbeddings('glove'),
  # ],
  # 'elmo': [
  #   ELMoEmbeddings(),
  # ],
}


def run_training(corpus, tag_dictionary, embedding_model):

  current_path = pathlib.Path(__file__).parent.resolve()

  print("Running model with %s embeddings" % embedding_model)

  # 4. initialize embeddings
  embedding_types: List[TokenEmbeddings] = EMBEDDING_TYPES[embedding_model]

  # [

  #     #FlairEmbeddings('resources/taggers/geo_language_model/best-lm.pt')

  #     # comment in this line to use character embeddings
  #     #CharacterEmbeddings(),
  #     #BertEmbeddings(),

  #     # comment in these lines to use flair embeddings
  #     FlairEmbeddings('mix-forward'),
  #     FlairEmbeddings('mix-backward'),
  # ]

  embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)

  # 5. initialize sequence tagger
  from flair.models import SequenceTagger

  tagger: SequenceTagger = SequenceTagger(hidden_size=256,
                                          embeddings=embeddings,
                                          tag_dictionary=tag_dictionary,
                                          tag_type='ner',
                                          use_crf=True)

  # 6. initialize trainer
  from flair.trainers import ModelTrainer

  trainer: ModelTrainer = ModelTrainer(tagger, corpus)

  # 7. start training
  trainer.train(os.path.join(current_path, 'resources/taggers/maintenance-ner-%s' % embedding_model),
                learning_rate=0.1,
                mini_batch_size=32,
                max_epochs=150,
                embeddings_storage_mode='gpu')

  # 8. plot weight traces (optional)
  from flair.visual.training_curves import Plotter
  plotter = Plotter()
  plotter.plot_weights(os.path.join(current_path, 'resources/taggers/maintenance-ner-%s/weights.txt' % embedding_model))

  with open(os.path.join(current_path, 'resources/taggers/maintenance-ner-%s/training.log' % embedding_model), 'r') as f:
    results_output = []
    in_results = False
    for line in f:
      if line.startswith("Results:"):
        in_results = True
      if in_results:
        results_output.append(line)




  print("Writing scores to results/%s.txt" % embedding_model)
  with open(os.path.join(current_path, 'results/%s.txt' % embedding_model), 'w') as f:
    for line in results_output:
      f.write(line)

def train_flair(data_folder):

  # Initialise tte corpus
  corpus: Corpus = ColumnCorpus(data_folder, columns,
                              train_file='train.txt',
                              dev_file='dev.txt',
                              test_file='test.txt')

  # make the tag dictionary from the corpus
  tag_dictionary = corpus.make_tag_dictionary(tag_type='ner')

  #for exp in EXPERIMENT_LIST:
  #  run_experiment(exp)
  run_training(corpus, tag_dictionary, 'flair')


if __name__=="__main__":
  train_flair()