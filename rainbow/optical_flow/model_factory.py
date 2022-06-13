from .gma import GMA


class ModelFactory:
    """Factory for initializing optical flow models.
    """
    def get_model(self, model, mdl_cfg):
        """Initializes a supported optical flow model.

        Args:
            model (string): The name of the optical flow model.
            mdl_cfg (dict): The configuration of the optical flow model.

        Raises:
            ValueError: The chosen optical flow model is not supported.

        Returns:
            BaseModel: Supported optical flow model.
        """
        if model == 'gma':
            return GMA(mdl_cfg)
        else:
            msg = f'Chosen optical flow model ({model}) not supported.'
            raise ValueError(msg)
