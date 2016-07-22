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
