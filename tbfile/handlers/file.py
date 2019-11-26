from os import path

from flask import Blueprint, request, current_app
from werkzeug.wsgi import wrap_file
from werkzeug.exceptions import NotFound
from gridfs import GridFS
from gridfs.errors import NoFile
from flask_pymongo import BSONObjectIdConverter

from tblib.mongo import mongo
from tblib.handler import json_response, ResponseCode

from ..models import FileSchema
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

executor = ThreadPoolExecutor(max_workers=2)

file = Blueprint('file', __name__, url_prefix='')

@file.route('/files', methods=['POST'])
def create_file():
	if 'file' not in request.files or request.files['file'].filename == '':
		raise NotFound
	id = mongo.save_file(request.files['file'].filename, request.files['file'])
	_, ext = path.splitext(request.files['file'].filename)
	executor.submit(lambda: make_thumbnails(id))
	return json_response(id='{}{}'.format(id, ext))

@file.route('/files/<id>', methods=['GET'])
def file_info(id):
	id, _ = path.splitext(id)
	id = BSONObjectIdConverter({}).to_python(id)
	try:
		file = GridFS(mongo.db).get(id)
	except NoFile:
		raise NotFound()
	return json_response(file=FileSchema().dump(file))

def file_response(id, download=False):
	try:
		file = GridFS(mongo.db).get(id)
	except NoFile:
		raise NotFound()

	data = wrap_file(request.environ, file, buffer_size=1024 * 255)
	response = current_app.response_class(
		data,
		mimetype=file.content_type,
		direct_passthrough=True,
		)
	response.content_length = file.length
	response.last_modified = file.upload_date
	response.set_etag(file.md5)
	response.cache_control.max_age = 365 * 24 * 3600
	response.cache_control.public = True
	response.make_conditional(request)
	if download:
		response.headers.set(
				'Content-Disposition', 'attachment', filename=file.filename.encode('utf-8')
			)
	return response

@file.route('/<id>', methods=['GET'])
def view_file(id):
	id, _ = path.splitext(id)
	id = BSONObjectIdConverter({}).to_python(id)
	return file_response(id)

@file.route('/<id>/download', methods=['GET'])
def download_file(id):
	id, _ = path.splitext(id)
	id = BSONObjectIdConverter({}).to_python(id)
	return file_response(id, True)


def make_thumbnails(id):
	try:
		file = GridFS(mongo.db).get(id)
	except NoFile:
		raise NotFound()
	img = Image.open(file)
	thumbnails = {}
	for size in (1024, 512, 200):
		t = img.copy()
		t.thumbnail((size, size))
		filename = '{}_{}'.format(id, size)
		filepath = '/tmp/{}'.format(filename)
		t.sava(filepath, 'JPEG')
		with open(filepath, 'rb') as f:
			thumbnails[str(size)] = mongo.save_file(filename, f)
		unlink(filepath)
	mongo.db.fs.files.update({'_id': id}, {'$set':{'thumbnails':thumbnails}})