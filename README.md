# git-deploy

A suite of git subcommands for managing deployment-related operations for
git repository-based deployments. Currently includes:

 * git-deploy: deploy a project repository to an environment-specific config (e.g. stg, prd)
 * git-secrets: manage ansible-vault secrets for a git-deploy configured project
 * git-playbook: run one of the git-deploy builtin playbooks (custom playbooks tbd)

`git-deploy` tools are mostly just opinionated scaffolding around Ansible. 
Ansible knowledge is helpful for debugging and working through issues, but
should not be a necessary requirement.

## Installation

To install the latest version of the full suite of git-deploy tools:

```
 $ pip install --user git+https://github.com/NUKnightLab/git-deploy.git
```

A version may be specified, e.g.:

```
 $ pip install --user git+https://github.com/NUKnightLab/git-deploy.git@1.0.6
```


## Usage

Type an empty subcommand to get help from the cli:

```
 $ git deploy
 $ git secrets
 $ git playbook
```

For more detailed help, the full hyphenated command name must be specifed for
the --help flag, due to the way git processes this flag:

```
 $ git-deploy --help
 $ git-secrets --help
 $ git-playbook --help
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


git-deploy will attempt to load environment variables from a .env file in the root
of the repository if it exists.


### The git-deploy vault directory

The following environment variable is supported across the git-deploy suite:

 * **GIT_DEPLOY_VAULT_DIR**

Since there is no longer a GIT_DEPLOY_ASSETS_DIR, there is also not a default
vault dir at that location. **GIT_DEPLOY_VAULT_DIR must be specified if vaulted
secrets are used**.



### Legacy setup for git-deploy <= 1.0.5


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
config._env_.yml
```

Where _env_ is the name of a deployment environment that **must match a group
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

Playbooks are now explicitly listed in the configuration, which can refer to
builtin git-deploy playbooks, or to custom playbooks in the deploy directory.

E.g., in the following configuration, _playbook.work.yml_ is a custom playbook
in the deploy dir:

```
playbooks:
  - build.containers.yml
  - deploy.web.yml
  - playbook.work.yml
```

The playbook list is likely to be environment specific. It is possible to
factor common components of the playlist into the common config. However,
practically it is probably better to specify the whole list for each environment
since the order of playbooks often matters and the order is not obvious when
factored apart.


---


## Additional First-time setup for each project

If your project has not already been setup for git-deploy, do these
additional steps:

 * create a `deploy` directory in your project root with a `config.common.yml`
   file and `config.<env>.yml` environment specific files. See `Advanced Usage`
   below for information on using an alternative project-relative location.
   See the `config-vars.md` file for a summary of configs required for each
   playbook. See below for more information about config file formats.
 * create environment specific branches for deployment
 * Setup a remote delegated static sync host for S3 sync with the AWS CLI. See
   the `AWS setup for S3 static file deployment` section below for more information


## Extra playbooks

git-deploy has a set of builtin playbooks useful for most projects. Projects
that require some extra work can use custom playbooks. These are standard
Ansible playbooks that go in the deploy directory for the project and are
named playbook.*.yml. Playbooks in that format will be automatically executed
after the standard playbook set.


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



