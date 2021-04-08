from .pwc_net import PWCNet


class ModelFactory:
    def get_model(self, model, mdl_cfg, reuse_mdl):
        if model == 'pwc_net':
            return PWCNet.get_instance(mdl_cfg, reuse_mdl)
        else:
            msg = ('Chosen optical flow model ({}) not supported.'
                   ).format(model)
            raise ValueError(msg)