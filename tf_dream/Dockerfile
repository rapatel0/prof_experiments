#----------------------------------------------
# Inheiratance container
#----------------------------------------------
# I will update when we have new containers 
# with optimizations.
#FROM kheiron/joe_ref
#FROM kheiron/intel_mkl:0.4.11
#FROM 10.58.124.244:35000/intel_mkl:0.4.11
FROM 10.58.124.244:35000/kheiron_intel_mkl_1_3 


#----------------------------------------------
# Custom installed packages
#----------------------------------------------
#---------------------------------
#
# Please use this section to add any custom 
# packages you would like to use 
USER root

#RUN rm -rf /home/keras/.local
#RUN pip uninstall -y keras
#RUN pip install git+https://github.com/fchollet/keras.git
#RUN pip install --upgrade git+https://github.com/farizrahman4u/keras-contrib.git


# Example (delete when actually using): 
RUN 	apt update && \ 
	apt install -y less && \
        apt install -y vim && \
        apt install -y tmux time

RUN     pip3 install docopt




#-----------------------------------------------
# Checkout your files
#-----------------------------------------------

# The workflow here is to simply fetch and checkout
# your source code from git and build it into the 
# job on the fly. We can always have the code co-located
# with the job that is running 
USER 	keras

# Example 
# This next snippet checkouts the 'joeDGX' branch, 
# pulls the newest code, and reinstalls the module
WORKDIR /src/kheiron_zoo
RUN 	eval `ssh-agent` && ssh-add /home/keras/.ssh/id_rsa &&\
	git fetch 				&& \
        git checkout tfm_rfork && \
	git pull 				&& \
	cd .. 					&& \
	pip install --user -e  kheiron_zoo

# Same thing except it fetches the master branch of 
# online preproc. Added for convenience
WORKDIR /src/online_preproc
RUN 	eval `ssh-agent` && ssh-add /home/keras/.ssh/id_rsa &&\
	git fetch 				&& \ 
	git checkout tfm_rfork && \
	git pull  				&& \
	cd .. 					&& \
	pip install --user -e online_preproc

WORKDIR /src/kheiron_runners
RUN     eval `ssh-agent` && ssh-add /home/keras/.ssh/id_rsa && \
	git fetch 				&& \ 
	git checkout tfm_rfork && \
	git pull  				&& \
	cd .. 					


RUN rm /src/kheiron_runners/settings/train_settings.py
COPY train_settings.py /src/kheiron_runners/settings/train_settings.py
#RUN rm /src/online_preproc/online_preproc/examples/classifier_queue_builder.py
#COPY classifier_queue_builder.py /src/online_preproc/online_preproc/examples/classifier_queue_builder.py

ENV NUM_GPUS=4

WORKDIR /run_context

ENTRYPOINT ./entrypoint.sh
