import os
import sys
import urllib
import warnings
from argparse import Namespace
from copy import deepcopy

import imutils

from rainbow.optical_flow.model import Model
from rainbow.optical_flow.optical_flow import get_img_pairs

import torch

MIN_DIMS = (284, 121)
CHECKPOINTS_BASE_URL = 'https://github.com/AlphonsG/GMA/raw/main/checkpoints/'


class GMA(Model):
    """Optical flow model from "Learning to Estimate Hidden Motions with Global
       Motion Aggregation" by Jiang et. al (https://github.com/zacjiang/GMA).
    """

    def __init__(self, model_cfg):
        """See base class."""
        gma_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'third_party', 'gma', 'core')
        sys.path.insert(1, gma_dir)
        from network import RAFTGMA
        from utils.utils import InputPadder
        self.RAFTGMA = RAFTGMA
        self.InputPadder = InputPadder
        self.args = Namespace(**model_cfg)
        self.model_cfg = model_cfg

    def load(self):
        """See base class."""
        self.model = torch.nn.DataParallel(self.RAFTGMA(self.args))
        if os.path.isfile(self.model_cfg['model']):
            self.model.load_state_dict(torch.load(self.model_cfg['model'],
                                  map_location=torch.device(
                                      self.model_cfg['device'])))
        else:
            checkpoint_url = CHECKPOINTS_BASE_URL + self.model_cfg['model']
            try:
                self.model.load_state_dict(torch.hub.load_state_dict_from_url(
                    checkpoint_url, map_location=torch.device(
                    self.model_cfg['device'])))
            except urllib.error.URLError as e:
                msg = ('\nERROR: The optical flow model checkpoint specified '
                       f'in the YAML config file ({self.model_cfg["model"]}) '
                       'is not a local file, and the attempt to download it '
                       f'from {CHECKPOINTS_BASE_URL} for local installation '
                       f'failed ({str(e)}).')
                print(msg)
                exit(1)

        self.model = self.model.module
        self.model.to(self.model_cfg['device'])
        self.model.eval()

    def prepare(self, imgs):
        """See base class."""
        imgs = deepcopy(imgs)

        # Resize images to minimum dimensions, if necessary.
        for i, img in enumerate(imgs):
            for j, kv in zip([0, 1], [{'height': MIN_DIMS[0]},
                                      {'width': MIN_DIMS[1]}]):
                if img.shape[j] < MIN_DIMS[j]:
                    img = imutils.resize(img, **kv)
            imgs[i] = img

        imgs = [torch.from_numpy(img).permute(2, 0, 1).float()[None] for img
                in imgs]

        # Pad images, if necessary.
        padder = self.InputPadder(imgs[0].shape)
        imgs = [padder.pad(img) for img in imgs]
        imgs = get_img_pairs(imgs)
        imgs = torch.stack([torch.stack(i) for i in imgs])

        return imgs

    def run(self, imgs):
        """See base class."""
        imgs = imgs.to(self.model_cfg['device'])
        with torch.no_grad(), warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=UserWarning)
            preds = [self.model(imgs[i, 0, ...], imgs[i, 1, ...],
                     test_mode=True)[1][0].permute(1, 2, 0).detach().cpu() for
                     i in range(0, imgs.shape[0])]

        return torch.stack(preds)
