__author__ = 'adeb'

import sys
import ConfigParser

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import nibabel

import nn
import trainer
from dataset import ConverterMriPatch, create_img_from_pred
from pick_voxel import *
from pick_patch import *
from pick_target import *
from dataset import Dataset, crop_image



if __name__ == '__main__':

    patch_width = 29
    n_classes = 139

    ### Load the network
    net = nn.Network2(patch_width, n_classes)
    net.load_parameters("net3.net")

    ### Create the patches
    file = [('../data/miccai/mri/1025.nii', '../data/miccai/label/1025.nii')]
    mri = nibabel.load(file[0][0]).get_data().squeeze()
    lab = nibabel.load(file[0][1]).get_data().squeeze()
    mri, lab = crop_image(mri, lab)
    select_region = SelectPlaneXZ(100)
    extract_voxel = ExtractVoxelAll(1)
    pick_vx = PickVoxel(select_region, extract_voxel)
    pick_patch = PickPatchParallelOrthogonal(1)
    pick_tg = PickTgCentered()
    dataset = Dataset()
    dataset.populate_from(file, n_classes, patch_width, True, 1, pick_vx, pick_patch, pick_tg)
    net.scale_dataset(dataset)

    # slice1 = mri[:,:,100]
    # mri_rot = rotate(mri, 20, axes=(0,1))
    # slice2 = mri_rot[:,:,100]

    # plt.imshow(slice1)
    # plt.show()
    #
    # plt.imshow(slice2)
    # plt.show()

    ### Predict the patches
    pred1 = net.predict(dataset.patch)
    pred12 = np.argmax(pred1, axis=1)
    err = trainer.Trainer.error_rate(pred1, dataset.tg)
    print err
    img_true = lab[:, 100, :]
    img_pred = create_img_from_pred(dataset.vx[:, (0, 2)], pred12, img_true.shape)

    file_name = "test.png"
    plt.imshow(img_pred)
    plt.savefig('../images/pred_' + file_name)

    plt.imshow(img_true)
    plt.savefig('../images/true_' + file_name)

    plt.imshow(img_pred != img_true)
    plt.savefig('../images/diff_' + file_name)