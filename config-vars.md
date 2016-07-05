## Implicit variables (provided by git-deploy)

These variables are generally available for use in configuration

  * `env` the current deployment environment
  * `config_dir` the application config directory. Defaults to `deploy`
  * `vault_dir` the value of `~/.vault` or `GIT_DEPLOY_VAULT_DIR` env var if set
  * `project_root` the root of the repository


## Configs required by all projects

  * `supported_envs` key-value pairs of deployment environment branches and merge-from branches
  * `project_name` a config-friendly name for this project
  * `applicaton_user` the name of the remote system user who deploys and runs the application


## deploy.python.yml

  * `env_setup_script` the shell script that is written during deployment and used for setting up execution environments
  * `env_run_script` shell script to execute arbtrary shell commands with the setup script environment sourced
  * `init_env` environment variable key-value pairs that will be written to `env_setup_script`
  * `service_name` the name of the Upstart service that manages this application
  * `requirements_file` the Python requirements.txt file with pip installable dependencies
  * `virtualenv` the virtual environment to install this project into
  * `python` python2 or python3
  * `application_dir` the python application directory. Often identical to `deploy_dir` used by `deploy.repository.yml` but it could be a subdirectory
  * `port` the port this application runs on
  * `gunicorn_reload` (true|false) whether to pass the --reload flag to gunicorn
  * `wsgi_application` the location of the wsgi file for this web application
  * `django_migrate` (optional) (true|false) default: true. Whether to run migrate on a Django


## deploy.repository.yml

  * `project_repo` the location of the git repository to deploy
  * `deploy_dir` the deployment destination for the repository on the remote host
  * `git_key_file` (optional) git key file if needed


## deploy.static.yml

  * `static_tmpdir` temporary collection directory for Django projects that use collectstatic
  * `type` the type of this application (django|flask|repository|other)
  * `application_dir` (see `application_dir` description for `deploy.python.yml`)
  * `static_service` (optional) specify s3 for S3 sync support or leave undefined or empty for filesystem copy to web hosting directory (see `static_dest` parameter)
  * `static_dir` location of static files to be synced to s3. Not used if Django collectstatic is used
  * `static_dest` S3 endpoint or filesystem directory to copy static files into
  * `staticbucket` (deprecated) the s3 bucket to sync files into (<1.0.2 only. Use `static_dest` now)


## deploy.web.yml
  * `domains` space-delimited list of domains this application listens on
  * `ssl` (optional) structure which contains the keys for `ssl_certificate` and `ssl_certificate_key` which are pointers to the remote locations of the appropriate files on the application server
  * `port` the reverse-proxy port this application runs on
  * `nginx_template` (optional) defaults to templates/nginx.j2 relative to git-deploy


## local.repository.yml

(See common config requirements above)
