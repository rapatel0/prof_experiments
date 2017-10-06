#!/usr/bin/env python
""" dgxJob - Run Job on DGX
Usage:
  dgxJob.py <input_directory> <script_command>
  dgxJob.py <input_directory> <script_command> [ --data_mount=<dm> ... ]
  dgxJob.py <input_directory> <script_command> [ -d <dm> ... ]
  dgxJob.py -h | --help
  dgxJob.py -v | --version 
  
Options:
  -h --help              Show this screen.
  -v --version           Show version.
  -d --data_mount=<dm>   Additional mount points for data volumes 

Notes:
    Use a fresh shell to run this script as it will take over the shell.
    Currently it is assumed that the docker container to run is completely
    Independent.  This means two things: 
        1) All files that are generated/used  will need to be in the local docker
           build directory
        2) The docker container will exit on completion
    At commandline the program will return two values upon submition of a job
        - Port:         port value for tensorboard
        - Job ID:       hash value of tensorboard
        - Directory:    Directory on DGX where run data will be stored 
                        (Do not modify while job is running.)
    Jobs will appear in docker ps and docker images as:
        build_job/runner:JOB_ID

    The container can be mounted using standard docker commands while running:
       E.g.:"docker exec -it container_name bash"
    
    Additional data mounts must be visible on the DGX, i.e., don't mount data that 
    has not been copied over to the DGX
"""

# -----------------------------------------------
# Copywrite Ravi Patel
# -----------------------------------------------


import pickle
import sys
# import uuid
import getpass
import os
import time
import signal
import json
import random
import string

from docopt import docopt
from subprocess import call 
from distutils.dir_util import copy_tree
from datetime import datetime
import shutil

# custom module
sys.path.append('/home/ravi/git_repos_for_production_dev/dgxQueue')
import job_frontend as jf

def copytree(src, dst, symlinks=False, ignore=None):
    
    
    
    
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)	
    return


def signal_handler(signal, frame):
    print("""\n\nYou pressed Ctrl+C!! 
          Please use docker to stop a running job. 
          Be sure that the currently running job is your own,  
          so to avoid stopping others. A container can be identified
          by the Container Name specified above \n\n """) 

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def get_short_job_id():
    return ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8))

def create_job_json(job_hash, current_user, target_directory, tensorboard_counter):
    returnDict = { 'job_id' : job_hash,
                   'job_settings': {'container_name' : str(current_user)+str(job_hash),
                                    'image_id': 'build/' + str(current_user) + ':' + str(job_hash),
                                    'run_directory': str(target_directory),
                                    'tensorboard_exposed_port': str(tensorboard_counter + 7000)}
                   }
    
    print("\n\n\n-----------------------------------------")
    print("Job Id:           {0} ".format(str(job_hash)))
    print("Container Name:   {0} ".format(str(current_user)+str(job_hash)))
    print("Image Id:         {0} ".format('build/' + str(current_user) + ':' + str(job_hash)))
    print("Run Directory:    {0} ".format(str(target_directory)))
    print("Tensorboard Port: {0} ".format(str(tensorboard_counter+7000)))
    print("-----------------------------------------")
    return returnDict


def stupid_hack_to_create_directories(target_directory_list, current_run_directory):
    copy_path=[]
    for item in target_directory_list:
        try:
            copy_path = copy_path + [item]
            os.mkdir('/'.join(copy_path))
        except OSError as ex_error:
            print("Directory {} exists".format(copy_path))
    copy_tree(current_run_directory, '/'.join(target_directory_list)) 




