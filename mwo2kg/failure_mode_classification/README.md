# Failure mode classification

Some experimental code for classifying observations in the knowledge graph into predefined failure mode codes from ISO14224.

## Current results

	Results:
	- F-score (micro) 0.6316
	- F-score (macro) 0.2929
	- Accuracy 0.6316

	By class:
	                             precision    recall  f1-score   support

	              Spurious stop     0.0000    0.0000    0.0000         0
	                High output     0.0000    0.0000    0.0000         1
	                  Breakdown     0.8571    0.6667    0.7500         9
	         Not an observation     0.6667    0.9231    0.7742        26
	      Structural deficiency     0.9091    0.8333    0.8696        12
	                      Other     0.0000    0.0000    0.0000         8
	                 Electrical     0.5000    0.6667    0.5714         3
	           Plugged / choked     0.6667    0.3333    0.4444         6
	                 Low output     0.0000    0.0000    0.0000         4
	                    Leaking     1.0000    0.5000    0.6667         8
	Abnormal instrument reading     0.0000    0.0000    0.0000         0
	 Failure to start on demand     0.0000    0.0000    0.0000         2
	  Minor in-service problems     0.5263    1.0000    0.6897        10
	  Failure to stop on demand     0.0000    0.0000    0.0000         3
	                Overheating     1.0000    0.6667    0.8000         3
	              Contamination     0.0000    0.0000    0.0000         0
	                  Vibration     0.0000    0.0000    0.0000         0
	                      Noise     0.0000    0.0000    0.0000         0
	             Erratic output     0.0000    0.0000    0.0000         0

	                  micro avg     0.6316    0.6316    0.6316        95
	                  macro avg     0.3224    0.2942    0.2929        95
	               weighted avg     0.6076    0.6316    0.5929        95
	                samples avg     0.6316    0.6316    0.6316        95


Old results (need to find out why these results are weird. I think the split was different before).


	MICRO_AVG: acc 0.6015 - f1-score 0.7512
	MACRO_AVG: acc 0.2013 - f1-score 0.2625722222222222
	Abnormal instrument reading tp: 0 - fp: 3 - fn: 0 - tn: 210 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Breakdown  tp: 128 - fp: 17 - fn: 2 - tn: 66 - precision: 0.8828 - recall: 0.9846 - accuracy: 0.8707 - f1-score: 0.9309
	Contamination tp: 0 - fp: 1 - fn: 0 - tn: 212 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Electrical tp: 5 - fp: 1 - fn: 1 - tn: 206 - precision: 0.8333 - recall: 0.8333 - accuracy: 0.7143 - f1-score: 0.8333
	Erratic output tp: 0 - fp: 0 - fn: 0 - tn: 213 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Failure to start on demand tp: 1 - fp: 1 - fn: 0 - tn: 211 - precision: 0.5000 - recall: 1.0000 - accuracy: 0.5000 - f1-score: 0.6667
	Failure to stop on demand tp: 0 - fp: 0 - fn: 3 - tn: 210 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	High output tp: 0 - fp: 0 - fn: 1 - tn: 212 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Leaking    tp: 1 - fp: 0 - fn: 12 - tn: 200 - precision: 1.0000 - recall: 0.0769 - accuracy: 0.0769 - f1-score: 0.1428
	Low output tp: 0 - fp: 1 - fn: 6 - tn: 206 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Minor in-service problems tp: 6 - fp: 9 - fn: 5 - tn: 193 - precision: 0.4000 - recall: 0.5455 - accuracy: 0.3000 - f1-score: 0.4616
	Noise      tp: 0 - fp: 5 - fn: 0 - tn: 208 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Other      tp: 2 - fp: 10 - fn: 7 - tn: 194 - precision: 0.1667 - recall: 0.2222 - accuracy: 0.1053 - f1-score: 0.1905
	Overheating tp: 1 - fp: 0 - fn: 3 - tn: 209 - precision: 1.0000 - recall: 0.2500 - accuracy: 0.2500 - f1-score: 0.4000
	Plugged / choked tp: 2 - fp: 1 - fn: 6 - tn: 204 - precision: 0.6667 - recall: 0.2500 - accuracy: 0.2222 - f1-score: 0.3636
	Spurious stop tp: 0 - fp: 1 - fn: 0 - tn: 212 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Structural deficiency tp: 14 - fp: 3 - fn: 7 - tn: 189 - precision: 0.8235 - recall: 0.6667 - accuracy: 0.5833 - f1-score: 0.7369
	Vibration  tp: 0 - fp: 0 - fn: 0 - tn: 213 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000

With the "Not an observation" category included:

	MICRO_AVG: acc 0.6446 - f1-score 0.7839
	MACRO_AVG: acc 0.2087 - f1-score 0.27373684210526317
	Abnormal instrument reading tp: 0 - fp: 0 - fn: 0 - tn: 273 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Breakdown  tp: 141 - fp: 6 - fn: 4 - tn: 122 - precision: 0.9592 - recall: 0.9724 - accuracy: 0.9338 - f1-score: 0.9658
	Contamination tp: 0 - fp: 0 - fn: 0 - tn: 273 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Electrical tp: 5 - fp: 6 - fn: 1 - tn: 261 - precision: 0.4545 - recall: 0.8333 - accuracy: 0.4167 - f1-score: 0.5882
	Erratic output tp: 0 - fp: 0 - fn: 0 - tn: 273 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Failure to start on demand tp: 0 - fp: 1 - fn: 1 - tn: 271 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Failure to stop on demand tp: 0 - fp: 0 - fn: 3 - tn: 270 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	High output tp: 0 - fp: 0 - fn: 1 - tn: 272 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Leaking    tp: 11 - fp: 8 - fn: 2 - tn: 252 - precision: 0.5789 - recall: 0.8462 - accuracy: 0.5238 - f1-score: 0.6875
	Low output tp: 1 - fp: 3 - fn: 5 - tn: 264 - precision: 0.2500 - recall: 0.1667 - accuracy: 0.1111 - f1-score: 0.2000
	Minor in-service problems tp: 8 - fp: 15 - fn: 3 - tn: 247 - precision: 0.3478 - recall: 0.7273 - accuracy: 0.3077 - f1-score: 0.4706
	Noise      tp: 0 - fp: 0 - fn: 0 - tn: 273 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Not an observation tp: 31 - fp: 8 - fn: 14 - tn: 220 - precision: 0.7949 - recall: 0.6889 - accuracy: 0.5849 - f1-score: 0.7381
	Other      tp: 0 - fp: 4 - fn: 9 - tn: 260 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Overheating tp: 1 - fp: 0 - fn: 3 - tn: 269 - precision: 1.0000 - recall: 0.2500 - accuracy: 0.2500 - f1-score: 0.4000
	Plugged / choked tp: 3 - fp: 3 - fn: 5 - tn: 262 - precision: 0.5000 - recall: 0.3750 - accuracy: 0.2727 - f1-score: 0.4286
	Spurious stop tp: 0 - fp: 3 - fn: 0 - tn: 270 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
	Structural deficiency tp: 13 - fp: 2 - fn: 8 - tn: 250 - precision: 0.8667 - recall: 0.6190 - accuracy: 0.5652 - f1-score: 0.7222
	Vibration  tp: 0 - fp: 0 - fn: 0 - tn: 273 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
