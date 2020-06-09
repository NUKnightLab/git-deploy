# TBD

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
