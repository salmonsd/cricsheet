DB_FILE_PATH=./db/odi_cricsheet.db
PWD = $(CURDIR)

remove-db:
	rm -f $(DB_FILE_PATH)

format:
	black src/

build:
	docker build -t cricsheet:latest .

run:
	docker run -it --name cricsheet --rm --volume /$(PWD):/usr/src/app/ cricsheet:latest bash

setup-db:
	python3 ./src/setup_db.py

load-data:
	python3 ./src/load_data.py
