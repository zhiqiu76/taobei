from flask import Flask
from . import config

def init_model(app):
	from importlib import import_module
	from tblib import model
	model.init(app)
	import_module('.models', __package__)

def init_handler(app):
	from .handlers import init
	init(app)

app = Flask(__name__)
app.config.from_object(config.configs.get(app.env))

init_model(app)
init_handler(app)

if __name__ == '__main__':
	from gevent import pywsgi
	server = pywsgi.WSGIServer(app.config['LISTENER'], app)
	print('gevent WSGIServer listen on {} ...'.format(app.config['LISTENER']))
	server.server_forever()