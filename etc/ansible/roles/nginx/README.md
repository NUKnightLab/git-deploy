## role: nginx

Ansible role for creating nginx configs and restarting Nginx. Does not
deal with installation and configuration of Nginx itself.

Templated config files are created in /etc/nginx/sites-available and are
symlinked into /etc/nginx/sites-enabled.


### Tasks

 * create nginx config
 * symlink nginx config


### Handlers

 * restart nginx


### Variables

 * **nginx_template**. Default: nginx.conf.j2
 * **service_name**. A pathname-friendly name
 * **service_port**. Port where the service application runs.
 * **nginx_client_max_body_size**. Default: 5M
 * **domains**. Space-delimited application domains.


### Template file

Specify an alternate template file by specifying the `nginx_template`
variable, with a template in the project-specific template directory and
a file name that is **not** nginx.conf.j2.
