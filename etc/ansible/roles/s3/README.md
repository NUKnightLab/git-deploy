## role: s3

Ansible role to sync files to s3. Requires the **aws cli** to be installed and
configured on the remote host.

Currently hard-coded to set synced files to public-read.


### Tasks

 * sync directory to s3


### Variables

 * **s3_src_dir**. The directory on the remote server to sync to s3.
 * **s3_dest**. The s3 destination.
