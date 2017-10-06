from online_preproc.queue_builder import QueueBuilder
import tensorflow as tf
from online_preproc.utils.transformation_utils import resize_images_with_padding
from online_preproc.utils.queue_utils import extract_masks
from online_preproc.utils.io_utils import get_png_paths

FLAGS = tf.app.flags
FLAGS.DEBUG = False
FLAGS.global_seed_value = 1


class ClassifierQueueBuilder(QueueBuilder):
    def __init__(self, dirs, loader_queue_kwargs,
                 shuffle_queue_kwargs,
                 max_size=None,
                 additional_feature_keys=None,
                 augmentation_kwargs=None,
                 read_threads=1,
                 scale=None,
                 ignore_file_ids=None):
        """
        Args:
            dirs: Directories to extract tf records from, for each queue.
            loader_queue_kwargs: kwargs for the loader queue.
            shuffle_queue_kwargs: kwargs for the suffle queue which feeds model
            max_size: If set the image and masks will be resized such
            that their largest side is set to max_side and the other
            is resized to maintain the aspect ratio. Padding is added to
            the smaller side to result in a square image of (max_size,
            max_size).
            sampling_kwargs: optional kwargs for sampling.
            augmentation_kwargs: optional kwargs for augmentations.
            read_threads: no. of threads used to feed shuffle queue.
            ignore_file_ids: list of file_ids to ignore
        """

        super().__init__(
            loader_queue_kwargs=loader_queue_kwargs,
            augmentation_kwargs=augmentation_kwargs)

        self.dirs = dirs
        self.max_size = max_size
        self.shuffle_queue_kwargs = shuffle_queue_kwargs
        self.read_threads = read_threads
        self.scale = scale
        self.ignore_file_ids = ignore_file_ids or []

        self.additional_feature_keys = additional_feature_keys

        # Set output shapes for shuffle queue
        if self.augmentation_kwargs:
            output_dims = [1, self.augmentation_kwargs['output_height'],
                           self.augmentation_kwargs['output_width']]
        else:
            if not isinstance(self.max_size,(list,tuple)):
                self.max_size = (self.max_size, self.max_size)
            output_dims = [1, self.max_size[0], self.max_size[1]]

        self.shuffle_queue_kwargs['shapes'] = [
            output_dims,
            [len(self.dirs)],
            *[[]] * len(
            self.additional_feature_keys)]

        # Set names for final shuffle queue
        self.shuffle_queue_kwargs['names'] = \
            ['img', 'label',
             *self.additional_feature_keys]

        # Set one-hot encoded label array
        self.labels = tf.eye(len(self.dirs), dtype=tf.int32)

    def build_example_queues(self):
        """Creates the queue to go before the model.

         Args:
             capacity (int): The maximum number of items in the queue.
             name (str): The name to assign the queue.
             min_after_dequeue (int): The minimum number of items that must be in the
                 queue before allowing dequeue operations.
             read_threads (int): The number of threads to start for the Queue.
             batch_size (int): The batch size

         Returns:
             [`tf.RandomShuffleQueue`]: Queues for positive and negative
             examples
         """

        queue_handles = []
        for i, filenames in enumerate(self.dirs):
            # Load data from tf records
            file_loader_queue = self.build_loader_queue(
                filenames, **self.loader_queue_kwargs)
            data = file_loader_queue.dequeue()

            ignore = tf.greater(
                tf.reduce_sum(
                    tf.cast(
                        tf.equal(
                            data['fileid'],
                            self.ignore_file_ids),
                        tf.float32)), 0)

            # Get image and masks and additional features
            [im] = extract_masks(data, ['img'])

            additional_features = [data[k] for k in
                                   self.additional_feature_keys]

            # for d in additional_features:
            #     d.set_shape([])

            if self.max_size:
                im = resize_images_with_padding(im, self.max_size)

            # Pad Full images when augmenting
            if self.max_size and self.augmentation_kwargs:
                im = tf.image.resize_image_with_crop_or_pad(
                    im, target_height=self.augmentation_kwargs['meta_height'],
                    target_width=self.augmentation_kwargs['meta_width'])

            # Set shuffle queue data types
            self.shuffle_queue_kwargs['dtypes'] = \
                [tf.float64, # im.dtype,
                 self.labels.dtype,
                 *[d.dtype for d in additional_features]]

            queue_handle = tf.RandomShuffleQueue(
                name=str(i),
                **self.shuffle_queue_kwargs)

            label = self.labels[i]

            if self.augmentation_kwargs:
                im_final = \
                    self.build_augmentation_graph(
                        im,
                        channels=1,
                        **self.augmentation_kwargs)
                im_final = tf.concat([im, im_final], 0)
                label = tf.concat([label, label], 0)
            else:
                im_final = im

            # Create enqueueing dict (and convert to channels first)
            im_final = tf.squeeze(tf.transpose(
                im_final, perm=[0, 3, 1, 2]), 0)
            if self.scale:
                im_final /= self.scale

            enqueue_dict = dict(zip(self.shuffle_queue_kwargs['names'],
                                    [im_final,
                                     label, *additional_features]))

            # Enqueue
            enqueue_op = tf.cond(ignore,
                                 lambda: tf.no_op(),
                                 lambda: queue_handle.enqueue(enqueue_dict))

            # Add queue to collection
            qr = tf.train.QueueRunner(
                queue_handle, [enqueue_op] * self.read_threads)
            tf.train.add_queue_runner(qr)
            queue_handles.append(queue_handle)

        return queue_handles
