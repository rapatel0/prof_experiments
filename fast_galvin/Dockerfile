#----------------------------------------------
# Inheiratance container
#----------------------------------------------
# I will update when we have new containers 
# with optimizations.
#FROM kheiron/joe_ref
FROM kheiron/intel_mkl:0.4.11



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
        apt install -y tmux

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
	git checkout galvin     		&& \
	git pull 				&& \
	cd .. 					&& \
	pip install --user -e kheiron_zoo

# Same thing except it fetches the master branch of 
# online preproc. Added for convenience
WORKDIR /src/online_preproc
RUN 	eval `ssh-agent` && ssh-add /home/keras/.ssh/id_rsa &&\
	git fetch 				&& \ 
	git checkout old_galvin_fast			&& \
	git pull  				&& \
	cd .. 					&& \
	pip install --user -e online_preproc

# Same thing except it fetches the master branch of 
# evaluation_module. Added for convenience
WORKDIR /src/evaluation_module
RUN 	eval `ssh-agent` && ssh-add /home/keras/.ssh/id_rsa &&\
	git fetch 				&& \
	git checkout master 			&& \
	git pull  				&& \
	cd .. 					&& \
	pip install --user -e evaluation_module

RUN pip install scikit-image

ENV NUM_GPUS=4
#RUN mkdir -p /run_context/calcification
#RUN chown -R keras:ml_users /run_context/calcification

COPY . /run_context
WORKDIR /run_context


ENTRYPOINT ./entrypoint.sh
