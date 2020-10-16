# TBD

 * GIT_DEPLOY_INVENTORY no longer supported (use Ansible inventory configs)
 * GIT_DEPLOY_VAULT_PASSWORD_FILE no longer supported (use Ansible vault_password_file config, ANSIBLE_VAULT_PASSWORD_FILE env var, or --vault-password-file on cli)
 * supported_envs config no longer used.
 * Branch merge workflow no longer supported. Instead, deployers should deploy specific branches/tags to specific environments.
 * Cleaner click-based CLI. More explicit usage patterns.
 * Removes deprecated Python 2 wrapper and related documentation
 * Removes support for pre-1.0.5 style deployments
 * Introduces git-secrets and git-playbook commands
 * Aligns deployment environments with env config names, thus eliminating coersion from `stg` to, e.g. `stg_app`, `stg_work`. 
 * Changed to explicit specification of playbooks in config rather than implied book list from project type
 * Eliminated builtin playbooks in favor of explicit playbooks for each project. Much less DRY overall, but also much less magical and more maintainable per project. See, e.g., Sandi Metz on [the wrong abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction). Given that git-deploy is now pip installable, it seems counterproductive to have the playbooks burried inside the tool.

# 1.0.5 (2020-09-21)

 * git-deploy.wrapper.sh and Python 2 support is deprecated 
 * Host groups now use `_` in lieu of `-` for ansible naming compliance
 * `port` variable for Nginx config is now called `application_port` for ansible reserved word compliance
 * Adds support for docker-compose based container build, deprecates python-specific app support and utils
 * Replaces upstart with systemd. Upstart no longer supported.
 * Replaces env.sh and env-run script with .env file

# 1.0.4

 * Removed buildkit parameter
 * Removed static_tmpdir for Django projects (use static_dir)
 * Removed Django and Buildkit specific static functionality, replace with `static_prep`
 * Added `static_prep` parameter for shell execution within `application_dir` prior to static sync
 * Added support for custom playbooks in the deploy directory. Custom playbooks run last and should be named in the format playbook.*.yml alongside the project config .yml files

# 1.0.3

 This version breaks backwards compatibility with any projects that do not
 explicitly set the enironment variables: GIT_DEPLOY_INVENTORY,
 GIT_DEPLOY_VAULT_DIR, and GIT_DEPLOY_VAULT_PASSWORD_FILE.

 * Added GIT_DEPLOY_ASSETS_DIR env var which defaults to ~/.git-deploy-assets. This
   now serves as a centralized default location for the hosts and vault_password
   files and for the vault directory containing vaults organized by projects.
 * Default inventory (hosts) location is no longer the Ansible default. Now:
   $GIT_DEPLOY_ASSETS_DIR/hosts
 * Default vault password file is now $GIT_DEPLOY_ASSETS_DIR/vault_password
 * Default vault directory (containing project-organized vaults) is now
   $GIT_DEPLOY_ASSETS_DIR/vault
 * Added buildkit boolean parameter for executing `npm run dist` before static sync

# 1.0.2

 * Added optional `static_service` parameter. Currently supports `s3` and empty/undefined for
hosting directly from server.
 * Static file sync to S3 now requires the `static_service` parameter to be set to s3
 * Added `static_dest` parameter which may be an S3 endpoint or a filesystem directory (e.g. a `/var/www/...` or `/usr/share/...` location)
 * Removed `staticbucket` parameter. Use `static_dest` now instead
 * Added support for running individual playbooks via the `--playbook=` option
 * Added git-deploy version management support via gitdeploy_version parameter

# 1.0.1

The first git-deploy
