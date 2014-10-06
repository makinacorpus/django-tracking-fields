.PHONY: test coverage

test:
	DJANGO_SETTINGS_MODULE=tracking_fields.tests.settings django-admin.py test tracking_fields.tests

coverage:
	DJANGO_SETTINGS_MODULE=tracking_fields.tests.settings coverage run `which django-admin.py` test tracking_fields.tests
	coverage html
