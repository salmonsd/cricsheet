DB_FILE_PATH=./db/adi_cricsheet.db

remove-db:
	rm -f $(DB_FILE_PATH)

setup-db:
	python3 ./src/setup_db.py

load-data:
	python3 ./src/load_data.py

build:
	docker build -t cricsheet:latest .

run:
	docker run -it --entrypoint bash cricsheet:latest

