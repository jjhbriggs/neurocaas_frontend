Developer Guide
========================

This section contains guidance for developing NeuroCAAS

To contribute to NeuroCAAS, please contact us at neurocaas@gmail.com

1. Project Structure
---------------------

This project utilizes two django apps, :ref:`Account` and :ref:`Main`.
The :ref:`Account` app handles user management, 
and the :ref:`Main` app has core functions to process data.

2. Deployment on Ubuntu Server
------------------------------

Refer to `this link <https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04>`_ for additional assistance.

**Install essential packages:**

.. code-block::

   $ sudo apt update
   $ sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl

**Install virtualenv:**

.. code-block::

   $ sudo pip3 install virtualenv
   $ cd /home/ubuntu/ncap
   $ virtualenv venv
   $ source venv/bin/activate
   $ pip install –r requirements.txt
   $ sudo ufw allow 8000
   $ deactivate

**Clone the repo**

.. code-block::

   $ git clone https://github.com/jjhbriggs/neurocaas_frontend ncap

**Install dependencies**

.. code-block::

   $ cd ncap
   $ virtualenv venv
   $ source  venv/bin/activate
   (venv) $ pip install -r requirements.txt 


**Create systemd Socket and Service Files for Gunicorn**

.. code-block::
   
   $ sudo nano /etc/systemd/system/gunicorn. Service
   
Add the following content and save:

.. code-block::

	[Unit]
	Description=gunicorn daemon
	Requires=gunicorn.socket
	After=network.target

	[Service]
	User=ubuntu
	Group=www-data
	WorkingDirectory=/home/ubuntu/ncap
	ExecStart=/home/ubuntu/ncap/venv/bin/gunicorn \
			  --access-logfile - \
			  --workers 3 \
			  --bind unix:/run/gunicorn.sock \
			  ncap.wsgi:application
	[Install]
	WantedBy=multi-user.target

.. code-block::
   
   $ sudo systemctl daemon-reload
   $ sudo systemctl restart gunicorn
   
**Configure Nginx to Proxy Pass to Gunicorn**

Install  Nginx

.. code-block::
   
   $ sudo apt install nginx

Configure Nginx

.. code-block::

   $ sudo nano /etc/nginx/sites-available/ncap

Add following content and save:

.. code-block::

	server {
		listen 80;
		server_name www.neurocaas.com neurocaas.com neurocaas.org www.neurocaas.org;
		location = /favicon.ico { access_log off; log_not_found off; }
		location /static/ {
				root /home/ubuntu/ncap;
		}
		location /docs/ {
				alias /home/ubuntu/ncap/docs/build/html/;
				index  index.html index.htm;
		}
		location / {
				include proxy_params;
				proxy_pass http://unix:/run/gunicorn.sock;
		 }
	}

.. code-block::

   $ sudo ln -s /etc/nginx/sites-available/ncap /etc/nginx/sites-enabled
   $ sudo nginx –t
   $ sudo systemctl restart nginx
   $ sudo ufw delete allow 8000
   $ sudo ufw allow 'Nginx Full'

**Environment Variables**

A set of valid AWS keys is needed to run tests properly. These should be set in .bash_profile.

Add these lines to your .bash_profile in the home directory (with your keys in place of the placeholders).
Travis CI has a similar set of environement variables in its project settings which are used for testing, however local testing requires that the developer source bash_profile by running:

.. code-block::

   source .bash_profile

.. code-block::

   export AWS_ACCESS_KEY=<placeholder>
   export AWS_SECRET_ACCESS_KEY=<placeholder>

**Cron Job**

There is a python script located "/home/ubuntu/ncap/cron.py".
It is running daily, removing old files in "/home/ubuntu/ncap/static/downloads" folder.

There is an additional python script called db_backup.py that backups the database to an s3 bucket daily.

Run the following command to edit crontab config (with <placeholder>s replaced with the AWS keys used to access your s3 bucket.

.. code-block::

   $ crontab –e
   
Add these line and save:

.. code-block::

   AWS_ACCESS_KEY=<placeholder>
   AWS_SECRET_ACCESS_KEY=<placeholder>
   5 4 * * * /usr/bin/python3 /home/ubuntu/ncap/cron.py >> ~/cron.log 2>&1
   0 0 * * * /usr/bin/python3 /home/ubuntu/ncap/db_backup.py >> ~/cron_db.log 2>&1
   
Start Cron job

.. code-block::

   $ sudo service cron start

3. Database Information
-----------------------

Currently the database used in NeuroCAAS is sqlite. The DB configuration is stored in ncap/settings.py.

To migrate the database, run the following in the command line:

.. code-block::

   python3 manage.py migrate

**Database Diagram:**

.. image:: dbdiagram.png

Additionally, Django stores a hashed password for every user. See the Django documentation on this for more information: https://docs.djangoproject.com/en/3.0/topics/auth/passwords/

4. AWS S3 File Uploading
------------------------

File uploading is done using a multipart upload based on the aws sdk javascript plugin (https://sdk.amazonaws.com/js/aws-sdk-2.617.0.min.js).
All functions needed to perform uploading are stored inside a js file named "file_upload.js" inside the "static/js/fileupload" folder.

Multiple large files can be uploaded via this drag and drop box.
To upload file to the s3 bucket, we need to add following permission on s3 bucket.

This allows users to upload files directly through a web browser.

.. code-block::

	<?xml version="1.0" encoding="UTF-8"?>
        <CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
        <CORSRule>
            <AllowedOrigin>*</AllowedOrigin>
            <AllowedMethod>GET</AllowedMethod>
            <AllowedMethod>PUT</AllowedMethod>
            <AllowedMethod>POST</AllowedMethod>
            <AllowedMethod>DELETE</AllowedMethod>
            <MaxAgeSeconds>3000</MaxAgeSeconds>
            <ExposeHeader>ETag</ExposeHeader>
            <AllowedHeader>*</AllowedHeader>
        </CORSRule>
        </CORSConfiguration>
        
.. image:: s3pic.png

