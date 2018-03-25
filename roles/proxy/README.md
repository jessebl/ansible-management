Role Name
=========

Deploy HTTPS reverse proxy using nginx

Requirements
------------

Role Variables
--------------

The variables that can be passed to this role and a brief description about
them are as follows:

    domain: base domain name to use in sites

    ssl_certificate: nginx directive

    ssl_certificate_key: nginx directive

    nginx_conf: main nginx conf location

    nginx_user: user that should run nginx

    sites_enabled: directory in which to keep sites

Dependencies
------------

None

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: proxy }

License
-------

GPLv3
