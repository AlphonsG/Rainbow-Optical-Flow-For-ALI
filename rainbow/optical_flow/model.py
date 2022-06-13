from abc import ABCMeta, abstractmethod


class Model:
    """Interface for optical flow models.

    Optical flow model classes must implement this class.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, model_cfg):
        """Initializes the model.

        Args:
            model_cfg (dict): The configuration of the optical flow model.

        Raises:
            NotImplementedError: Child class does not implement method.
        """
        raise NotImplementedError

    @abstractmethod
    def load(self):
        """Loads the optical flow model into memory.

        Raises:
            NotImplementedError: Child class does not implement method.
        """

    @abstractmethod
    def prepare(self, imgs):
        """Returns preprocessed images as a (CPU) torch.Tensor.

        Prepares images for optical flow prediction using the '.run()' method
        by performing any necessary image preprocessing, such as resizing,
        and converting them to a (CPU) tensor.

        Args:
            imgs: A list of images.

        Returns:
            torch.Tensor: A (CPU) tensor of preprocessed images.
        """
        raise NotImplementedError

    @abstractmethod
    def run(self, imgs):
        """Returns the optical flow of an image sequence as a (CPU)
           torch.Tensor.

        Args:
            imgs (torch.Tensor): The input image sequence.

        Returns:
            torch.Tensor: A (CPU) tensor of the computed optical flow.

        Raises:
            NotImplementedError: Child class does not implement method.
        """
        raise NotImplementedError
