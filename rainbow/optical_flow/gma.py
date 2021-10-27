import os
import sys
from argparse import Namespace

import imutils

from rainbow.optical_flow.base_model import BaseModel

import torch

MIN_DIMS = (284, 121)


class GMA(BaseModel):
    """Optical flow model from "Learning to Estimate Hidden Motions with Global
    Motion Aggregation" by Jiang et. al (https://github.com/zacjiang/GMA).
    """
    __instance__ = None

    def __init__(self, model_cfg, reuse_model):
        """See base class."""
        gma_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'third_party', 'gma')
        sys.path.insert(1, os.path.join(gma_dir, 'core'))
        from network import RAFTGMA
        from utils.utils import InputPadder
        self.InputPadder = InputPadder

        args = Namespace(**model_cfg)
        model = torch.nn.DataParallel(RAFTGMA(args))

        if not os.path.isfile(model_cfg['model']):
            model_cfg['model'] = os.path.join(gma_dir, 'checkpoints',
                                              model_cfg['model'])
        if not os.path.isfile(model_cfg['model']):
            raise FileNotFoundError('Could not locate checkpoint '
                                    f'{model_cfg["model"]}.')

        model.load_state_dict(torch.load(model_cfg['model'],
                              map_location=torch.device(model_cfg['device'])))
        model = model.module
        model.to(model_cfg['device'])
        model.eval()
        self.model = model
        self.model_cfg = model_cfg
        GMA.__instance__ = self

    @staticmethod
    def get_instance(model_cfg, reuse_model):
        """See base class."""
        if GMA.__instance__ is not None:
            if not reuse_model:
                raise ValueError('Cannot create multiple GMA instances.')
        else:
            GMA(model_cfg, reuse_model)

        return GMA.__instance__

    def predict(self, imgs):
        """See base class."""
        imgs = imgs.copy()
        # Resize images to minimum dimensions, if necessary.
        for i, img in enumerate(imgs):
            for j, kv in zip([0, 1], [{'height': MIN_DIMS[0]},
                                      {'width': MIN_DIMS[1]}]):
                if img.shape[j] < MIN_DIMS[j]:
                    img = imutils.resize(img, **kv)
            imgs[i] = img

        imgs = [torch.from_numpy(img).permute(2, 0, 1).float()[None].to(
                self.model_cfg['device']) for img in imgs]
        imgs = self.get_img_pairs(imgs)

        # Pad images, if necessary.
        padder = self.InputPadder(imgs[0][0].shape)
        imgs = [(padder.pad(img1, img2)) for img1, img2 in imgs]

        preds = []
        with torch.no_grad():
            for img1, img2 in imgs:
                _, flow = self.model(img1, img2, iters=12, test_mode=True)
                preds.append(flow[0].permute(1, 2, 0).cpu().numpy())

        return preds
