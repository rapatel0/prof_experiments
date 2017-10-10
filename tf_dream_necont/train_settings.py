import time
import os

TRAIN_DATA_DIR = ['/data/'
                  'anatomy-june_png_tabar_strat/training']

VAL_DATA_DIR = ['/data/'
                'anatomy-june_png_tabar_strat/validation']

BASE_RESULTS_PATH = '/nfs_mount/KheironML/User_Directories/rp/model_runs/' \
                    'tabar_rsna/{}'.format(
        time.strftime('%Y%m%d-%H%M%S'))

# Sampling settings
sampling_kwargs = {'patch_count': 2, 'patch_height': 224,
                   'patch_width': 224}


# Augmentation settings
augmentation_kwargs = {
    'max_zoom': 0.2, 'max_stretch': 0., 'max_rotation_angle': 20,
    'max_channel_shift': 0., 'max_shear_range': 0.}

# Queue settings
loader_queue_kwargs = {
    'read_threads': 4,
    'capacity': 64,
    'key_dict_json_file':
        os.path.join(TRAIN_DATA_DIR[0], 'key_dict.json')}

shuffle_queue_kwargs = {'capacity': 128, 'min_after_dequeue':40}
queue_builder_kwargs = {
    'max_size': 256,
    'read_threads': 24,
    'scale': 65535,
    'loader_queue_kwargs': loader_queue_kwargs,
    'shuffle_queue_kwargs': shuffle_queue_kwargs,
    # 'sampling_kwargs': sampling_kwargs,
    # 'augmentation_kwargs': augmentation_kwargs,
    # 'output_mask_keys': [
    #     ('mass_benign',
    #      ['mass_masks/birads1', 'mass_masks/birads2', 'mass_masks/birads3']),
    #     ('mass_malignant',
    #      ['mass_masks/birads4', 'mass_masks/birads5'])],
    'additional_feature_keys': []}

# Train settings
train_kwargs = {'n_epochs': 10,
                'samples_per_epoch': {'train': 1713, 'val': 60},
                'batch_size': 8}
optimizer_kwargs = {'learning_rate': 1e-8}
ema_kwargs = {'decay': 0.999, 'eval_with_ema': False}

# Model settings
model_kwargs = {'classes': [5, 4], 'reduce': 0.5,
                'batch_norm_kwargs': {'momentum': 0.99, 'axis': 1,
                                       'fused': True },
                'train_top_only': False}
    # 'output_names': zip(*queue_builder_kwargs['output_mask_keys'])}

# Monitoring settings
CB_MONITOR = 'val_output_accuracy'

callbacks = {
    'EarlyStopping': {
        'patience': 10,
        'monitor': CB_MONITOR,
        'minimize': False},
    'ModelCheckpoint': {
        'monitor': CB_MONITOR,
        'verbose': 1,
        'save_best_only': True,
        'mode': 'max'},
    'ReduceLROnPlateau': {
        'lr': optimizer_kwargs['learning_rate'],
        'mode': 'max',
        'verbose': 1,
        'patience': 5,
        'monitor': CB_MONITOR},
    'CSVLogger': {
        'filename': os.path.join(BASE_RESULTS_PATH, 'training_log.csv')
    }}

progbar_kwargs = {
    'train': {
        'verbose': 1,
        'epochs': train_kwargs['n_epochs']},
    'val': {
        'verbose': 1,
        'validation': True,
        'epochs': train_kwargs['n_epochs']}}

# Combine settings into one dict
settings = {
    'data_dir': {'train': TRAIN_DATA_DIR,
                 'val': VAL_DATA_DIR},
    'checkpoint': None,
    # 'checkpoint': {'file': '/nfs_mount/KheironML/User_Directories/mo'
    #                        '/model_runs/tabar_rsna/20171003-205923/'
    #                        'model_val_density_main_output_accuracy_0.765179-10',
    #                'ignore_scope': 'Adam'},
    'ignore_file_ids_path': '/nfs_mount/KheironML/User_Directories/mo/'
                            'meta_data/anatomy_disagree_file_ids.pkl',
    # 'ignore_file_ids_path': None,
    'input_keys': ['img'],
    'output_keys': ['label' ],
    'results_dir': BASE_RESULTS_PATH,
    'queue_builder_class': 'ClassifierQueueBuilder',
    'model': 'inception_v3',
    'optimizer': 'AdamOptimizer',
    'loss': 'softmax_cross_entropy',
    'queue_builder_kwargs': queue_builder_kwargs,
    'train_kwargs': train_kwargs,
    'model_kwargs': model_kwargs,
    'progbar_kwargs': progbar_kwargs,
    'optimizer_kwargs': optimizer_kwargs,
    'loss_kwargs': [{}, {}],
    'ema_kwargs': ema_kwargs,
    'callbacks': callbacks,
    'metrics': ['accuracy'],
    'num_gpus': 1}

