# 1.0.2b

 * Added optional `static_service` parameter. Currently supports `s3` and empty/undefined for
hosting directly from server.
 * Static file sync to S3 now requires the `static_service` parameter to be set to s3
 * Added `static_dest` parameter which may be an S3 endpoint or a filesystem directory (e.g. a `/var/www/...` or `/usr/share/...` location)
 * Removed `staticbucket` parameter. Use `static_dest` now instead
 * Added support for running individual playbooks via the `--playbook=` option

# 1.0.1

The first git-deploy
