import logging
from flask import Flask
from flask_cors import CORS
from flask.logging import default_handler
from environs import Env

from .logger import logging_handler




env = Env()
env.read_env('.env')

app = Flask(__name__, static_url_path='',
                  static_folder='client/build',
                  template_folder='client/build')

app.config.from_mapping(
	GRAPH_PASSWORD = env("GRAPH_PASSWORD"),
	JSON_SORT_KEYS = False,
)

CORS(app) # set up CORS

app.logger.removeHandler(default_handler)
app.logger.addHandler(logging_handler)

logging_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)

import echidna_app.views


if __name__=="__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)