## role: service

Role for enabling a systemd service. Mainly designed for services proxied by Nginx.

TODO: Should Nginx restart be optional?


### Tasks

 * Create systemd service config
 * ensure service is running


### Variables

 * **service_name**
 * **service_template** Service configuration template. Defaults to templates/default.service.j2


### Default template specific

 * **application_user**
 * **application_group**
 * **application_dir**
 * **env_file**. k=v .env file to load.
 * **service_exec**. Command to execute


### Notes

Assumes that Nginx should be restarted when the service is modified.

To override the default template, specify the service_template variable to
choose a template with a different name.
