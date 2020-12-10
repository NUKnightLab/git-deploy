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
 $ pip install git+https://github.com/NUKnightLab/git-deploy.git@1.0.6
```

## Additional setup

If your project has not already been setup for git-deploy, do these
additional steps:

 * Create a `deploy` directory in your project root with a `config.common.yml`
   file and `config.<env>.yml` environment specific files. See `Advanced Usage`
   below for information on using an alternative project-relative location.
   See the `config-vars.md` file for a summary of configs required for each
   playbook. See below for more information about config file formats.
   the `AWS setup for S3 static file deployment` section below for more information
 * Create ansible playbooks to be executed and reference them in the playbooks
   variable in the configs


### (optional) Ansible roles

A set of [ansible roles](https://github.com/NUKnightLab/git-deploy/tree/1.0.6/etc/ansible/roles)
is provided in the git-deploy GitHub repository. Those roles can be copied as-is
into /etc/ansible/roles. The missing variables that you will need in your config
can be teased out by attempted runs of `git deploy`.


### Playbooks

Playbooks should be located in the project deploy directory using the naming
convention: playbook.<type>.yml

Playbooks should be referenced by the `playbooks` variable in the configs.
Alternatively, specify the `--playbook` option on the command line.

### git-deploy configs

Configs are actually ansible variable files which should be referenced by the
playbook.

The convention is to name the config according to the deployment environment
and to reference the `env` variable when loading vars_files. See the examples
folder for details.

Note that __env__ should match a labeled host configuration in /etc/ansible/hosts.


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


This means:

 * Most alternative configurations are now handled via the Ansible config rather than
   with GIT_DEPLOY env variables.
 * Unless otherwise specified, the inventory file is /etc/ansible/hosts
   - alternative inventory file can be specified by -i (https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html)
   - inventory can also be specified in the Ansible config file 
 * Specify project-specific configurations in an ansible config file indicated by the ANSIBLE_CONFIG environment variable (https://docs.ansible.com/ansible/latest/reference_appendices/config.html)
 * The following environment variables are **no longer supported**:
    - GIT_DEPLOY_ASSETS_DIR
    - GIT_DEPLOY_INVENTORY
    - GIT_DEPLOY_VAULT_PASSWORD_FILE


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

## Legacy setup for git-deploy <= 1.0.5


See the legacy README doc if you need to install a version of git-deploy older
than 1.0.6



## First Steps


## hosts (a.k.a inventory) file format

git-deploy depends on standard Ansible configs for finding the inventory.

This means your inventory can be specified by:

 * /etc/ansible/hosts
 * An inventory file specified by `inventory=filepath` in an ansible config (`~/.ansible.cfg`)
 * On the command-line via the -i flag


The inventory file will typically contain hosts and users for each deployment
environment. A typical hosts file setup for `stg` and `prd` environments looks
like:

```
[stg]
staging-appserver.mydomain.com ansible_user=ansibleuser

[prd]
production-appserver.mydomain.com ansible_user=ansibleuser
```

Or if, for example, your user varies by project:

```
[stg]
staging-appserver.mydomain.com ansible_user="{{ application_user }}"

[prd]
production-appserver.mydomain.com ansible_user="{{ application_user }}"
```

## Anatomy of a deploy directory

### Config files

The collection of config files is the basis for organizing the concept of
deployment environments for a project. Config files are Ansible compatible
Yaml files that contain the variables (or vault lookups) needed to deploy the
project to a given deployment environment. Config files are named by convention
as:

```
config.env.yml
```

Where env is the name of a deployment environment that **must match a group
name** in the Ansible inventory configuration.

Note that _common_ is a reserved name for the creation of a common config that
is imported by the other configs. The common config file should be named:

```
config.common.yml
```

An example config stack might look like this:

```
config.common.yml
config.stg.yml
config.prd.yml
config.prd_work.yml
```

Where **stg**, **prd**, and **prd_work** are all group names in the inventory
file. E.g:

/etc/ansible/hosts:

```
[stg]
stg.example.com

[prd]
prd.example.com

