### Setup


create virtual environment via [virtualenv](https://pypi.python.org/pypi/virtualenv) (recommended):

    $ virtualenv feedstrap_env
    $ cd feedstrap_env && source bin/activate
        
create django project:
        
    $ django-admin.py startproject dev_server
    $ cd dev_server
        
intall requirements via pip:
        
    $ git clone https://github.com/eblahm/feedstrap.git
    $ cd feedstrap
    $ pip install -r requirements.txt
        
### Option 1 - Quick Start (the fastest way to get up and running)

- intialize database, upload seed data and runserver - using example settings

        $ ./manage.py syncdb --settings=feedstrap.xample_settings
        $ ./manage.py createcachetable temp --settings=feedstrap.xample_settings
        $ ./manage.py upload --settings=feedstrap.xample_settings
        $ ./manage.py runserver localhost:8000 --settings=feedstrap.xample_settings
    
### Option 2 - Full Install (recommended)
- edit dev_server/settings.py to reflect the following:
    
        ### edit to reflect DATABASE backend  
        
        DATABASES = {
            'default': {
                        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
                        'NAME':  "/ect/data.db",
                        'USER': '',
                        'PASSWORD': '',
                        'HOST': '', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
                        'PORT': '', # Set to empty string for default.
                    }
        } 
        
        ### edit to reflect your CACHE backend
        ### if you don't have a cache system installed, keep the following as is and run: $ ./manage.py createcachetable temp
        
        CACHES = {
         'default': {
                     'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
                     'LOCATION': 'temp',
                     'TIMEOUT': 60 * 60 * 24,
                 }
        }
        
        ### append to your existing INSTALLED_APPS
        
        INSTALLED_APPS += (
            'django_comments_xtd',
            'django.contrib.comments',
            'tinymce',
            'feedstrap',
        )
        
        ### add additional app settings
        
        COMMENTS_APP = 'django_comments_xtd'
        COMMENTS_XTD_MAX_THREAD_LEVEL = 1
        TINYMCE_DEFAULT_CONFIG = (
            'theme': 'advanced'    
        )
        TINYMCE_SPELLCHECKER = True
        
        ### edit to reflect your email backend
        
        SERVER_EMAIL = 'you@example.com'
        DEFAULT_FROM_EMAIL = 'no-reply@example.com'
        EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
        EMAIL_FILE_PATH = '/ect/dev_email_log/'
        
- intialize database and runserver
    
        $ ./manage.py syncdb 
        $ ./manage.py upload
        $ ./manage.py runserver
