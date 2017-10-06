
/nfs_mount/bin/nv_gpu.py -t 2000 -d 50 -o /run_context/ & 
python /src/Dream/kheiron-runners/train_runner.py >/src/Dream/kheiron-runners/stdout.txt 2>&1

