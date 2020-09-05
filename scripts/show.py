#!/usr/bin/python3
import os
import h5py
import argparse
import numpy as np
from matplotlib import pyplot as plt
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__)))

parser = argparse.ArgumentParser("Script to visualize hdf5 files")

parser.add_argument('hdf5_paths', help='Path to hdf5 file/s')
args = parser.parse_args()

print(args.hdf5_paths)
for fname in os.listdir(args.hdf5_paths):
    print('fname: ', fname)
    data = h5py.File(args.hdf5_paths+'/'+fname, 'r+')
    try:
        print(np.asarray(data['campose']))
    except KeyError:
        print("campose do not saved")
    try:
        print(np.asarray(data['light_states']))
    except KeyError:
        print("lightpose do not saved")
        
    plt.imshow(data['colors'])
    plt.show()
