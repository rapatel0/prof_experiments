
/nfs_mount/bin/nv_gpu.py -t 2000 -d 50 -o /run_context/ & 
python3 /src/kheiron_runners/train_runner.py >/run_context/stdout.txt 2>&1

