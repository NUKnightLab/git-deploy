# git-deploy

A suite of git subcommands for managing deployment-related operations for
git repository-based deployments. Currently includes:

 * git-deploy: deploy a project to an environment-specific ansible configuration (e.g. stg, prd)
 * git-secrets: manage ansible-vault secrets for a git-deploy configured project

`git-deploy` tools are mostly just opinionated scaffolding around Ansible. 
Ansible knowledge is helpful for debugging and working through issues, but
should not be a necessary requirement.

## Installation

As deploy configurations are tied to a specific git-deploy version, it is
recommended that you install to your projects virtualenvironment with the
git-deploy version specified. E.g.:

```
 $ pip install -e git+https://github.com/NUKnightLab/git-deploy.git@1.0.6#egg=git-deploy
```

## Environment variables

* **GIT_DEPLOY_VAULT_DIR** Defaults to ~/.vault (see details below)
* **ANSIBLE_VAULT_PASSWORD_FILE** Needed if you are using ansible-vault to maintain secrets


### Alternate ansible hosts inventory

E.g., if you are supporting multiple organizations or configurations, you may
need an alternate hosts file. This can be set with ansible configs, such as
with the **ANSIBLE_INVENTORY** environment variable.


## Additional setup

The easiest way to see what needs to be done for an initial git-deploy setup is
to look at the [git-deploy-example project](https://github.com/NUKnightLab/git-deploy-example)

The bullet-point version is:

 * install git-deploy (see above)
 * create a [/etc/ansible/hosts](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
   file. The section labels of the host file match the deployment environments
   used by git-deploy.
 * set environment variables (see above)
 * (optionally) set up ansible roles (copy them from here](https://github.com/NUKnightLab/git-deploy/tree/1.0.6/etc/ansible/roles)
 * clone the example project and set any missing variables in the configs 


## Usage

Due to the way subcommand help is handled, the best way to get help is by
calling the dashed command instead of calling it as a subcommand:

```
 $ git-deploy --help
 $ git-secrets --help
```

### Some useful options

**git-deploy specifically**

Any additional options passed after the full git-deploy command will be passed
to Ansible. In general, any [options that will work with ansible-playbook](https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html) should also work with git-deploy.

E.g.:

  `--check` is a dry-run flag that shows what commands Ansible would execute:

```
  $ git deploy stg 1.0.1 --check
```


---

### Configuration


Standard ansible configurations are used for configuration management.

Ansible configs are determined by:

 * ANSIBLE_CONFIG environment variable
 * /etc/ansible/ansible.cfg
 * ~/.ansible.cfg

See the [Ansible docs](https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html)
for details.

git-deploy will attempt to load environment variables from .env in the root of
the repository if it exists.


### The git-deploy vault directory

The following environment variable is supported across the git-deploy suite:

 * **GIT_DEPLOY_VAULT_DIR** Defaults to ~/.vault

**GIT_DEPLOY_VAULT_DIR must be specified or ~/.vault must exist if vaulted secrets are used**.

Since there is no longer a GIT_DEPLOY_ASSETS_DIR, there is also not a default
vault dir at that location. The default vault directory is now ~/.vault, which
may be a simlink to the actual vault location. The vault directory should
contain sub-directories of vaults by project name.

### The vault password

The vault password can be specified in either of the following ways:

 * ANSIBLE_VAULT_PASSWORD_FILE environment variable (recommended)
 * --vault-password-file cli flag. E.g. `git deploy stg v1.0 --vault-password-file /path/to/vault/password/file`

**Use of --vault-id is strongly discouraged** as [there seem to be issues with its reliabilityl](https://github.com/ansible-community/ansible-vault/issues/183)
