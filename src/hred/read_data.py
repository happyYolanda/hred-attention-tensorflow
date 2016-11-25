import tensorflow as tf
import os
import numpy as np

TRAIN_FILE = '../../data/tr_session.out'
VALIDATION_FILE = '../../data/val_session.out'
TEST_FILE = '../../data/test_session.out'
SMALL_FILE = '../../data/small_test_session.out'
eos = 2 #'2'
max_len = 12
pad = 3

TRAIN_TFR = '../../data/tfrecords/train.tfrecords'
VALIDATION_TFR = '../../data/tfrecords/valid.tfrecords'
TEST_TFR = '../../data/tfrecords/test.tfrecords'
SMALL_TFR = '../../data/tfrecords/small.tfrecords'

#BATCH_SIZE = 200


def _bytes_feature(value):
    #print tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))
    #return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def convert_to_tfr(data_file, name):
    """ Makes the TFRecoderFile
    """
    filename = os.path.join('../../data/tfrecords/%s.tfrecords' % name)
    print("Writing", filename)
    writer = tf.python_io.TFRecordWriter(filename)

    with open(data_file) as df:
        for line in df:
            input = line.strip().replace('\t', ' 1 ').replace(' ', '')
            label = input[1:] + eos
            example = tf.train.Example(
                features=tf.train.Features(
                    feature={
                        'label': _bytes_feature(label),
                        'input': _bytes_feature(input)
                    }
                )
            )

            #print example
            serialized = example.SerializeToString()
            writer.write(serialized)
    writer.close()


def read_and_decode(records_file):
    reader = tf.TFRecordReader()
    filename_queue = tf.train.string_input_producer([records_file],
                                                    num_epochs=None)
    _, serialized_example = reader.read(filename_queue)
    features = tf.parse_single_example(
        serialized_example,
        features={
            'label': tf.FixedLenFeature([], tf.string),
            'input': tf.FixedLenFeature([], tf.string)
        })

    # label = tf.decode_raw(features['label'], tf.uint8)
    # #label.set_shape()
    # input = tf.decode_raw(features['input'], tf.uint8)

    label = tf.cast(features['label'], tf.int32)
    input = tf.cast(features['input'], tf.int32)

    #print label, input

    #
    # label = features['label']
    # input = features['input']

    return label, input


def convert_multiple_files(files, names):
    for i in range(len(files)):
        convert_to_tfr(files[i], names[i])

#convert_multiple_files([TRAIN_FILE, VALIDATION_FILE, TEST_FILE], ['train', 'valid', 'test'])
#convert_multiple_files([TEST_FILE], ['test'])


#convert_to_tfr(SMALL_FILE, 'small')

# for serialized_example in tf.python_io.tf_record_iterator(SMALL_TFR):
#
#     print tf.train.Example().ParseFromString((serialized_example))
#
#     # example = tf.train.Example()
#     # example.ParseFromString(serialized_example)
#     #
#     # input = type(example.features.feature['input'].int64_list)#.value
#     # label = example.features.feature['label'].int64_list#.value
#     #
#     # print input, label
#
#
# label, input = read_and_decode(SMALL_TFR)
# print tf.train.Example().ParseFromString(label)
# #print label, input
# # input_batch, labels_batch = tf.train.shuffle_batch(
# #     [input, label], batch_size=BATCH_SIZE,
# #     capacity=2000,
# #     min_after_dequeue=1000)
# #
# # print input_batch, labels_batch
#
#
# # label, input = read_and_decode('../../data/tfrecords/small.tfrecords')
# # print label, input

def read_data(data_file):

    with open(data_file, 'r') as df:
        input_data = []
        labels = []
        for line in df:
            input = [int(x) for x in line.strip().replace('\t', ' 1 ').split()] #[map(int, x.split()) for x in line.strip().split('\t')]
            label = input[1:] + [eos]
1
            if len(input) > max_len:
                continue
            else:
                padding = [pad for i in range(max_len - len(input))]
                input += padding
                label += padding

            print input
            print label

    return np.array(input_data), np.array(labels)

read_data(SMALL_FILE)
