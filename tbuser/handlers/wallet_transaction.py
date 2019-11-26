from flask import Blueprint, request, current_app
from sqlalchemy import and_, or_

from tblib.model import session
from tblib.handler import json_response, ResponseCode

from ..models import WalletTransaction, WalletTransactionSchema, User

wallet_transaction = Blueprint(
	'wallet_transaction', __name__, url_prefix='/wallet_transactions'
	)

@wallet_transaction.route('', methods=['POST'])
def create_wallet_transaction():
	data = request.get_json()
	wallet_transaction = WalletTransactionSchema().load(data)
	payer = User.query.get(wallet_transaction.payer_id)
	if payer is None:
		return json_response(ResponseCode.NOT_FOUND)
	payee = User.query.get(wallet_transaction.payee_id)
	if payee is None:
		return json_response(ResponseCode.NOT_FOUND)
	count1 = User.query.filter(
			and_(User.id == payer.id, User.wallet_money >= wallet_transaction.amount,
				User.wallet_money == payer.wallet_money)
		).update(
			{User.wallet_money: payer.wallet_money - wallet_transaction.amount}
		)
	count2 = User.query.filter(
			and_(User.id == payee.id, User.wallet_money == payee.wallet_money)
		).update(
			{User.wallet_money: payee.wallet_money + wallet_transaction.amount}
		)
	if count1 == 0 or count2 == 0:
		session.rollback()
		return json_response(ResponseCode.TRANSACTION_FAILURE)
	session.add(wallet_transaction)
	session.commit()
	return json_response(wallet_transaction=WalletTransactionSchema().dump(wallet_transaction))

@wallet_transaction.route('', methods=['GET'])
def wallet_transaction_list():
	user_id = request.args.get('user_id', type=int)
	order_direction = request.args.get('order_direction', 'desc')
	limit = request.args.get('limit', current_app.config['PAGINATION_PER_PAGE'], type=int)
	offset = request.args.get('offset', 0 , type=int)
	order_by = WalletTransaction.id.asc() if order_direction == 'asc' else WalletTransaction.id.desc()
	query = WalletTransaction.query
	if user_id is not None:
		query = query.filter(or_(
				WalletTransaction.payer_id == user_id, WalletTransaction.payee_id == user_id
			))
	total = query.count()
	query = query.order_by(order_by).limit(limit).offset(offset)
	return json_response(wallet_transactions=WalletTransactionSchema().dump(query, many=True), total=total)

@wallet_transaction.route('/<int:id>', methods=['POST'])
def update_wallet_transaction(id):
	data = request.get_json()
	count = WalletTransaction.query.filter(
			WalletTransaction.id == id
		).update(data)
	if count == 0:
		return json_response(ResponseCode.NOT_FOUND)
	wallet_transaction = WalletTransaction.query.get(id)
	session.commit()
	return json_response(wallet_transaction=WalletTransactionSchema().dump(wallet_transaction))

@wallet_transaction.route('/<int:id>', methods=['GET'])
def wallet_transaction_info(id):
	wallet_transaction = WalletTransaction.query.get(id)
	if wallet_transaction is None:
		return json_response(ResponseCode.NOT_FOUND)
	return json_response(wallet_transaction=WalletTransactionSchema().dump(wallet_transaction))
