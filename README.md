# MWO2KG

Code for constructing a knowledge graph from annotated maintenance work order data.

## Requirements

The main requirements are:

-   Python 3.6+
-   Neo4J Community Edition
-   NodeJS

Python package requirements are listed in `requirements.txt`. NodeJS requirements are listed in `client/package.json`.

## Installing the required packages

We recommend using virtual environments to run this code:

    python -m virtualenv venv
    venv\Scripts\activate

Python packages can be installed via:

    pip install -r requirements.txt

Please note that at this stage this file may not capture all Python package requirements (such as Flair) - I will update this shortly. For now, if any missing packages come up while running the script, you can simply install them via `pip`.

## Setting up the code

The Theme 1 Pipeline is shown below:

![alt text](https://github.com/nlp-tlp/t1-pipeline/blob/master/diagram.png?raw=true)

Rounded boxes represent data, and hard-edged boxes represent software. Green boxes are data required to run the pipeline, while white boxes are intermediate datasets that are produced as part of the pipeline.

The four required files under `data` are as follows:

-   mwos (.csv file). The csv file containing the work orders.
-   mwos_short_text (.txt file). A text file containing the short text fields of the same work orders as above, without any additional data. Each work order should appear on a new line.
-   ampla_data (.csv file). The CSV data containing the AMPLA data. The order must be the same as the above.
-   ner_training_data (.json file): The JSON data produced by Redcoat after annotating a set of work orders.

Note that at this stage, the following fields are required in the mwos csv file:

-   Work_Order_Functional_Location
-   Functional_Location_Description
-   Functional_Location_Sort_Field
-   ShortText

See `mwo2kg/sample_data/input/work_orders.csv` for examples of these fields.

<!-- The following two files are the output of the previous component of the pipeline:

- entity_hierarchy (.txt file). The list of entity classes present in the NER data.
- autolabelled_mwos_postprocessed (.json file). The postprocessed output corresponding to the above, which has been postprocessed to include aggregated entity class labels etc.
 -->

We have included a copy of some example data under the directory above. This data is publicly available data that we annotated within the NLP-TLP Group at UWA. The functional locations have been simulated, and the functional location sort field has been set to "AMSUL" for every work order.

### 1. Setting the config.ini file

Before running the pipeline you must modify `mwo2kg/config.ini` so that it points to the locations of each of the datasets necessary to run this tool.

### 2. Running Neo4J

Neo4J will need to be running prior to building the knowledge graph and running the web server. Open up Neo4J and create a new graph (if you haven't already), and start the database.

### 3. Setting the environment file

You must then create an environment file within the main folder of this repository, named `.env`. This file must contain:

    GRAPH_PASSWORD="(the Neo4J graph password)"

## Running the MWO2KG pipeline

The pipeline is located in `mwo2kg`:

    cd mwo2kg

The entire pipeline can be ran via:

    python run_pipeline.py

The modules that will be run are determined in the `config.ini` file:

    [OPTIONS]
    retrain_ner_model=True          # Whether to retrain the NER model.
                                    # Set "True" if you are building a new graph and have set "run_ner" = True below.
                                    # Set "True" if you are building a new graph and have never trained this model before.
    run_ner=True                    # Whether to run the Named Entity Recognition module.
    run_postprocessing=True         # Whether to run the postprocessing module.
    run_failure_mode_grouping=True  # Whether to run the failure mode grouping module. This will only work if you have
                                    # trained the failure mode grouping model once before (see below).
    run_triple_generation=True      # Whether to run the triple generation module.

To run the graph on the sample data, you can set everything above to `False` aside from `run_triple_generation` (which should be `True`), as I have already run the NER, Postprocessing and Failure Mode Grouping modules on the sample data.

### Training the Failure Mode Classification model

For some reason (no idea why), the Failure Mode Classification model must be trained separately and cannot be trained via `run_pipeline.py`. I tried doing it inside run_pipeline.py but kept getting OOM errors. If you can figure out why this is, please let me know! It is annoying to have to train it separately but it is what it is.

To train the failure mode classification model, navigate to:

    cd failure_mode_classification

And run the script:

    python train_failure_mode_classifier.py

Please note that before doing this, you'll need to paste the ISO15926 files into `mwo2kg/postprocessing/taxonomy`. They should be as follows:

    activities
        activity.csv
    attributes
        property.csv
    items
        basics.csv
        connection_material.csv

... and so on. Without these files, the classifier cannot be run. You can obtain them from the ISO15926 standard.

This will train a TextClassification model to predict a failure mode given an observation, e.g. 'fault' might be labelled as 'Electrical'.

Training this once is necessary to run `run_failure_mode_grouping=True` in the config.

If you do not run this, you will not see Observations broken down into failure mode codes (leak, electrical etc) in Echidna.

## Running Echidna

### Flask server

Then, to run the Flask server, navigate to the root directory of this repository and run `python run_app.py`:

    python run_app.py

The server will then be running on port 5000. Before you can view it, however, you must "build" the client.

### React client

To run the React client, you must first install the package requirements via `npm`. Navigate to `client` and run `npm install`.

    cd echidna_app/client
    npm install

Once this has been run once, you must "build" the client once also.

    npm run build

Now that the client has been built, navigate to 'http://localhost:5000' in your browser to access the web application.

Note that you only need to do this part once. For subsequent uses you can just run `python app.py` again as above - no need to rebuild the client again.

## Notes

Python 3.9 doesn't work with Flair, so you'll need to use Python 3.8.x.

We are currently working on revamping the source code - stay tuned for more updates.
