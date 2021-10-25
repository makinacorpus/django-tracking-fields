=========
Changelog
=========

1.3.3 (2021-10-25)
------------------

* Fix tracking of models with uuid ids

1.3.2 (2021-09-01)
------------------

* Fix related event when there is no backward relation.

1.3.1 (2021-02-19)
------------------

* Added `get_object_model_verbose_name`.

1.3.0 (2021-02-19)
------------------

* Added `get_object_model` on `TrackingEvent` to be able to get model class in templates.
* Fix deprecation warnings for Django 4.0.
* Drop support for Django 2.0 and 2.1.

1.2.1 (2020-10-20)
------------------

* Deferred fields are not tracked to avoid additional requests.

1.2.0 (2020-05-07)
------------------

* fix 'str' object has no attribute 'name' #6
* Django 3.0 compatibility
* Drop support for Django 1.11

1.1.2 (2019-09-11)
------------------

* added serialization for xworkflow StateWrapper

1.1.1 (2019-01-25)
------------------

* Optimize admin user lookup

1.1.0 (2019-01-24)
------------------

* Compatibility with Django 1.11 to 2.1
* Compatibility droped for earlier versions

1.0.6
-----

* Fix unicode error in admin with Python 3.4 and django_cuser

1.0.5
-----

* Fix MANIFEST

1.0.4
-----

* Order TrackingEvent by -date

1.0.3
-----

* Fix MANIFEST

1.0.2
-----

* Include migrations in MANIFEST

1.0.0
-----

* Initial release
