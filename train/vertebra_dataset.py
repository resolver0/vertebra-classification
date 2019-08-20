#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from PIL import Image

import torchvision
from torch.utils.data import Dataset
import custom_transforms as custom_t


def get_transforms(crop_factor, h_flip_prob, v_flip_prob, mean, std,
                   center_crop=True):
    train_transforms = torchvision.transforms.Compose([
        custom_t.Crop(crop_factor, center_crop=center_crop),
        custom_t.RandomHorizontalFlip(h_flip_prob),
        custom_t.RandomVerticalFlip(v_flip_prob),
        custom_t.ToTensor(),
        custom_t.Normalize(mean=mean, std=std)
    ])
    test_transforms = torchvision.transforms.Compose([
        custom_t.Crop(crop_factor, center_crop=center_crop),
        custom_t.ToTensor(),
        custom_t.Normalize(mean=mean, std=std),
    ])
    return train_transforms, test_transforms


class VertebraDataset(Dataset):
    def __init__(self, json_path, transform=None):
        with open(json_path) as f:
            self.samples = json.load(f)

        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        labels = [int(x['label']) for x in self.samples[idx]['annotation']]
        bboxes = [x['bbox'] for x in self.samples[idx]['annotation']]
        img = Image.open(self.samples[idx]['img_path'])
        sample = {'img': img, 'bboxes': bboxes, 'labels': labels}

        if self.transform is not None:
            sample = self.transform(sample)
        else:
            sample = custom_t.ToTensor()(sample)

        return sample['img'], {'boxes': sample['bboxes'],
                               'labels': sample['labels']}

    @staticmethod
    def collate_fn(batch):
        return tuple(zip(*batch))