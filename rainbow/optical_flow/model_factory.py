from .gma import GMA


class ModelFactory:
    def get_model(self, model, mdl_cfg, reuse_mdl):
        """Initializes a supported optical flow model.

        Args:
        if model == 'gma':
            return GMA.get_instance(mdl_cfg, reuse_mdl)
        else:
            msg = f'Chosen optical flow model ({model}) not supported.'
            raise ValueError(msg)
