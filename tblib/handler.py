import traceback

from flask import jsonify

class ResponseCode:
	OK = 0
	ERROR = 1
	NOT_FOUND = 10
	TRANSACTION_FAILURE = 20
	QUANTITY_EXCEEDS_LIMIT = 30
	NO_ENOUGH_MONEY = 40

	MESSAGES = {
		OK: 'sucess',
		ERROR: 'unknow error',
		NOT_FOUND: 'not found',
		TRANSACTION_FAILURE: 'transaction fail',
		QUANTITY_EXCEEDS_LIMIT: 'too many for limt',
		NO_ENOUGH_MONEY: 'no so much money',
	}

def json_response(code=ResponseCode.OK, message='', **kwargs):
	return jsonify({
			'code': code,
			'message': message or ResponseCode.MESSAGES.get(code, ''),
			'data': kwargs,
		})

def handle_error_json(exception):
	traceback.print_exc()
	return json_response(ResponseCode.ERROR, str(exception))