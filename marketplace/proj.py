from flask import Flask,g,render_template,request,flash,jsonify
import sqlite3
from datetime import date,timedelta
# from flask_session import Session
from flask import session
from http import HTTPStatus
from secrets import token_hex
import time
from datetime import datetime
from flask_selfdoc import Autodoc

app = Flask(__name__,static_url_path='/static')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

auto = Autodoc(app)

# sess = Session()

# sess.init_app(app)

DATABASE = 'test.db'

def format_error(err_str):
	err_dict = {'error_info': err_str}
	return jsonify(err_dict)

def logger(func_name, action_name, e):
	try:
		fp = open('logs_cnt.txt', 'r')
		line = fp.readline()
		log_id = int(line)
		fp.close()
	except:
		log_id = 0
	
	fp = open('logs.txt', 'a')
	fp.write(f'{log_id}: {func_name} $ {action_name} $ {e}\n')
	fp.close()

	fp = open('logs_cnt.txt', 'w')
	fp.write(f'{log_id + 1}')
	fp.close()

	result = format_error(f'Server error has been logged. Contact system administrator reporting ID #{log_id}.')

	return jsonify(result)

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE)
	db.commit()
	return db

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

class output:
	string = ""
	def add(s,str,end='\n'):
		s.string = s.string + str + end
	
	def get(s):
		ret = s.string
		s.string = ""
		return ret

o = output()

def print_result(statement,table,updatable=True):
	cur = get_db().cursor()
	cur.execute(statement)
	names = [description[0] for description in cur.description]
	rows = cur.fetchall()
	o.add('<table id="res">')

	# first print Column names
	o.add('<tr>')
	for i in names[1:]:
		o.add('<th><b>'+str(i).replace("_"," ")+'</b></th>')

	if updatable:
		o.add('<th><b>Delete</b></th>')
	o.add('</tr>')

	for i in rows[:]:
		o.add('<tr>')

		for j in range(1,1+len(i[1:])):
			if updatable:
				o.add('<td><a href="/update/%s/%d/%s">%s</a></td>'%(table,i[0],names[j],i[j]))
			else:
				o.add('<td>%s</td>'%(i[j]))
		
		if updatable:
			o.add('<td><a href="/delete/%s/%d"><font color="red">X</font></a></td>' % (table,i[0]) )
		o.add('</tr>')
	o.add('</table>')

########### Below is the app ###########

@app.route('/')
def index():
	return render_template('index.html')


