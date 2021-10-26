from .pwc_net import PWCNet
from .gma import GMA


class ModelFactory:
    def get_model(self, model, mdl_cfg, reuse_mdl):
        if model == 'pwc_net':
            return PWCNet.get_instance(mdl_cfg, reuse_mdl)
        elif model == 'gma':
            return GMA.get_instance(mdl_cfg, reuse_mdl)
        else:
            msg = f'Chosen optical flow model ({model}) not supported.'
            raise ValueError(msg)
