from abc import ABCMeta, abstractmethod


class BaseModel:
    """Interface for optical flow models.

    Base class that optical flow model classes must inherit from.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """Initializes class instance.

        Raises:
            NotImplementedError: Child class does not implement method.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_instance(model_cfg, reuse_model):
        """Returns an instance of the class.

        Args:
            model_cfg (dict): The configuration of the optical flow model.
            reuse_model (bool): If True, multiple calls of this method
            will return the same optical model instance.
            Defaults to True.

        Raises:
            NotImplementedError: Child class does not implement method.
        """
        raise NotImplementedError

    @abstractmethod
    def predict(self):
        """Returns the optical flow of an image sequence as a list of
        numpy arrays of dimension [x, y, 2].

        Raises:
            NotImplementedError: Child class does not implement method.
        """
        raise NotImplementedError

    def get_img_pairs(self, imgs):
        """Returns image pairs.

        Duplicates every image of an image sequence, except the first and last,
        and groups pairs of images.

        Args:
            imgs (list): A list of images.

        Returns:
            list: A list of tuple images pairs.
        """
        img_pairs = []
        for i in range(0, len(imgs) - 1):
            img_pairs.append((imgs[i], imgs[i + 1]))

        return img_pairs
