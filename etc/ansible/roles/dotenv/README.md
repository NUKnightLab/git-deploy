## role: dotenv

Ansible role for creating a .env file, which has environment variables for
executing the application and is referenced by the application service.

A .envrc file is also created which manages the sourcing of the .env
autotmatically when a user enters the project directory.

### Tasks

 * create .env file
 * create .envrc file


### Variables

 * **deploy_dir**. The root of the project.
 * **service_name**. Service to restart if environment variables change.
 * **init_env**. Environment variables to be written to .env.
 * **virtualenv**. Virtualenvironment to source with direnv in .envrc.
