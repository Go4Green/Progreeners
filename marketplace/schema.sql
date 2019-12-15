CREATE TABLE IF NOT EXISTS producer(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT,
	telephone INTEGER,
	email TEXT,
	address TEXT,
	lat REAL,
	lon REAL,
	pass INTEGER
);

CREATE TABLE IF NOT EXISTS receiver(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT,
	telephone INTEGER,
	email TEXT,
	address TEXT,
	lat REAL,
	lon REAL,
	pass INTEGER
);

CREATE TABLE IF NOT EXISTS tokens(
	token TEXT PRIMARY KEY,
	is_producer INTEGER,
	id INTEGER,
	creation_timestamp INTEGER
);

CREATE TABLE IF NOT EXISTS products(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	producer_id INTEGER,
	announcement_date TEXT,
	amount INTEGER,
	kind TEXT,
	availability_date TEXT,
	price REAL,
	receiver_id INTEGER,
	FOREIGN KEY (producer_id) REFERENCES producer(id) ON DELETE CASCADE,
	FOREIGN KEY (receiver_id) REFERENCES receiver(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS results(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	product_id INTEGER,
	amount INTEGER,
	price REAL,
	technical_details TEXT,
	results_date TEXT,
	FOREIGN KEY (product_id) REFERENCES producer(id) ON DELETE CASCADE
);