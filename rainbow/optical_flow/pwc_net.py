import logging
import os
import sys
from copy import deepcopy

from rainbow.optical_flow.base_model import BaseModel


class PWCNet(BaseModel):
    __sgle_insce__, __an_isce__ = None, None

    def __init__(self, mdl_cfg, reuse_mdl):
        if reuse_mdl:
            if PWCNet.__sgle_insce__ is None:
                PWCNet.__sgle_insce__ = self
            else:
                raise ValueError('Multiple instances of same model are not '
                                 'permitted.')

        if not mdl_cfg['tf_logging']:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            logging.getLogger('tensorflow').disabled = True
            import tensorflow as tf
            tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.FATAL)

        curr_dir = os.path.abspath(os.path.dirname(__file__))
        sys.path.insert(1, os.path.join(curr_dir, 'third_party', 'pwc_net'))
        from model_pwcnet import ModelPWCNet, _DEFAULT_PWCNET_TEST_OPTIONS

        model_opts = deepcopy(_DEFAULT_PWCNET_TEST_OPTIONS)
        model_opts['verbose'] = mdl_cfg['model']['opts']['verbose']
        model_opts['ckpt_path'] = mdl_cfg['model']['opts']['ckpt_path']
        model_opts['batch_size'] = mdl_cfg['model']['opts']['batch_size']
        model_opts['gpu_devices'] = mdl_cfg['model']['opts']['gpu_devices']
        model_opts['controller'] = mdl_cfg['model']['opts']['controller']
        model_opts['use_dense_cx'] = mdl_cfg['model']['opts']['use_dense_cx']
        model_opts['use_res_cx'] = mdl_cfg['model']['opts']['use_res_cx']
        model_opts['adapt_info'] = tuple(mdl_cfg['model']['opts'][
                                         'adapt_info'])
        self.model = ModelPWCNet(mode=mdl_cfg['model']['mode'],
                                 options=model_opts)
        self.model_opts = model_opts
        self.mdl_cfg = mdl_cfg

        PWCNet.__an_isce__ = self

    @staticmethod
    def get_instance(mdl_cfg, reuse_mdl):
        if reuse_mdl:
            if not PWCNet.__sgle_insce__:
                PWCNet(mdl_cfg, reuse_mdl)

            return PWCNet.__sgle_insce__

        PWCNet(mdl_cfg, reuse_mdl)

        return PWCNet.__an_isce__

    def predict(self, imgs):
        if not self.mdl_cfg['const_img_shape']:
            self.apply_adapt_info(imgs)
        img_pairs = self.get_img_pairs(imgs)
        preds = (self.model.predict_from_img_pairs(img_pairs,
                 batch_size=self.mdl_cfg['pred']['batch_size'],
                 verbose=self.mdl_cfg['pred']['verbose']))

        return preds

    def get_img_pairs(self, imgs):
        img_pairs = []
        for i in range(0, len(imgs) - 1):
            img_pairs.append((imgs[i], imgs[i + 1]))

        return img_pairs

    def apply_adapt_info(self, imgs):
        shps = [img.shape for img in imgs]
        if not shps.count(shps[0]) == len(shps):
            msg = 'Images in series have unequal shapes.'
            raise ValueError(msg)
        if shps[1] != self.model_opts['adapt_info'][1] and (
                shps[0] != self.model_opts['adapt_info']):
            self.model_opts['adapt_info'] = (1, shps[1], shps[2], 2)
            self.model = ModelPWCNet(mode=self.mdl_cfg['model']['mode'],
                                     options=self.model_opts)
