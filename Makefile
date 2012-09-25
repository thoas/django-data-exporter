test:
	flake8 data_exporter --ignore=E501,E127,E128,E124
	coverage run --branch --source=data_exporter manage.py test data_exporter
	coverage report --omit=data_exporter/test*

release:
	python setup.py sdist register upload -s
