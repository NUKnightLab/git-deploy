# git-deploy

An Ansible-based git-subcommand deployment script with support for projects in
Python 3 (potentially for non-python projects also, but not yet supported as
such). See the **Project organization** section at the end of this README if
you are not sure if git-deploy is right your project's deployment needs.

`git-deploy` is mostly just some opinionated scaffolding around Ansible. 
Ansible knowledge is helpful for debugging and working through issues, but
should not be a necessary requirement.


## Usage:

`git-deploy <env>` within the project repository will deploy to
branch / environment (Note: the git branch and deployment environment should
have the same name)


### Additional options:

  `--verbose` show a lot of extra information

  `--playbook=<playbook>` run a specific playbook. Currently supported playbooks
   are: deploy.python.yml, deploy.static.yml, 'deploy.repository.yml, deploy.web.yml

## Getting started checklist

For working with a project that is already configured for git-deploy:

 1. Follow the **First Steps** section below to install Ansible and git-deploy

 2. Place a hosts file in `~/.git-deploy-assets` or in the file indicated by
    the `GIT_DEPLOY_INVENTORY` environment varable. See the **hosts**
    section below for file details.

 3. If your project has Ansible vaulted secrets, place them in a
    project-specific directory under `~/.git-deploy-assets/vault/projectname/vault.<env>.yml`.
    Also set your vault password in the file `~/.git-deploy-assets/vault_password` (See the
    Advanced Usage section below for alternative file locations).

For getting a new project configured for git-deploy, do all of the above, and
continue to follow the **Additional First-time setup for each project** section.


## First Steps

### Install Ansible

You may choose to install Ansible globally, ie. in the user context:

```
 $ pip install --user ansible
```

Or, you can install on a per-project basis into your project's virtualenv
provided your project Python is compatible with your version of Ansible.
We are currently only supporting Python 3 variants, with Ansible >= 2.9.9.

### Clone git-deploy and make it path executable

 * Clone this repository
 * Put the git-deploy.py executable on your `PATH` as `git-deploy`.

   e.g.: `ln -s ~/repos/git-deploy/git-deploy.py /usr/local/bin/git-deploy`

 * Place your hosts file in `~/.git-deploy-assets` or set `GIT_DEPLOY_INVENTORY` to
   point to your hosts file. See below for host file format


## hosts (a.k.a inventory) file format


git-deploy will look in `~/.git-deploy-assets/hosts` for the host inventory.

git-deploy currently supports a single `app` role with multiple evironments.
Support for further role-based deployment support is in the future roadmap.

A typical hosts file setup for `stg` and `prd` environments looks like:

```
[stg-app]
staging-appserver.mydomain.com ansible_user={{ application_user }}

[prd-app]
production-appserver.mydomain.com ansible_user={{ application_user }}
```

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
