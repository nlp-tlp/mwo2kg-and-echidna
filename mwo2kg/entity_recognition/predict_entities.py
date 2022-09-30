import os

from flair.models import SequenceTagger
from flair.data import Sentence
import torch
import flair
from tqdm import tqdm

flair.device = torch.device('cuda')


class FlairTagger():
    def __init__(self):

        d = os.path.dirname(__file__)
        # flair.cache_root = d

        path = os.path.abspath(os.path.join(
            d, 'resources/taggers/maintenance-ner-flair/best-model.pt'))
        # print(path, "<<")
        # print(os.path.exists(path))
        self.model = SequenceTagger.load(path)

    def tag(self, tokens):
        sentence = Sentence(' '.join(tokens))
        self.model.predict(sentence)

        # d = sentence.to_dict(tag_type="ner")
        # print(sentence)
        # print(d)

        # s = sentence.to_tagged_string().split(' ')

        labels = []

        s = sentence.to_tagged_string().split()

        for t in s:  # This is horrible. Flair does not output the labels in the way we need, though, so this seems like the only option.
            if t.startswith("<B-") or t.startswith("<I-"):
                labels[-1] = t[1:-1]
            else:
                labels.append("O")

            # labels[d['start_pos']] = "B-%s" % d['type']
            # labels[d['start_pos'] + 1: d['end_pos']] = "I-%s" % d['type']

        # print(sentence.to_tagged_string())

        return labels

    def get_agg_score(self, input_sentence: str, verbose: bool = False) -> float:
        '''
            Gets the length normalised aggregate token confiddence for a single sentence.

            Notes
            -----
            Review required (09.09.21): Spans does not always equal number of tokens
        '''
        try:
            sentence = Sentence(input_sentence)
            self.model.predict(sentence)

            spans = sentence.get_spans('ner')
            span_scores = [entity.score for entity in spans]
            num_spans = len(spans)

            if num_spans == 0:
                # No predictions could be made (likely due to OOV issues)
                return float(0)
            else:
                agg_score = sum(span_scores)/num_spans
                if verbose:
                    print(spans, span_scores)

                assert agg_score <= 1
                return agg_score
        except Exception as e:
            print(
                f'Failed to process {input_sentence} (spans: {spans}) - error occurred: {e}')

    def __str__(self):
        return "Flair Tagger"


def predict_entities(input_filename, output_filename):

    tagger = FlairTagger()
    test_sents = []
    with open(input_filename, 'r') as f:
        for line in f:
            test_sents.append(line.strip())

    print(len(test_sents))
    # exit()

    with open(output_filename, 'w') as f:
        for i, sent in enumerate(test_sents):
            # print(sent)

            tokens = sent.split()
            labels = tagger.tag(tokens)

            # Empty strings will not be tagged correctly. Rather than get Flair to tag it, just insert an "(empty)" token with no label.
            if(len(tokens) == 0):
                f.write("%s %s\n\n" % ('(empty)', 'O'))
                continue

            for token, label in zip(tokens, labels):
                f.write("%s %s\n" % (token, label))

            f.write('\n')
            # print(i)


def confidence_sampler(input_filename: str, output_filename: str):
    '''
        Captures model prediction confidence and sorts texts from least to most confident.
    '''

    assert output_filename.split('.')[-1] == 'txt'

    tagger = FlairTagger()
    with open(input_filename, 'r', encoding="ISO-8859-1") as fr:
        # Note: this drop duplicates
        test_sents = list(set([line.strip() for line in fr.readlines()]))
        
    # Get scores
    scored_sents = [(sent, tagger.get_agg_score(
        input_sentence=sent, verbose=True)) for sent in test_sents]

    # Sort least to most confident
    scored_sents_sorted = sorted(
        scored_sents, key=lambda x: x[1], reverse=False)

    with open(output_filename, 'w') as fw:
        for sent, score in scored_sents_sorted:
            fw.write(f'{sent}|{score}\n')


if __name__ == "__main__":
    # Put your locations here or call from else where!
    input_filename = '/home/tyler/Desktop/Repos/nlp_tlp/t1-pipeline/mwo2kg/data/kalgoorlie_dataset.txt'
    output_filename = '/home/tyler/Desktop/Repos/nlp_tlp/t1-pipeline/mwo2kg/data/kalgoorlie_dataset_preds.txt'
    confidence_sampler(input_filename, output_filename)

    # predict_entities()