if __name__ == '__main__':

    arguements = docopt(__doc__, version='DGX Job 0.1 ')
    signal.signal(signal.SIGINT, signal_handler)
    # print(arguements)

    # ---------------------------------------------------------------------
    # Get the user information and metadata copying the files to run directory
    # ---------------------------------------------------------------------
    current_user = getpass.getuser()
    job_hash =get_short_job_id()
    current_day = datetime.now().day
    current_month  = datetime.now().month
    current_year = datetime.now().year
    target_directory_list = [ '/workdir_tmp', current_user, 
                              str(current_year), 
                              str(current_month), 
                              str(current_day),  
                              job_hash ]
    
    target_directory = '/'.join(target_directory_list)
    current_run_directory = os.path.abspath( arguements["<input_directory>"] )
    

    # ---------------------------------------------------------------------
    # Check if directory is too big
    # ---------------------------------------------------------------------
    
    print("Checking directory size")
    MAX_DIRECTORY_SIZE = [32 * 1024* 1024] # 32 megabytes
    size = get_size(current_run_directory)
    if (size>MAX_DIRECTORY_SIZE):
        print("Directory is too big")
        print("Please use -d command for mounting data directories")
        print("Note: please also move directories outside of the current folder")
        print("If you wish to mount the directory in the current folder inside\nthe docker container, just mount it as\n\t\t\
                    -d <folder_to_mount>:/run_context/<folder_to_mount>\n")
        sys.exit()


    # ---------------------------------------------------------------------
    # get data mounts
    # ---------------------------------------------------------------------
    
    data_mounts =arguements["--data_mount"] 
    script_command = arguements["<script_command>"]

    # counter for tensorboard ports so there are no conflicts
    tensorboard_counter = 0
    if ( os.path.isfile("/job_metadata/tensorboard_counter") ):
       with open('/job_metadata/tensorboard_counter', 'r+') as f:
            tensorboard_counter = int(f.read())
            f.seek(0)
            f.write( str((tensorboard_counter + 1 ) % 100))
            f.truncate()





    # ---------------------------------------------------------------------
    # Copy files and submit job 
    # ---------------------------------------------------------------------
    
    if ( os.path.isabs(target_directory) and os.path.isabs(current_run_directory) ):
        # old python hack
        stupid_hack_to_create_directories(target_directory_list, current_run_directory)
        os.system('chgrp -R ml_users ' + target_directory)       
    else:
        sys.stderr.write('Error in path converstion - The path are not absolute ')


    # mark job_status
    user_job_status_directory =['~/.dgx_job_runner'] 
    if not os.path.exists(os.path.expanduser('/'.join(user_job_status_directory))):
        os.mkdir(os.path.expanduser('/'.join(user_job_status_directory))) 
    
    jobJSON = create_job_json(job_hash=job_hash,
                              current_user=current_user,
                              target_directory=target_directory,
                              tensorboard_counter=tensorboard_counter)

    with open(os.path.expanduser('/'.join(user_job_status_directory+[str(job_hash)])), 'w') as outfile:
        json.dump(jobJSON, 
                  outfile,
                  sort_keys = True, 
                  indent = 4,
                  ensure_ascii = False)

    # Build container
    build_result = jf.tasks.cmd_docker_build.delay(
        job_id=job_hash, 
        master_directory=target_directory, 
        username=current_user,
        gpu_list=['7'] )
    build_counter = 0
    while( not build_result.ready()):
        sys.stdout.write('\r'+ 'Docker is building container -  seconds elapsed: '+str(build_counter))
        sys.stdout.flush()
        time.sleep(1)
        build_counter+=1
    print("\n Build Complete")


    # Run job
    run_counter = 0
    run_result = jf.tasks.cmd_docker_run.delay(job_id=job_hash, 
                                               tensorboard_exposed_port=tensorboard_counter+7000, 
                                               script_command=script_command,
                                               metadata_directory='/job_metadata/', 
                                               master_directory=target_directory, 
                                               data_mount_directories=data_mounts, 
                                               gpu_count=4, 
                                               username=current_user, 
                                               container_name= str(current_user) + str(job_hash) ) 
    while( not run_result.ready()):
        sys.stdout.write('\r'+'Docker is running container - seconds elapsed: '+ str(run_counter) )
        time.sleep(1)
        run_counter+=1
    print("\n Run Complete")


    
