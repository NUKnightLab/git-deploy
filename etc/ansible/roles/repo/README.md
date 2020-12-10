## role: repo

Ansible role for cloning/pulling a project repository.


### Variables

  * **project_repo**. Project repository, e.g. git@github.com:MyAccount/MyProject.git
  * **deploy_dir**. Path to repository destination, includes repo folder name.
  * **project_version**. Branch or tag to deploy.


### Optional

  * **git_key_file**. Path to git key file.
