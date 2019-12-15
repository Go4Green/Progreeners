INSERT INTO producer (name, pass, email, telephone, address, lat, lon) VALUES ("Company S.A.","12345","info@site.com","2105555555","Αθήνας 55",34.2,35.7);
INSERT INTO producer (name, pass, email, telephone, address, lat, lon) VALUES ("Ταβέρνα ο Μάκης","12345","info@gmail.com","2104444444","Καρδίτσας 55",34.2,35.4);
INSERT INTO producer (name, pass, email, telephone, address, lat, lon) VALUES ("Ταβέρνα τα 32 αδέρφια","12345","info@baidu.com","2104567890","Θεσσαλονίκης 55",34.1,35.4);

INSERT INTO products (producer_id, announcement_date, amount, kind, availability_date, price, receiver_id) VALUES (1, "2019/1/1", 55, "Ηλιέλαιο", "2019/2/2", "1.2", NULL);
INSERT INTO products (producer_id, announcement_date, amount, kind, availability_date, price, receiver_id) VALUES (1, "2019/1/1", 55, "Ελαιόλαδο", "2019/2/2", "2.2", NULL);
INSERT INTO products (producer_id, announcement_date, amount, kind, availability_date, price, receiver_id) VALUES (2, "2019/2/3", 55, "Ηλιέλαιο", "2019/4/5", "1.5", NULL);
INSERT INTO products (producer_id, announcement_date, amount, kind, availability_date, price, receiver_id) VALUES (2, "2019/1/1", 55, "Ελαιόλαδο", "2019/2/6", "3.2", NULL);
INSERT INTO products (producer_id, announcement_date, amount, kind, availability_date, price, receiver_id) VALUES (3, "2019/1/3", 55, "Ελαιόλαδο", "2019/1/8", "2.4", NULL);
