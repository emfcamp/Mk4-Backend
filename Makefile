.PHONY: run update clean

run:
	FLASK_APP=main.py FLASK_DEBUG=1 python -m flask run

update:
	PIPENV_MAX_SUBPROCESS=$$(($$(nproc)+1)) pipenv sync --dev

deploy:
	PIPENV_MAX_SUBPROCESS=$$(($$(nproc)+1)) pipenv install --deploy

clean:
	rm -rf ./__pycache__  # In theory pycache should be version dependent
	rm -rf ./env

shell:
	SETTINGS_FILE=$(SETTINGS) pipenv shell

test:
	SETTINGS_FILE=$(TEST_SETTINGS) pipenv run pytest ./tst

flush_memcached:
	echo 'flush_all' | nc localhost 11211

