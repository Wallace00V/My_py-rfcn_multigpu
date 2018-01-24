#!/usr/bin/env python
#coding=utf-8
# --------------------------------------------------------
# R-FCN
# Copyright (c) 2016 Yuwen Xiong
# Licensed under The MIT License [see LICENSE for details]
# Written by Yuwen Xiong
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""

import _init_paths
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import caffe, os, sys, cv2
import argparse

#CLASSES = ('__background__',
#            '13001','1698','13000','110045','110046','13002','1431','460', '110035','3710',
#                         '529','2214','3499','1464','2672','2370','110034','3560','13004','1501','4013','534', '3889', '13003', '110049' )

CLASSES = tuple(np.loadtxt('../classes561.txt',str))
NETS = {'ResNet-101': ('ResNet-101',
                  'resnet101_rfcn_final.caffemodel'),
        'ResNet-50': ('ResNet-50',
                  'resnet50_rfcn_iter_2100000.caffemodel')}



def vis_detections(im, class_name, dets, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    im = im[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(im, aspect='equal')
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]

        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor='red', linewidth=3.5)
            )
        ax.text(bbox[0], bbox[1] - 2,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor='blue', alpha=0.5),
                fontsize=14, color='white')

    ax.set_title(('{} detections with '
                  'p({} | box) >= {:.1f}').format(class_name, class_name,
                                                  thresh),
                  fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.draw()

def demo(net):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    '''im_file = os.path.join(cfg.DATA_DIR, 'demo', image_name)
    im = cv2.imread(im_file)'''
    cap = cv2.VideoCapture(-1)
    cap.set(3,1000)
    cap.set(4,600)

    # Detect all object classes and regress object bounds
    '''timer = Timer()
    timer.tic()
    scores, boxes = im_detect(net, im)
    timer.toc()
    print ('Detection took {:.3f}s for '
           '{:d} object proposals').format(timer.total_time, boxes.shape[0])
'''
    while(1):
        tic = time.time()
        _,im = cap.read()
        #im = cv2.flip(im,1)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        # Visualize detections for each class
        scores, boxes = im_detect(net, im)
        CONF_THRESH = 0.8
        NMS_THRESH = 0.3
        print '\n'*20

        cv2_im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im)
        draw = ImageDraw.Draw(pil_im)
        font = ImageFont.truetype("../simhei.ttf", 18, encoding="utf-8")

        for cls_ind, cls in enumerate(CLASSES[1:]):
            cls_ind += 1 # because we skipped background
            cls_boxes = boxes[:, 4:8]
            cls_scores = scores[:, cls_ind]
            dets = np.hstack((cls_boxes,
                              cls_scores[:, np.newaxis])).astype(np.float32)
            keep = nms(dets, NMS_THRESH)
            dets = dets[keep, :]
            '''vis_detections(im, cls, dets, thresh=CONF_THRESH)'''
            inds = np.where(dets[:, -1] >= 0.7)[0]
            #print inds
            for i in inds:
                # list_df += '\n' + cls + '\n'
                text = cls + ':' + str(dets[i, 4])
                if sku_number2name.has_key(cls):
                    chinese_text =  text + sku_number2name[cls]
                else:
                    chinese_text =  text + u'未登记'
                bbox = dets[i, :4]
                #cv2.rectangle(im, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), thickness=3)
                #cv2.putText(im, text, (bbox[0], bbox[1]), 0, 1, (255, 0, 0), 2)

                draw.text((bbox[0], bbox[1]), chinese_text, (0, 0, 0), font=font)
                draw.rectangle((bbox[0], bbox[1],bbox[2], bbox[3]),outline=(255,0,0))
                print (text)

        cv2_text_im = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
        cv2.imshow("capture", cv2_text_im)
        #print 'times: {:.3f} s'.format(time.time()-tic)

    cap.release()
    cv2.destroyAllWindows()

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Faster R-CNN demo')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
                        help='Use CPU mode (overrides --gpu)',
                        action='store_true')
    parser.add_argument('--net', dest='demo_net', help='Network to use [ResNet-101]',
                        choices=NETS.keys(), default='ResNet-50')

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    import time
    from PIL import Image,ImageDraw,ImageFont
    import pickle as pkl
    with open('../sku_name.pkl', 'r') as f:
        sku_number2name = pkl.load(f)

    cfg.TEST.HAS_RPN = True  # Use RPN for proposals

    args = parse_args()

    prototxt = os.path.join(cfg.MODELS_DIR, NETS[args.demo_net][0],
                            'rfcn_end2end', 'test_agnostic.prototxt')
    caffemodel = os.path.join(cfg.DATA_DIR, 'rfcn_models',
                              NETS[args.demo_net][1])

    if not os.path.isfile(caffemodel):
        raise IOError(('{:s} not found.\n').format(caffemodel))

    if args.cpu_mode:
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()
        caffe.set_device(args.gpu_id)
        cfg.GPU_ID = args.gpu_id
    net = caffe.Net(prototxt, caffemodel, caffe.TEST)

    print '\n\nLoaded network {:s}'.format(caffemodel)

    # Warmup on a dummy image
    im = 128 * np.ones((300, 500, 3), dtype=np.uint8)
    for i in xrange(2):
        _, _= im_detect(net, im)

    '''im_names = ['000456.jpg', '000542.jpg', '001150.jpg',
                '001763.jpg', '004545.jpg']
    for im_name in im_names:
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Demo for data/demo/{}'.format(im_name)
        demo(net, im_name)

    plt.show()'''
    demo(net)