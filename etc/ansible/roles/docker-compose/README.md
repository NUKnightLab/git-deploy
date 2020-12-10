## role: docker-compose

Ansible role for handling build and execute tasks with a docker-compose file.


### Tasks

 * build containers
 * run scripts


### Variables

**Required**

 * **docker_compose_file**. The compose file.
 * **deploy_dir**. The root of the project.


**Optional**

 * **docker_compose_commands**. Commands to run via docker-compose after build.
