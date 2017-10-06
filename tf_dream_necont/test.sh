nvidia-docker run -it --entrypoint=bash -v /home/rp/anatomy-june_png_tabar_strat:/data/anatomy-june_png_tabar_strat -v /nfs_mount/:/nfs_mount -v $PWD/run_context:/run_context  tf_dream
