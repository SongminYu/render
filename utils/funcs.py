import random
from typing import Dict, Any
import math
from utils.logger import get_logger

logger = get_logger(__name__)


def dict_sample(options: Dict[Any, float]) -> Any:
    value_sum = 0
    for key in options.keys():
        value_sum += options[key]
    for key in options.keys():
        options[key] = options[key] / value_sum if value_sum > 0 else 1

    rand = random.uniform(0, 1)
    prob_accumulated = 0
    option_chosen_key = None
    for key in options.keys():
        prob_accumulated += options[key]
        if prob_accumulated >= rand:
            option_chosen_key = key
            break
    return option_chosen_key


def dict_normalize(options: Dict[Any, float]) -> Dict[Any, float]:
    value_min = min(options.values())
    value_max = max(options.values())
    for key, value in options.items():
        options[key] = (value - value_min) / (value_max - value_min)
    return options


def dict_utility_sample(options: Dict[Any, float], utility_power: float) -> Any:
    for key, value in options.items():
        options[key] = math.exp(- value * utility_power)
    return dict_sample(options)

