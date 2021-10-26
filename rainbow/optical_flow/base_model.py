from abc import ABCMeta, abstractmethod


class BaseModel:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_instance(model_cfg, reuse_model):
        raise NotImplementedError

    @abstractmethod
    def predict(self):
        raise NotImplementedError

    def get_img_pairs(self, imgs):
        img_pairs = []
        for i in range(0, len(imgs) - 1):
            img_pairs.append((imgs[i], imgs[i + 1]))

        return img_pairs
