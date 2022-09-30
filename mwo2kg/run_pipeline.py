# run_pipeline.py
# Runs the entire MWO2KG pipeline in one go.
# @author M Stewart

import os
import configparser
import entity_recognition
import postprocessing
import triple_generation
import failure_mode_classification

def check_boolean(str):
	return True if str == "True" else False

def run_ner(data_folder, options, filenames):
	""" Run the NER component of the pipeline.
	Will not run if run_ner set to False in the config.
	Will only retrain the NER model if retrain_ner_model is True.
	"""
	if not check_boolean(options["run_ner"]):
		return

	ner_input_folder = os.path.join(data_folder, filenames["ner_input_folder"])
	ner_processed_folder = os.path.join(data_folder, filenames["ner_processed_folder"])
	ner_intermediate_folder = os.path.join(data_folder, filenames["ner_intermediate_folder"])

	if check_boolean(options["retrain_ner_model"]):
		entity_recognition.build_data(
			train_filename = os.path.join(ner_input_folder, filenames["ner_data_train"]),
			dev_filename   = os.path.join(ner_input_folder, filenames["ner_data_dev"]),
			test_filename  = os.path.join(ner_input_folder, filenames["ner_data_test"]),
			output_folder  = ner_processed_folder
		)
		entity_recognition.train_flair(
			data_folder = ner_processed_folder
		)

	entity_recognition.predict_entities(
		input_filename  = os.path.join(data_folder, filenames["mwos_short_text"]),
		output_filename = os.path.join(ner_intermediate_folder, filenames["autolabelled_mwos_conll"])
	)
	entity_recognition.results_to_json(
		input_filename  = os.path.join(ner_intermediate_folder, filenames["autolabelled_mwos_conll"]),
		output_filename = os.path.join(ner_intermediate_folder, filenames["autolabelled_mwos"])
	)

def run_postprocessing(data_folder, options, filenames):
	""" Run the postprocessing component of the pipeline,
	including the failure_mode_grouping model if run_failure_mode_grouping=True.
	"""
	if not check_boolean(options["run_postprocessing"]):
		return
	
	ner_intermediate_folder = os.path.join(data_folder, filenames["ner_intermediate_folder"])

	#if check_boolean(options["retrain_failure_mode_grouping_model"]):
	#	print("Training Failure Mode classifier...")
	#	failure_mode_classification.train_failure_mode_classifier()

	postprocessing.postprocess(
			input_filename = os.path.join(ner_intermediate_folder, filenames["autolabelled_mwos"]),
			output_filename = os.path.join(ner_intermediate_folder, filenames["autolabelled_mwos_postprocessed"]),
			output_filename_hierarchy = os.path.join(ner_intermediate_folder, filenames["entity_hierarchy"]),
			run_failure_mode_grouping = check_boolean(options["run_failure_mode_grouping"])
	)

def run_triple_generation(data_folder, options, filenames):
	""" Run the triple generation component of the pipeline.
	"""
	if not check_boolean(options["run_triple_generation"]):
		return

	ner_intermediate_folder = os.path.join(data_folder, filenames["ner_intermediate_folder"])

	triple_generation.build_triples(
		ner_input_filename = os.path.join(ner_intermediate_folder, filenames["autolabelled_mwos_postprocessed"]),
		mwo_input_filename = os.path.join(data_folder, filenames["mwos"]),
		entity_hierarchy_input_filename = os.path.join(ner_intermediate_folder, filenames["entity_hierarchy"]),
		ampla_data_filename = os.path.join(data_folder, filenames['ampla_data']) if 'ampla_data' in filenames else None
	)

def main():

	config = configparser.ConfigParser()
	config.read('config.ini')

	filenames = config["FILENAMES"]
	options   = config["OPTIONS"]

	data_folder = filenames["data_folder"]

	run_ner(data_folder, options, filenames)
	run_postprocessing(data_folder,options, filenames)
	run_triple_generation(data_folder, options, filenames)


if __name__=="__main__":
	main()