import numpy as np
import cv2
import os
import h5py
from random import shuffle, seed

# Set random seed for reproducible training / val split
seed(7)

# Load in the file
filelist = np.load('SP_SN_August_malignancy.np')
test_filelist = np.load('test_filelist.npy')

test_png = []
for i in test_filelist:
    test_png.append(str(i,'utf-8'))

# Setup empty arrays
png_filelist = []
case_id_pos = []
case_id_neg = []

final_test_filelist = []
# Loop through data and append to arrays
for i in filelist:
    if '.png' in i[0]:
        if i[0] in test_png:
            final_test_filelist.append(i)
        else:
            png_filelist.append(i)
            if i[1] == '0':
                case_id_neg.append(i[0].split('_')[0])
            elif i[1] == '1':
                case_id_pos.append(i[0].split('_')[0])

# Unique ids in case lists
case_id_pos = list(set(case_id_pos))
case_id_neg = list(set(case_id_neg))
# Shuffle positive and negative case ids
shuffle(case_id_pos)
shuffle(case_id_neg)
pos_size = len(case_id_pos)
neg_size = len(case_id_neg)


# Split the training and validation 85%/15%, ensure the same proportion of
# postiive samples are distributed in both
val_pos = case_id_pos[:int(0.1*pos_size)]
val_neg = case_id_neg[:int(0.1*neg_size)]
validation = val_pos + val_neg

train_pos = case_id_pos[int(0.1*pos_size):]
train_neg = case_id_neg[int(0.1*neg_size):]
training = train_pos + train_neg

# Setup final filelists
final_val_filelist = []
final_train_filelist = []

# Add each image to correct train / val list and repeat
for i in png_filelist:
    if i[0].split('_')[0] in validation:
        if i[0].split('_')[0] in case_id_neg:
            final_val_filelist.append(i)
        else:
            final_val_filelist.extend([i]*24)
    elif i[0].split('_')[0] in training:
        if i[0].split('_')[0] in case_id_neg:
            final_train_filelist.append(i)
        else:
            final_train_filelist.extend([i]*24)

# Shuffle these arrays again (avoid bunching repeated positives)
shuffle(final_val_filelist)
shuffle(final_train_filelist)
shuffle(final_test_filelist)

# Turn to numpy arrays and save
final_val_filelist = np.array(final_val_filelist)
final_train_filelist = np.array(final_train_filelist)
final_test_filelist = np.array(final_test_filelist)

for i in final_val_filelist[:20]:
    print(i)
'''
np.save('balanced_validation_filelist.npy', final_val_filelist)
np.save('balanced_training_filelist.npy', final_train_filelist)
np.save('final_test_filelist.npy', final_test_filelist)
'''
