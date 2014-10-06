===============
Tracking Fields
===============

.. image:: https://travis-ci.org/makinacorpus/django-tracking-fields.png
    :target: https://travis-ci.org/makinacorpus/django-tracking-fields

.. image:: https://coveralls.io/repos/makinacorpus/django-tracking-fields/badge.png?branch=master
    :target: https://coveralls.io/r/makinacorpus/django-tracking-fields?branch=master


A Django app allowing the tracking of objects field in the admin site.

Quick start
-----------

1. Add "tracking_fields" to your INSTALLED_APPS settings.

2. Add the ``tracking_fields.decorators.track`` decorator to your models with the fields you want to track as parameters::

     @track('test', 'm2m')
     class MyModel(models.Model):
         test = models.BooleanField('Test', default=True)
         m2m = models.ManyToManyField(SubModelTest, null=True)

3. Your objects are now tracked. See the admin site for the tracking information.

4. You can run the tests by doing ``make test``.

5. If you want to track who does the changes, please install the ``django-cuser`` app.

FAQ
===

* Why does my ManyToMany relationship create two events ?

    The admin site actually do a clear then an add for m2m fields (even when they are not modified). Thus, two events are created for each ManyToManyField.


AUTHORS
=======

* Yann FOUILLAT (alias Gagaro) <yann.fouillat@makina-corpus.com>

|makinacom|_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com


=======
LICENSE
=======

* GPLv3+
