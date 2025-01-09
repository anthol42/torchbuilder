import os.path
import glob
import numpy as np
import torch

class InvalidConfigFileException(Exception):
    pass

def _recursive_check(config, expected, verify_path, verify_out_path):
    if config.keys() != expected.keys():
        raise InvalidConfigFileException(f"Config file is invalid. missing keys: "
                                         f"{set(expected.keys()) - set(config.keys())} || and have these key that are "
                                         f"unknown: {' '.join(set(config.keys()) - set(expected.keys()))}")
    else:
        for key, value in expected.items():
            if isinstance(value, str):
                if value == "ipath" and verify_path:
                    if "/*" in config[key]:
                        if len(glob.glob(config[key], recursive = True)) == 0:
                            raise InvalidConfigFileException(f"Config file contains invalid input path at key: {key}")
                    else:
                        if not os.path.exists(config[key]):
                            raise InvalidConfigFileException(f"Config file contains invalid input path at key: {key}")
                elif value == "opath" and verify_out_path:
                    if not os.path.exists(config[key]):
                        raise InvalidConfigFileException(f"Config file contains invalid output path at key: {key}")
            elif isinstance(value, dict):
                _recursive_check(config[key], expected[key], verify_path, verify_out_path)
            elif isinstance(value, tuple):
                isOk = False
                for el_type in value:
                    if isinstance(config[key], el_type):
                        isOk = True

                if not isOk:
                    raise InvalidConfigFileException(f"Config file has value of type {type(config[key])} where it is "
                                                 f"supposed to be {value} at key {key}.")
            else:
                if not isinstance(config[key], value) and config[key] is not None:
                    raise InvalidConfigFileException(f"Config file has value of type {type(config[key])} where it is "
                                                    f"supposed to be {value} at key {key}.")



def verify_config(config: dict, expected: dict, verify_path=True, verify_out_path=False):
    """
    This function will raise an exception if the given config file does not conform to the expected config structure.
    :param config: The parsed yaml config file
    :param expected: The expected structure (Dict with classes as value of keys)
    :return:
    """
    _recursive_check(config, expected, verify_path, verify_out_path)


def load_model(model: torch.nn.Module, load_path: str):
    """
    Load the model
    :param model: The randomly initialized model.
    :param load_path: The path where to find the state_dict.  Must point to a pth file that contains
            a key: model_state_dict
    :return: The initialized model
    """
    data = torch.load(load_path, map_location=torch.device('cpu'))
    model.load_state_dict(data["model_state_dict"])
    return model


def get_trainable_weights(model: torch.nn.Module):
    """
    Return a reference to every trainable weight of the model.  (Including bias).
    :param model: The initialized model we want to get a reference to its weights.
    :return: weights list, bias list, module_name list, whole: dictionary containing weights/bias indexed by name
    """
    weights = []
    bias = []
    layer_names = []
    whole = {
        "Weights": {},
        "Bias": {}
    }
    for name, module in model.named_modules():
        if hasattr(module, "weight"):
            added = False
            if module.weight.requires_grad:
                weights.append(module.weight)
                whole["Weights"][name] = module.weight
                added = True
            if hasattr(module, "bias"):
                if module.bias is not None and module.bias.requires_grad:
                    bias.append(module.bias)
                    whole["Bias"][name] = module.bias
                    added = True

            if added:
                layer_names.append(name)

    return weights, bias, layer_names, whole

def clean_dict(dictionary: dict):
    """
    The method remove the keys that have None as value.
    It also removes default hyperparameters such as config, experiment and dropout
    WARNING: Dictionary must not have nested dictionaries !
    :param dictionary: The dictionary to clean
    :return: The cleaned dict
    """
    out = dictionary.copy()
    out.pop("config")
    out.pop("experiment")
    out.pop("debug")
    for key, value in dictionary.items():
        if value is None:
            out.pop(key)
    return out


def angular(a: torch.Tensor, b: torch.Tensor) -> float:
    """
    Calculate the angle between two multidimensional vectors.
    Formula: arccos(a.b/(||a|| * ||b||)) where . is dot product and * is a multiplication.
    :param a: The first vector
    :param b: The second vector
    :return: The angle in radians
    """
    return np.arccos(
        a @ b / (torch.linalg.vector_norm(a) * torch.linalg.vector_norm(b))
    )

def get_device():
    """
    Find which device is the optimal device for training.  Priority order: cuda, mps, cpu
    Returns: the device
    """
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")

if __name__ == "__main__":
    pass
