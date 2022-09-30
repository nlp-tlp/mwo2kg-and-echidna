# NER for Maintenance

This repository contains code for training a Named Entity Recognition model on Maintenance Work Orders. 

## Repository structure

    /data                         The data to train and evaluate the model.
      /input                      Contains the input data.
         /annotations_all.json    The input data file.
      /output                     Contains the output data.
         /redcoat_curator_data    The output folder. Data can be pasted into Redcoat Curator to visualise the results.
      /processed                  The CONLL-formatted data, required to train NER models.      
    /resources                    Contains the trained Flair model.
    build_data.py                 A simple script for converting annotations_all.json into CONLL format.
    evaluate.py                   Code for evaluating the trained Flair model on the evaluation data.
    save_results_for_curator.py   Code for transforming the CONLL-formatted outputs into JSON so that it can be visualised via Redcoat Curator.
    train_flair.py                Code for training the model on the data contained within /conll_format.

## Usage

First, save the input dataset as `/data/input/annotations_all.json`. This input dataset must be formatted for mention-level entity typing, i.e. each line will look as follows:

    {"doc_idx":136,"annotator_agreement":0.9466666666666667,"tokens":["jacks","won","\"","t","work."],"mentions":[{"start":0,"end":1,"labels":["Item"]},{"start":0,"end":1,"labels":["Item"]},{"start":1,"end":2,"labels":["Observation","Observation/Observed_state"]},{"start":1,"end":3,"labels":["Observation","Observation/Observed_state"]},{"start":1,"end":4,"labels":["Observation","Observation/Observed_state"]},{"start":1,"end":5,"labels":["Observation","Observation/Observed_state"]}]}

This data will typically come directly from Redcoat. In this repository, `annotations_all.json` is the combined labels from our MWO Tagging Project.

The next step is to convert this JSON data into CONLL data. This is required because the Flair model can read CONLL-formatted data, but not JSON. Simply run the `build_data.py` file to transform it into CONLL - it will be saved under `/data/processed/ner_data`:

    python build_data.py

Note that the `min_agreement` variable in this file allows you to specific the minimum annotator agreement to include in the dataset. Any docs with lower than `min_agreement` will be removed.

We are now ready to train the model: `train_flair.py`:

    python train_flair.py

After some time, the F1-Score of the model will be shown and the training will end. Using the dataset provided here, the result is an F1-Score of approximately 0.85.

The next step is to use this trained Flair model to predict the entity types of the test data, i.e. the data we do not necessarily have labels for. This data should be placed under `/data/input/test_sents.txt`, where each line is a single sentence. For example, the first three lines might look like this:

    rebuild drill steels
    load roller holes cracked in track frame
    replace manufacturer30 battery ITEM_ID
    
Then, run the `evaluate.py` script to predict the entity types contained within these sentences:

    python evaluate.py
    
The results will be saved to `/data/output/test_sents_preds.txt`, in CONLL format.

These results can already be used as-is, but it is nice to be able to visualise them against the ground truth labels. To do this, run `save_results_for_curator.py` to convert these CONLL-formatted sentences back into JSON:

    python save_results_for_curator.py
    
The results will be saved to `/data/output/redcoat_curator_data`. You can use the Redcoat Curator Tool (available on the ITTC Gitlab or on Github) to visualise the results of the Flair Model against the original ground truth labels, if they are available. Simply paste the JSON files from `/data/output/redcoat_curator_data` into the `/data` folder of the Redcoat Curator tool (further instructions are available in the Redcoat Curator repository).

This will provide a nice visualisation of the results, e.g:

![Results](/results_example.png?raw=true "Results example")

## Results

The best observed results are below:

    MICRO_AVG: acc 0.7532 - f1-score 0.8592
    MACRO_AVG: acc 0.7432 - f1-score 0.84459
    Activity   tp: 193 - fp: 5 - fn: 5 - tn: 193 - precision: 0.9747 - recall: 0.9747 - accuracy: 0.9507 - f1-score: 0.9747
    Agent      tp: 20 - fp: 0 - fn: 1 - tn: 20 - precision: 1.0000 - recall: 0.9524 - accuracy: 0.9524 - f1-score: 0.9756
    Attribute  tp: 3 - fp: 2 - fn: 1 - tn: 3 - precision: 0.6000 - recall: 0.7500 - accuracy: 0.5000 - f1-score: 0.6667
    Cardinality tp: 5 - fp: 1 - fn: 0 - tn: 5 - precision: 0.8333 - recall: 1.0000 - accuracy: 0.8333 - f1-score: 0.9091
    Consumable tp: 16 - fp: 4 - fn: 5 - tn: 16 - precision: 0.8000 - recall: 0.7619 - accuracy: 0.6400 - f1-score: 0.7805
    Item       tp: 358 - fp: 94 - fn: 81 - tn: 358 - precision: 0.7920 - recall: 0.8155 - accuracy: 0.6717 - f1-score: 0.8036
    Location   tp: 102 - fp: 14 - fn: 11 - tn: 102 - precision: 0.8793 - recall: 0.9027 - accuracy: 0.8031 - f1-score: 0.8908
    Observation tp: 111 - fp: 17 - fn: 22 - tn: 111 - precision: 0.8672 - recall: 0.8346 - accuracy: 0.7400 - f1-score: 0.8506
    Specifier  tp: 11 - fp: 2 - fn: 1 - tn: 11 - precision: 0.8462 - recall: 0.9167 - accuracy: 0.7857 - f1-score: 0.8800
    Time       tp: 5 - fp: 2 - fn: 2 - tn: 5 - precision: 0.7143 - recall: 0.7143 - accuracy: 0.5556 - f1-score: 0.7143
