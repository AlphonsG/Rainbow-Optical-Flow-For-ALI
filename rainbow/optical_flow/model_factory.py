from .gma import GMA


class ModelFactory:
    """Factory for initializing optical flow models.
    """
    def get_model(self, model, mdl_cfg, reuse_mdl):
        """Initializes a supported optical flow model.

        Args:
            model (string): The name of the optical flow model.
            mdl_cfg (dict): The configuration of the optical flow model.
            reuse_mdl (bool): If True, multiple calls of this function
                with the same model name will return the same optical model
                instance.

        Raises:
            ValueError: The chosen optical flow model is not supported.

        Returns:
            BaseModel: Supported optical flow model.
        """
        if model == 'gma':
            return GMA.get_instance(mdl_cfg, reuse_mdl)
        else:
            msg = f'Chosen optical flow model ({model}) not supported.'
            raise ValueError(msg)
