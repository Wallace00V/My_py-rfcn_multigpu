#!/usr/bin/env python

# --------------------------------------------------------
# Written by Bharat Singh
# Modified version of py-R-FCN
# --------------------------------------------------------

"""Train a Fast R-CNN network on a region of interest database."""

import _init_paths
from fast_rcnn.train_multi_gpu import get_training_roidb, train_net_multi_gpu
from fast_rcnn.config import cfg, cfg_from_file, cfg_from_list, get_output_dir
from datasets.factory import get_imdb
import datasets.imdb
import caffe
import argparse
import pprint
import numpy as np
import sys

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Train a Fast R-CNN network')
    parser.add_argument("--gpu_id", type=str, default='0,1',
                        help="List of device ids.")
    '''parser.add_argument('--solver', dest='solver',
                        help='solver prototxt',
                        default='models/pascal_voc/VGG16/faster_rcnn_end2end/solver.prototxt', type=str)'''
    parser.add_argument('--solver', dest='solver',
                        help='solver prototxt',
                        default='models/pascal_voc/ResNet-50/rfcn_end2end/solver.prototxt', type=str)
    parser.add_argument('--iters', dest='max_iters',
                        help='number of iterations to train',
                        default=2500000, type=int)
    '''parser.add_argument('--weights', dest='pretrained_model',
                        help='initialize with pretrained model weights',
                        default='data/imagenet_models/VGG16.v2.caffemodel', type=str)'''
    parser.add_argument('--weights', dest='pretrained_model',
                        help='initialize with pretrained model weights',
                        default='data/imagenet_models/ResNet-50-model.caffemodel', type=str)
    '''parser.add_argument('--cfg', dest='cfg_file',
                        help='optional config file',
                        default='experiments/cfgs/faster_rcnn_end2end.yml', type=str)'''
    parser.add_argument('--cfg', dest='cfg_file',
                        help='optional config file',
                        default='experiments/cfgs/rfcn_end2end.yml', type=str)
    '''parser.add_argument('--imdb', dest='imdb_name',
                        help='dataset to train on',
                        default='voc_2007_train', type=str)'''
    parser.add_argument('--imdb', dest='imdb_name',
                        help='dataset to train on',
                        default='voc_0712_train', type=str)
    parser.add_argument('--rand', dest='randomize',
                        help='randomize (do not use a fixed seed)',
                        action='store_true')
    parser.add_argument('--set', dest='set_cfgs',
                        help='set config keys', default=None,
                        nargs=argparse.REMAINDER)

    if len(sys.argv) == 1:
        parser.print_help()
      #  sys.exit(1)

    args = parser.parse_args()
    return args

def combined_roidb(imdb_names):
    def get_roidb(imdb_name):
        imdb = get_imdb(imdb_name)
        print 'Loaded dataset `{:s}` for training'.format(imdb.name)
        imdb.set_proposal_method(cfg.TRAIN.PROPOSAL_METHOD)
        print 'Set proposal method: {:s}'.format(cfg.TRAIN.PROPOSAL_METHOD)
        roidb = get_training_roidb(imdb)
        return roidb

    roidbs = [get_roidb(s) for s in imdb_names.split('+')]
    roidb = roidbs[0]
    if len(roidbs) > 1:
        for r in roidbs[1:]:
            roidb.extend(r)
        imdb = datasets.imdb.imdb(imdb_names)
    else:
        imdb = get_imdb(imdb_names)
    return imdb, roidb

if __name__ == '__main__':
    import os
    os.chdir('..')
    args = parse_args()

    print('Called with args:')
    print(args)

    if args.cfg_file is not None:
        cfg_from_file(args.cfg_file)
    if args.set_cfgs is not None:
        cfg_from_list(args.set_cfgs)

    gpu_id = args.gpu_id
    gpu_list = gpu_id.split(',')
    gpus = [int(i) for i in gpu_list]

    print('Using config:')
    pprint.pprint(cfg)

    if not args.randomize:
        # fix the random seeds (numpy and caffe) for reproducibility
        np.random.seed(cfg.RNG_SEED)
        #caffe.set_random_seed(cfg.RNG_SEED)

    # set up caffe

    imdb, roidb = combined_roidb(args.imdb_name)
    print '{:d} roidb entries'.format(len(roidb))

    output_dir = get_output_dir(imdb)
    print 'Output will be saved to `{:s}`'.format(output_dir)

    train_net_multi_gpu(args.solver, roidb, output_dir,
              pretrained_model=args.pretrained_model,
              max_iter=args.max_iters, gpus=gpus)