[prd_work]
prd-work.example.com
```


### Custom playbooks

As of git-deploy 1.06, there are no longer builtin playbooks. All playbooks
must be specified either by the playbooks variable, or by the the --playbook
command-line option which may be specified multiple times in the command.

---


## Additional First-time setup for each project


### AWS setup for S3 static file deployment

Static file sync to S3 requires the AWS cli command to be installed and
configured on a remote delegated host. This is currently the first app host
listed in your inventory file.

See the aws s3 cli reference docs for AWS CLI setup:
http://docs.aws.amazon.com/cli/latest/reference/s3/index.html

If you can do `aws s3 sync <sourcedir> <bucket>` on the remote host as the
designated application_user, then the sync playbook should work.

See the `deploy.static.yml` variable summary in `config-vars.md` for more
information on the configs required for static sync.


## Config file contents

Configuration parameters should be placed into either `config.common.yml` or
`config.<env>.yml` as appropriate in the **deploy_config_dir** (usually `deploy`)
relative to the project root. Configurations may freely reference other config
parameters as required by passing the parameter as a template variable via
{{ }}.

See `config-vars.md` and the example configs for more information about the
specific parameters required and the Yaml configuration syntax.


## Advanced usage

### Environment variables

For project-specific settings, consider using virtualenvwrapper's
postactivate hook for managing non-default environment variable settings.

**GIT_DEPLOY_ASSETS_DIR**

Default `~/.git-deploy-assets`. Sets the location of the assets directory which
contains the hosts file, password file (`vault_password`), and project vaults.
The locations of these assets can also be specified individually with the
`GIT_DEPLOY_INVENTORY`, `GIT_DEPLOY_VAULT_PASSWORD_FILE`, and
`GIT_DEPLOY_VAULT_DIR` environment variables.

**GIT_DEPLOY_INVENTORY**

Default: `/etc/ansible/hosts`. Sets the file to be used for specifying Ansible
hosts. File should contain <env>-<role> host groups with `app` being the
only currently supported role.

**GIT_DEPLOY_PROJECT_CONFIG_DIR**

Default: `deploy`. The location of git-deploy configs, relative to the project
root. This directory must contain a `config.common.yml` file and a
`config.<env>.yml` for each deploy environment supported.

**GIT_DEPLOY_VAULT_DIR**

Default: `~/.vault`. Location of directory containing Ansible vault files.
Files should be located in subdirectories named for the project name, and
should follow the naming convention of `vault.<env>.yml`

**GIT_DEPLOY_VAULT_PASSWORD_FILE**
Default: `~/.vault_password`. File which contains the password for decrypting
Ansible vault files located in the vault directory.


## Project organization and operations requirements

git-deploy is designed around some very specific process and organizational
assumptions; The following are some fundamental considerations to make in
determining whether git-deploy is a good fit for your project:


### Git-based deployment

Applications are deployed via git clone/pull. The specific branches that are
deployed match environment names as described in the next section.


### Named deployment environments and branches

Deployment infrastructure is organized into environments whose names match
deployment branches in your repository. The supported environments must be
configured in your project's `config.common.yml` file. This configuration is a
structure which indicates in key-value pairs the environments and the
respective merge-from branch for each. For example, given the environments
`staging` and `production` where staging is merged from `master` and
production is merged from `staging`, the following configuration is required in
`config.common.yml`:

```
supported_envs:
  stg: master
  prd: stg
```


### Static file deployment

Support is currently provided for S3 sync or for copying static files into a
server filesystem directory for self-hosting.


### Implicit security handling

Security is handled outside the scope of git-deploy. If you have a public key
in known hosts of the remote server, git-deploy *should* just work. If you use
a pemfile, you should create a ~/.ssh/config file such as:

```
Host *.<domain>.com
    User apps
    IdentityFile ~/mypemfile.pem
```

### Single system user

A single system user is set to handle application management, git deployment,
service starting, etc. This username is specified via the `application_user`
parameter

## Development

Install as editable (-e).


```
 $ pip install -e '.[test]'
```

If using virtualenvironments, be sure your setup allows the venv to remain
sourced across projects so that git-deploy can be used within the context of
deployable projects.

The simpler thing to do is probably deploy into user scope:

```
 $ pip install --user -e '.[test]'
```



