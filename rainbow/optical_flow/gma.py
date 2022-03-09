import os
import sys
import urllib
import warnings
from argparse import Namespace

import imutils

from rainbow.optical_flow.base_model import BaseModel

MIN_DIMS = (284, 121)
CHECKPOINTS_BASE_URL = 'https://github.com/AlphonsG/GMA/raw/main/checkpoints/'


class GMA(BaseModel):
    """Optical flow model from "Learning to Estimate Hidden Motions with Global
    Motion Aggregation" by Jiang et. al (https://github.com/zacjiang/GMA).
    """
    __instance__ = None

    def __init__(self, model_cfg, reuse_model):
        """See base class."""
        gma_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'third_party', 'gma', 'core')
        sys.path.insert(1, gma_dir)
        from network import RAFTGMA
        from utils.utils import InputPadder
        import torch
        self.InputPadder = InputPadder
        self.torch = torch
        args = Namespace(**model_cfg)
        model = self.torch.nn.DataParallel(RAFTGMA(args))

        if os.path.isfile(model_cfg['model']):
            model.load_state_dict(self.torch.load(model_cfg['model'],
                                  map_location=self.torch.device(
                                      model_cfg['device'])))
        else:
            checkpoint_url = CHECKPOINTS_BASE_URL + model_cfg['model']
            try:
                model.load_state_dict(self.torch.hub.load_state_dict_from_url(
                    checkpoint_url, map_location=self.torch.device(
                        model_cfg['device'])))
            except urllib.error.URLError as e:
                msg = ('\nERROR: The optical flow model checkpoint specified '
                       f'in the YAML config file ({model_cfg["model"]}) is '
                       'not a local file, and the attempt to download it '
                       f'from {CHECKPOINTS_BASE_URL} failed ({str(e)}).')
                print(msg)
                exit(1)

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

        imgs = [self.torch.from_numpy(img).permute(2, 0, 1).float()[None].to(
                self.model_cfg['device']) for img in imgs]
        imgs = self.get_img_pairs(imgs)

        # Pad images, if necessary.
        padder = self.InputPadder(imgs[0][0].shape)
        imgs = [(padder.pad(img1, img2)) for img1, img2 in imgs]

        preds = []
        with self.torch.no_grad():
            for img1, img2 in imgs:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=UserWarning)
                    _, flow = self.model(img1, img2, iters=12, test_mode=True)
                preds.append(flow[0].permute(1, 2, 0).cpu().numpy())

        return preds
