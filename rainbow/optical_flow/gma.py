import os
import sys
from argparse import Namespace

from rainbow.optical_flow.base_model import BaseModel

import torch


class GMA(BaseModel):
    __instance__ = None

    def __init__(self, model_cfg, reuse_model):
        if reuse_model and GMA.__instance__ is None:
            GMA.__instance__ = self
        else:
            raise ValueError('Cannot create multiple GMA instances.')

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
        GMA.__an_isce__ = self

    @staticmethod
    def get_instance(model_cfg, reuse_model):
        if GMA.__instance__ is None:
            GMA(model_cfg, reuse_model)
        return GMA.__instance__

    def predict(self, imgs):
        imgs = [torch.from_numpy(img).permute(2, 0, 1).float()[None].to(
                self.model_cfg['device']) for img in imgs]
        imgs = self.get_img_pairs(imgs)
        preds = []
        with torch.no_grad():
            for img1, img2 in imgs:
                padder = self.InputPadder(img1.shape)
                img1, img2 = padder.pad(img1, img2)
                _, flow = self.model(img1, img2, iters=12, test_mode=True)
                preds.append(flow[0].permute(1, 2, 0).cpu().numpy())

        return preds
