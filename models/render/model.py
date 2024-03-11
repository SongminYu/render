import random

from Melodie import Model
from Melodie import set_seed


class RenderModel(Model):

    @staticmethod
    def set_seed():
        set_seed(0)
        random.seed(0)
