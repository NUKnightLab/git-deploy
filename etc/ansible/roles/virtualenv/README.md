## role: virtualenv

Creation of a python virtualenv with pip install dependencies from a
requirements file.

Ansible will not source your application user's shell profile, so you may
need to set the exec_path in order for the python executable to be found.

Requires a python with `-m venv` available.


### Variables

 * **requirements_file** The requirements.txt file
 * **virtualenv** The name of the virtualanv
 * **python** The python command to invoke
 * **exec_path**. May be required if full python path is not provided.
