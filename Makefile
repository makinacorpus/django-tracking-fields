.PHONY: test coverage

test:
	PYTHONPATH=${PYTHONPATH}:`pwd` DJANGO_SETTINGS_MODULE=tracking_fields.tests.settings django-admin.py test tracking_fields.tests

coverage:
	PYTHONPATH=${PYTHONPATH}:`pwd` DJANGO_SETTINGS_MODULE=tracking_fields.tests.settings coverage run `which django-admin.py` test tracking_fields.tests
	coverage html