@app.route('/api/producers', methods=['POST'])
@auto.doc()
def register_producer():
	# Check for input validity
	try:
		r = request.get_json()

		name = r['name']
		password = r['password']
		email = r['email']
		telephone = r['telephone']
		address = r['address']
		latitude = r['latitude']
		longitude = r['longitude']

	except:
		return format_error('Invalid or missing data.'), HTTPStatus.BAD_REQUEST

	# Check for producer's name duplicate
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT COUNT(name) FROM producer WHERE name="{name}"'
		result = cur.execute(query)

		name_duplicates = result.fetchone()[0]

		if name_duplicates > 0:
			return format_error('Duplicate provider name.'), HTTPStatus.BAD_REQUEST

	except Exception as e:
		return logger('register_producer', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Register producer
	try:
		query = f'INSERT INTO producer (name, pass, email, telephone, address, lat, lon) VALUES ("{name}", "{password}", "{email}", "{telephone}", "{address}", {latitude}, {longitude})'
		cur.execute(query)

		conn.commit()

	except Exception as e:
		return logger('register_producer', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return '', HTTPStatus.NO_CONTENT


@app.route('/api/receivers', methods=['POST'])
@auto.doc()
def register_receiver():
	# Check for input validity
	try:
		r = request.get_json()

		name = r['name']
		password = r['password']
		email = r['email']
		telephone = r['telephone']
		address = r['address']
		latitude = r['latitude']
		longitude = r['longitude']
		
	except:
		return format_error('Invalid or missing data.'), HTTPStatus.BAD_REQUEST

	# Check for receiver's name duplicate
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT COUNT(name) FROM receiver WHERE name="{name}"'
		result = cur.execute(query)

		name_duplicates = result.fetchone()[0]

		if name_duplicates > 0:
			return format_error('Duplicate provider name.'), HTTPStatus.BAD_REQUEST

	except Exception as e:
		return logger('register_receiver', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Register receiver
	try:
		query = f'INSERT INTO receiver (name, pass, email, telephone, address, lat, lon) VALUES ("{name}", "{password}", "{email}", "{telephone}", "{address}", {latitude}, {longitude})'
		cur.execute(query)

		conn.commit()

	except Exception as e:
		return logger('register_receiver', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return '', HTTPStatus.NO_CONTENT


@app.route('/api/producers/login', methods=['GET'])
@auto.doc()
def login_producer():
	# Check for input validity
	try:
		r = request.get_json()

		name = r['name']
		password = r['password']
		
	except:
		return format_error('Invalid or missing data.'), HTTPStatus.BAD_REQUEST

	# Check for producer's identifiers matching
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id FROM producer WHERE name="{name}" AND pass="{password}"'
		result = cur.execute(query)

		matching_id = result.fetchone()

		if matching_id is None:
			return format_error('Wrong producer\'s identifiers.'), HTTPStatus.BAD_REQUEST

	except Exception as e:
		return logger('login_producer', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Login producer
	try:
		producer_id = matching_id[0]

		token = token_hex(16)
		
		current_UTC_timestamp = int(time.time())

		query = f'INSERT INTO tokens (token, is_producer, id, creation_timestamp) VALUES ("{token}", 1, "{producer_id}", "{current_UTC_timestamp}")'
		cur.execute(query)

		conn.commit()

	except Exception as e:
		return logger('login_producer', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	result = {'token': token}

	return jsonify(result), HTTPStatus.OK


@app.route('/api/receivers/login', methods=['GET'])
@auto.doc()
def login_receiver():
	# Check for input validity
	try:
		r = request.get_json()

		name = r['name']
		password = r['password']
		
	except:
		return format_error('Invalid or missing data.'), HTTPStatus.BAD_REQUEST

	# Check for receiver's identifiers matching
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id FROM receiver WHERE name="{name}" AND pass="{password}"'
		result = cur.execute(query)

		matching_id = result.fetchone()

		if matching_id is None:
			return format_error('Wrong receiver\'s identifiers.'), HTTPStatus.BAD_REQUEST

	except Exception as e:
		return logger('login_receiver', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Login receiver
	try:
		receiver_id = matching_id[0]

		token = token_hex(16)
		
		current_UTC_timestamp = int(time.time())

		query = f'INSERT INTO tokens (token, is_producer, id, creation_timestamp) VALUES ("{token}", 0, "{receiver_id}", "{current_UTC_timestamp}")'
		cur.execute(query)

		conn.commit()

	except Exception as e:
		return logger('login_receiver', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	result = {'token': token}

	return jsonify(result), HTTPStatus.OK


@app.route('/api/producers', methods=['GET'])
@auto.doc()
def get_producers():
	""" Get all producers """
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = 'SELECT id, name, email, telephone, address, lat, lon FROM producer'
		result = cur.execute(query)

		producers_data_tuple_list = result.fetchall()

		producers_data = []

		for producer_data_tuple in producers_data_tuple_list:
			producer_data = {
				'id': producer_data_tuple[0],
				'name': producer_data_tuple[1],
				'email': producer_data_tuple[2],
				'telephone': producer_data_tuple[3],
				'address': producer_data_tuple[4],
				'lat': producer_data_tuple[5],
				'lon': producer_data_tuple[6]
			}

			producers_data.append(producer_data)

	except Exception as e:
		return logger('get_producers', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(producers_data), HTTPStatus.OK


@app.route('/api/receivers', methods=['GET'])
@auto.doc()
def get_receivers():
	""" Get all receivers """
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = 'SELECT id, name, email, telephone, address, lat, lon FROM receiver'
		result = cur.execute(query)

		receivers_data_tuple_list = result.fetchall()

		receivers_data = []

		for receiver_data_tuple in receivers_data_tuple_list:
			receiver_data = {
				'id': receiver_data_tuple[0],
				'name': receiver_data_tuple[1],
				'email': receiver_data_tuple[2],
				'telephone': receiver_data_tuple[3],
				'address': receiver_data_tuple[4],
				'lat': receiver_data_tuple[5],
				'lon': receiver_data_tuple[6]
			}

			receivers_data.append(receiver_data)

	except Exception as e:
		return logger('get_receivers', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(receivers_data), HTTPStatus.OK


@app.route('/api/producers/<int:producer_id>', methods=['GET'])
@auto.doc()
def get_producer(producer_id):
	""" Get producer with given id """
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id, name, email, telephone, address, lat, lon FROM producer WHERE id={producer_id}'
		result = cur.execute(query)

		producer_data_tuple = result.fetchone()

		if producer_data_tuple is None:
			return 'Non existing producer\'s id.', HTTPStatus.NOT_FOUND

		producer_data = {
			'id': producer_data_tuple[0],
			'name': producer_data_tuple[1],
			'email': producer_data_tuple[2],
			'telephone': producer_data_tuple[3],
			'address': producer_data_tuple[4],
			'lat': producer_data_tuple[5],
			'lon': producer_data_tuple[6]
		}

	except Exception as e:
		return logger('get_producer', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(producer_data), HTTPStatus.OK


@app.route('/api/receivers/<int:receiver_id>', methods=['GET'])
@auto.doc()
def get_receiver(receiver_id):
	""" Get receiver with given id """
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id, name, email, telephone, address, lat, lon FROM receiver WHERE id={receiver_id}'
		result = cur.execute(query)

		receiver_data_tuple = result.fetchone()

		if receiver_data_tuple is None:
			return 'Non existing receiver\'s id.', HTTPStatus.NOT_FOUND

		receiver_data = {
			'id': receiver_data_tuple[0],
			'name': receiver_data_tuple[1],
			'email': receiver_data_tuple[2],
			'telephone': receiver_data_tuple[3],
			'address': receiver_data_tuple[4],
			'lat': receiver_data_tuple[5],
			'lon': receiver_data_tuple[6]
		}

	except Exception as e:
		return logger('get_receiver', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(receiver_data), HTTPStatus.OK


@app.route('/api/products', methods=['POST'])
@auto.doc()
def announce_product():
	""" Submit a new product """
	# Check for input validity
	try:
		r = request.get_json()

		token = r['token']
		amount = r['amount']
		kind = r['kind']
		availability_date = r['availability_date']
		price = r['price']

	except:
		return format_error('Invalid or missing data.'), HTTPStatus.BAD_REQUEST
	
	# Check for producer's authentication
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id FROM tokens WHERE token="{token}" AND is_producer=1'
		result = cur.execute(query)

		matching_id = result.fetchone()

		if matching_id is None:
			return format_error('Invalid token.'), HTTPStatus.UNAUTHORIZED

	except Exception as e:
		return logger('announce_product', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Announce product
	try:
		producer_id = matching_id[0]

		announcement_date = datetime.today().strftime('%Y/%d/%m')

		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'INSERT INTO products (producer_id, announcement_date, amount, kind, availability_date, price, receiver_id) VALUES ("{producer_id}", "{announcement_date}", "{amount}", "{kind}", "{availability_date}", {price}, NULL)'
		cur.execute(query)

		conn.commit()

	except Exception as e:
		return logger('announce_product', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return '', HTTPStatus.NO_CONTENT


@app.route('/api/products', methods=['GET'])
@auto.doc()
def get_products():
	""" List all products """
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = 'SELECT id, producer_id, announcement_date, amount, kind, availability_date, price, receiver_id FROM products'
		result = cur.execute(query)

		products_data_tuple_list = result.fetchall()

		products_data = []

		for product_data_tuple in products_data_tuple_list:
			product_data = {
				'id': product_data_tuple[0],
				'producer_id': product_data_tuple[1],
				'announcement_date': product_data_tuple[2],
				'amount': product_data_tuple[3],
				'kind': product_data_tuple[4],
				'availability_date': product_data_tuple[5],
				'price': product_data_tuple[6],
				'receiver_id': product_data_tuple[7]
			}

			products_data.append(product_data)

	except Exception as e:
		return logger('get_products', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(products_data), HTTPStatus.OK


@app.route('/api/products/<int:product_id>', methods=['GET'])
@auto.doc()
def get_product(product_id):
	""" Get product with given id """
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id, producer_id, announcement_date, amount, kind, availability_date, price, receiver_id FROM products WHERE id={product_id}'
		result = cur.execute(query)

		product_data_tuple = result.fetchone()

		if product_data_tuple is None:
			return 'Non existing product\'s id.', HTTPStatus.NOT_FOUND

		product_data = {
				'id': product_data_tuple[0],
				'producer_id': product_data_tuple[1],
				'announcement_date': product_data_tuple[2],
				'amount': product_data_tuple[3],
				'kind': product_data_tuple[4],
				'availability_date': product_data_tuple[5],
				'price': product_data_tuple[6],
				'receiver_id': product_data_tuple[7]
			}

	except Exception as e:
		return logger('get_product', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(product_data), HTTPStatus.OK


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@auto.doc()
def remove_product(product_id):
	""" Remove product with given id """
	# Check for input validity
	try:
		r = request.get_json()

		token = r['token']

	except:
		return format_error('Invalid or missing data.'), HTTPStatus.BAD_REQUEST
	
	# Check for producer's authentication
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id FROM tokens WHERE token="{token}" AND is_producer=1'
		result = cur.execute(query)

		matching_id = result.fetchone()

		if matching_id is None:
			return format_error('Invalid token.'), HTTPStatus.UNAUTHORIZED

	except Exception as e:
		return logger('remove_product', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	# Check for product's existance and producer's authorization
	try:
		producer_id = matching_id[0]

		query = f'SELECT producer_id, receiver_id FROM products WHERE id="{product_id}"'
		result = cur.execute(query)

		matching_id = result.fetchone()

		if matching_id is None:
			return 'Non existing product\'s id.', HTTPStatus.NOT_FOUND
		
		if producer_id != matching_id[0]:
			return format_error('Not allowed to remove other producer\'s products.'), HTTPStatus.UNAUTHORIZED
		
		if matching_id[1] is not None:
			return format_error('Not allowed to remove contracted products.'), HTTPStatus.UNAUTHORIZED

	except Exception as e:
		return logger('remove_product', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Remove product
	try:
		query = f'DELETE FROM products WHERE id={product_id}'
		cur.execute(query)
		
		conn.commit()

	except Exception as e:
		return logger('remove_product', 2, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return '', HTTPStatus.NO_CONTENT


@app.route('/api/products/<int:product_id>', methods=['PUT'])
@auto.doc()
def update_product(product_id):
	""" Update given product """
	# Check for input validity
	try:
		r = request.get_json()

		token = r['token']

	except:
		return format_error('Invalid or missing data.'), HTTPStatus.BAD_REQUEST
	
	# Check for producer's authentication
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id, is_producer FROM tokens WHERE token="{token}"'
		result = cur.execute(query)

		matching_id = result.fetchone()

		if matching_id is None:
			return format_error('Invalid token.'), HTTPStatus.UNAUTHORIZED
		
		is_producer = matching_id[1]

	except Exception as e:
		return logger('update_product', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	if is_producer == 1:
		# Check for input validity
		try:
			amount = r['amount']
			kind = r['kind']
			availability_date = r['availability_date']
			price = r['price']

		except:
			return format_error('Invalid or missing data.'), HTTPStatus.BAD_REQUEST

		# Check for product's existance and producer's authorization
		try:
			producer_id = matching_id[0]

			query = f'SELECT producer_id, receiver_id FROM products WHERE id="{product_id}"'
			result = cur.execute(query)

			matching_id = result.fetchone()

			if matching_id is None:
				return 'Non existing product\'s id.', HTTPStatus.NOT_FOUND
			
			if producer_id != matching_id[0]:
				return format_error('Not allowed to update other producer\'s products.'), HTTPStatus.UNAUTHORIZED
			
			if matching_id[1] is not None:
				return format_error('Not allowed to update contracted products.'), HTTPStatus.UNAUTHORIZED

		except Exception as e:
			return logger('update_product', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR

		# Update product
		try:
			query = f'UPDATE products SET amount={amount}, kind="{kind}", availability_date="{availability_date}", price={price} WHERE id={product_id}'
			cur.execute(query)
			
			conn.commit()

		except Exception as e:
			return logger('update_product', 2, e), HTTPStatus.INTERNAL_SERVER_ERROR
		
		return '', HTTPStatus.NO_CONTENT
	
	else:
		# Check for product's existance and receiver's authorization
		try:
			receiver_id = matching_id[0]

			query = f'SELECT receiver_id FROM products WHERE id="{product_id}"'
			result = cur.execute(query)

			matching_id = result.fetchone()

			if matching_id is None:
				return 'Non existing product\'s id.', HTTPStatus.NOT_FOUND
			
			if matching_id[0] is not None:
				return format_error('Not allowed to update contracted products.'), HTTPStatus.UNAUTHORIZED

		except Exception as e:
			return logger('update_product', 3, e), HTTPStatus.INTERNAL_SERVER_ERROR

		# Update product
		try:
			query = f'UPDATE products SET receiver_id={receiver_id} WHERE id={product_id}'
			cur.execute(query)
			
			conn.commit()

		except Exception as e:
			return logger('update_product', 4, e), HTTPStatus.INTERNAL_SERVER_ERROR
		
		return '', HTTPStatus.NO_CONTENT


@app.route('/api/results', methods=['POST'])
@auto.doc()
def announce_results():
	""" Submit a review about given product """
	# Check for input validity
	try:
		r = request.get_json()

		token = r['token']
		product_id = r['product_id']
		amount = r['amount']
		price = r['price']
		technical_details = r['technical_details']

	except:
		return format_error('Invalid or missing data.'), HTTPStatus.BAD_REQUEST
	
	# Check for receiver's authentication
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id FROM tokens WHERE token="{token}" AND is_producer=0'
		result = cur.execute(query)

		matching_id = result.fetchone()

		if matching_id is None:
			return format_error('Invalid token.'), HTTPStatus.UNAUTHORIZED

	except Exception as e:
		return logger('announce_results', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Check for product's existance and receiver's authorization
	try:
		receiver_id = matching_id[0]

		query = f'SELECT receiver_id FROM products WHERE id="{product_id}"'
		result = cur.execute(query)

		matching_id = result.fetchone()

		if matching_id is None:
			return 'Non existing product\'s id.', HTTPStatus.NOT_FOUND
		
		if matching_id[0] != receiver_id:
			return format_error('Not allowed to update contracted products.'), HTTPStatus.UNAUTHORIZED

	except Exception as e:
		return logger('announce_results', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Check that there aren't already results for this product
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT COUNT(id) FROM results WHERE product_id="{product_id}"'
		result = cur.execute(query)

		duplicates = result.fetchone()[0]

		if duplicates > 0:
			return format_error('Duplicate results.'), HTTPStatus.BAD_REQUEST

	except Exception as e:
		return logger('announce_results', 2, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Announce results
	try:
		results_date = datetime.today().strftime('%Y/%d/%m')

		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'INSERT INTO results (product_id, amount, price, technical_details, results_date) VALUES ({product_id}, {amount}, {price}, "{technical_details}", "{results_date}")'
		cur.execute(query)

		conn.commit()

	except Exception as e:
		return logger('announce_results', 3, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return '', HTTPStatus.NO_CONTENT


@app.route('/api/results', methods=['GET'])
@auto.doc()
def get_results():
	""" Get all reviews about products """
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = 'SELECT id, product_id, amount, price, technical_details, results_date FROM results'
		result = cur.execute(query)

		results_data_tuple_list = result.fetchall()

		results_data = []

		for result_data_tuple in results_data_tuple_list:
			result_data = {
				'id': result_data_tuple[0],
				'product_id': result_data_tuple[1],
				'amount': result_data_tuple[2],
				'price': result_data_tuple[3],
				'technical_details': result_data_tuple[4],
				'results_date': result_data_tuple[5]
			}

			results_data.append(result_data)

	except Exception as e:
		return logger('get_results', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(results_data), HTTPStatus.OK


@app.route('/api/results/<int:results_id>', methods=['GET'])
@auto.doc()
def get_single_results(results_id):
	""" Get review about product with given id """
	# Get single results
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id, product_id, amount, price, technical_details, results_date FROM results WHERE id={results_id}'
		result = cur.execute(query)

		result_data_tuple = result.fetchone()

		if result_data_tuple is None:
			return 'Non existing results\' id.', HTTPStatus.NOT_FOUND

		result_data = {
			'id': result_data_tuple[0],
			'product_id': result_data_tuple[1],
			'amount': result_data_tuple[2],
			'price': result_data_tuple[3],
			'technical_details': result_data_tuple[4],
			'results_date': result_data_tuple[5]
		}

	except Exception as e:
		return logger('get_single_results', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(result_data), HTTPStatus.OK


@app.route('/api/producers/<int:producer_id>/products', methods=['GET'])
@auto.doc()
def get_producer_products(producer_id):
	""" List all products from given producer """
	# Check if producer exists
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT COUNT(id) FROM producer WHERE id={producer_id}'
		result = cur.execute(query)

		matchings = result.fetchone()[0]

		if matchings == 0:
			return 'Non existing producer\'s id.', HTTPStatus.NOT_FOUND

	except Exception as e:
		return logger('get_producer_products', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Get producer's products
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id, producer_id, announcement_date, amount, kind, availability_date, price, receiver_id FROM products WHERE producer_id={producer_id}'
		result = cur.execute(query)

		products_data_tuple_list = result.fetchall()

		products_data = []

		for product_data_tuple in products_data_tuple_list:
			product_data = {
				'id': product_data_tuple[0],
				'producer_id': product_data_tuple[1],
				'announcement_date': product_data_tuple[2],
				'amount': product_data_tuple[3],
				'kind': product_data_tuple[4],
				'availability_date': product_data_tuple[5],
				'price': product_data_tuple[6],
				'receiver_id': product_data_tuple[7]
			}

			products_data.append(product_data)

	except Exception as e:
		return logger('get_producer_products', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(products_data), HTTPStatus.OK


@app.route('/api/receivers/<int:receiver_id>/products', methods=['GET'])
@auto.doc()
def get_receiver_products(receiver_id):
	""" Get receivers of product of given id """
	# Check if receiver exists
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT COUNT(id) FROM receiver WHERE id={receiver_id}'
		result = cur.execute(query)

		matchings = result.fetchone()[0]

		if matchings == 0:
			return 'Non existing receiver\'s id.', HTTPStatus.NOT_FOUND

	except Exception as e:
		return logger('get_receiver_products', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Get receiver's products
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT id, receiver_id, announcement_date, amount, kind, availability_date, price, receiver_id FROM products WHERE receiver_id={receiver_id}'
		result = cur.execute(query)

		products_data_tuple_list = result.fetchall()

		products_data = []

		for product_data_tuple in products_data_tuple_list:
			product_data = {
				'id': product_data_tuple[0],
				'receiver_id': product_data_tuple[1],
				'announcement_date': product_data_tuple[2],
				'amount': product_data_tuple[3],
				'kind': product_data_tuple[4],
				'availability_date': product_data_tuple[5],
				'price': product_data_tuple[6],
				'receiver_id': product_data_tuple[7]
			}

			products_data.append(product_data)

	except Exception as e:
		return logger('get_receiver_products', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(products_data), HTTPStatus.OK


@app.route('/api/producers/<int:producer_id>/results', methods=['GET'])
@auto.doc()
def get_producer_results(producer_id):
	""" Get all reviews submitted to producer """
	# Check if producer exists
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT COUNT(id) FROM producer WHERE id={producer_id}'
		result = cur.execute(query)

		matchings = result.fetchone()[0]

		if matchings == 0:
			return 'Non existing producer\'s id.', HTTPStatus.NOT_FOUND

	except Exception as e:
		return logger('get_producer_products', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Get producer's results
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT results.id, results.product_id, results.amount, results.price, results.technical_details, results.results_date FROM results LEFT JOIN products ON results.product_id=products.id WHERE producer_id={producer_id}'
		result = cur.execute(query)

		results_data_tuple_list = result.fetchall()

		results_data = []

		for result_data_tuple in results_data_tuple_list:
			result_data = {
				'id': result_data_tuple[0],
				'product_id': result_data_tuple[1],
				'amount': result_data_tuple[2],
				'price': result_data_tuple[3],
				'technical_details': result_data_tuple[4],
				'results_date': result_data_tuple[5]
			}

			results_data.append(result_data)

	except Exception as e:
		return logger('get_producer_results', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(results_data), HTTPStatus.OK


@app.route('/api/receivers/<int:receiver_id>/results', methods=['GET'])
@auto.doc()
def get_receiver_results(receiver_id):
	"""  """
	# Check if receiver exists
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT COUNT(id) FROM receiver WHERE id={receiver_id}'
		result = cur.execute(query)

		matchings = result.fetchone()[0]

		if matchings == 0:
			return 'Non existing receiver\'s id.', HTTPStatus.NOT_FOUND

	except Exception as e:
		return logger('get_receiver_products', 0, e), HTTPStatus.INTERNAL_SERVER_ERROR

	# Get receiver's results
	try:
		conn = get_db()
		conn.set_trace_callback(print)
		cur = conn.cursor()

		query = f'SELECT results.id, results.product_id, results.amount, results.price, results.technical_details, results.results_date FROM results LEFT JOIN products ON results.product_id=products.id WHERE receiver_id={receiver_id}'
		result = cur.execute(query)

		results_data_tuple_list = result.fetchall()

		results_data = []

		for result_data_tuple in results_data_tuple_list:
			result_data = {
				'id': result_data_tuple[0],
				'product_id': result_data_tuple[1],
				'amount': result_data_tuple[2],
				'price': result_data_tuple[3],
				'technical_details': result_data_tuple[4],
				'results_date': result_data_tuple[5]
			}

			results_data.append(result_data)

	except Exception as e:
		return logger('get_receiver_results', 1, e), HTTPStatus.INTERNAL_SERVER_ERROR
	
	return jsonify(results_data), HTTPStatus.OK



@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/query')
def query():
	
	return app.send_static_file('query.html')

@app.route('/search/<table>')
def query_list(table):
	# o.add(session.get('username'))
	print_result('SELECT rowid,* FROM '+table,table)
	return render_template('template.html',main=o.get())

@app.route('/login/producer')
def login_producer_get():
	conn = get_db()
	cur = conn.cursor()
	return render_template('login_producer.html')

@app.route('/login/producer',methods=['POST'])
def login_producer_post():
	r = request.form
	conn = get_db()
	cur = conn.cursor()

	username = r['name']
	password = r['pass']

	result = cur.execute(f'SELECT name FROM producer WHERE name="{username}" AND pass="{password}"')

	if result.fetchone() is not None:
		session['username'] = username
		o = output()
		o.add(session.get('username'))
		return render_template('template.html', main=o.get())

	return render_template('login_producer.html')

@app.route('/insert/producer')
def insert_producer():
	conn = get_db()
	cur = conn.cursor()
	return render_template('register_producer.html')

@app.route('/insert/byproduct')
def insert_byproduct():
	conn = get_db()
	cur = conn.cursor()
	return render_template('sell_waste.html')

@app.route('/insert/producer',methods=['POST'])
def insert_book():
	r = request.form
	conn = get_db()
	cur = conn.cursor()
	try:
		cur.execute("INSERT INTO producer(name,telephone,email,address,lat,lon,pass) VALUES(?,?,?,?,?,?,?)",(r['name'],r['telephone'],r['email'],r['address'],r['lat'],r['lon'],r['pass']))
		conn.commit()
	except sqlite3.Error:
		return "an error occured"
	return "insertion Ok"

@app.route('/insert/byproduct',methods=['POST'])
def insert_member():
	r = request.form
	conn = get_db()
	cur = conn.cursor()
	try:
		cur.execute("INSERT INTO product VALUES(?,?,?,?)",(r['id'],r['availability_date'],r['amount'],r['type']))
		conn.commit()
	except sqlite3.Error:
		return "an error occured"
	return "insertion Ok"

	return render_template('template.html',main=o.get())

@app.route('/query/stats')
def query_monthly_salary_costs():
	conn = get_db()
	cur = conn.cursor()
	cur.execute("SELECT count() FROM producer");
	num_of_producers = cur.fetchone()[0]
	cur.execute("SELECT count() FROM product");
	number_of_products = cur.fetchone()[0]

	return render_template('template.html',main='''
	<center>
	<b style="color: #1da1f2;">Πλήθος παραγωγών:</b> %d </br>
	<b style="color: #1da1f2;">Πλήθος προϊόντων:</b> %d </br>
	</center>''' % (num_of_producers,number_of_products));

@app.route('/documentation')
def documentation():
    return auto.html()

@app.before_first_request
def startup():
	conn = get_db()
	cur = conn.cursor()
	cur.execute('PRAGMA foreign_keys = ON')

	for filename in ['schema.sql']:
		with open(filename) as file:
			script = file.read()
			cur.executescript(script)

	conn.commit()
