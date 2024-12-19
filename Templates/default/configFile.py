import yaml
from .functions import verify_config
from .color import Color, ResetColor

class _Config:
    def __init__(self, internal: dict, name: str = ""):
        self.__internal = internal
        self.__name = name
        self.__running_stats = {}

        for key, value in self.__internal.items():
            if isinstance(value, dict):
                self.__internal[key] = _Config(self.__internal[key], name=key)
            self.__running_stats[key] = {"write": 1, "read": 0}

    def __contains__(self, item):
        return item in self.__internal

    def __getitem__(self, key):
        data = self.__internal[key]
        if not isinstance(data, _Config):
            self.__running_stats[key]["read"] += 1
        return data

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            self.__internal[key] = _Config(value, name=key)
        else:
            if key in self.__running_stats:
                self.__internal[key] = value
                self.__running_stats[key]["write"] += 1
            else:
                self.__running_stats[key] = {"write": 1, "read": 0}

    # @property
    # def __dict__(self):
    #     """
    #     This method is used to be compatible with the vars() function
    #     :return: A dictionary representation of itself
    #     """
    #     return self._todict()

    def dict(self):
        return self._todict()

    def _stat_txt(self, offset: int = 2):
        max_len = len(max(self.__internal.keys(), key=lambda x: len(x))) + 1    # offset
        s = "<Config>\n"
        for key, value in self.__internal.items():
            if isinstance(value, _Config):
                s += f"{' '*(offset)}{key}{' '*(max_len - len(key))}: {value._stat_txt(max_len + offset + 3)}\n"
            else:
                s += f"{' '*(offset)}{key}{' '*(max_len - len(key))}: writes: {self.__running_stats[key]['write']}, " \
                     f"reads: {self.__running_stats[key]['read']}\n"

        return s

    def _unused_var(self, parent: str = ""):
        unused_var = []
        for key, value in self.__internal.items():
            if isinstance(value, _Config):
                unused_var += value._unused_var(key)
            else:
                if self.__running_stats[key]['read'] == 0:
                    if parent != "":
                        unused_var.append(f"{parent}.{key}")
                    else:
                        unused_var.append(key)
        return unused_var

    def stats(self):
        """
        Get the statistics of how many reads and writes for each variable (leaf) in the config file.
        :return: A multiline string representing the stats.
        """
        s = self._stat_txt()
        s_split = s.split("\n")
        max_len = len(max(s_split, key=lambda x: len(x)))
        s_split[0] = "<ConfigStats>" + "-" * (max_len - 8)
        unused = self._unused_var()
        if len(unused) > 0:
            warning_message = f"\nWARNING: You have {len(unused)} unused variables in your config file.\n" \
                              f"Consider removing them:\n{unused}\n"
        else:
            warning_message = "\nYou have 0 unused variable:)\n"
        s_split.insert(1, warning_message)
        s_split[-1] = "-" * max_len
        return "\n".join(s_split)

    def _txt(self, offset: int = 2):
        max_len = len(max(self.__internal.keys(), key=lambda x: len(x))) + 1    # offset
        s = "<Config>\n"
        for key, value in self.__internal.items():
            if isinstance(value, _Config):
                s += f"{' '*(offset)}{key}{' '*(max_len - len(key))}: {value._txt(max_len + offset + 3)}\n"
            else:
                s += f"{' '*(offset)}{key}{' '*(max_len - len(key))}: {value}\n"

        return s

    def __str__(self):
        """
        :return: The config file as a string yaml-like
        """
        d = self._todict()
        s = yaml.dump(d)
        s_split = s.split("\n")
        max_len = len(max(s_split, key=lambda x: len(x)))
        s_split[0] = "<Config>" + "-" * (max_len - 8)
        s_split[-1] = "-" * max_len
        return "\n".join(s_split)

    def __repr__(self):
        return "<ConfigFile>"

    def _todict(self):
        d = {}
        for key, value in self.__internal.items():
            if isinstance(value, _Config):
                d[key] = value._todict()
            else:
                d[key] = value
        return d

    def dump(self, path: str):
        """
        This method will save the config in a yaml format to the given path.
        :param path: The path to where to save the config file
        :return: None
        """
        config = self._todict()
        print(config)
        with open(path, "w") as file:
            file.write(yaml.dump(config))

    def save_stats(self, path: str):
        """
        This function will save the statistics of how many writes and reads to a file.
        :param path: The path of where to save the file
        :return: None
        """
        with open(path, "w") as file:
            file.write(self.stats())


class ConfigFile(_Config):
    """
    This class is a representation of a YAML configuration file.  It is as easy to use as a dictionary.
    It supports internal loading (With type and path verification)  and saving (dumping).  In addition, it will record
    if each key is used, and how many times.  This way, you can see if there are unused keys and remove them.

    How it works:
    1. Create an expected config file format: a dictionary analog to the expected config file structure with its values
        being python types(classes).
    2. Create the object by specifying the path to the file and the expected config format.
    3. Use it like any dictionary
    4. At the end of the script, you can print or save to a file the statistics (How many times each key as been
        written and read.)

    Example:
        >>> config_format = {
                "data": {
                    "train_path": "ipath",
                    "valid_path": "ipath",
                    "test_path": "ipath",
                    "shuffle": bool,
                },
                "model_config": {
                    "model_dir": "opath",
                    "name": str,
                },
                "training": {
                    "num_epochs": int,
                    "learning_rate": float,
                    "weight_decay": float,
                    "batch_size": int
                },
                "checkpoint_rate": int,
                "results_path": "opath"
        >>> }

        >>> conf = ConfigFile("configs/config.yml", config_format)

        >>> # Use it like any other dictinary

        >>> lr = conf["training"]["learning_rate"]

        >>> # Print the statistics

        >>> print(conf.stats())

    Config_format:
        The leafs of the config file dictionary can be:

        Python Class
            -float
            -int
            -str
            -list

        Tuples of python class ex: (str, float):
            This means that it only accepts that the value is a string OR a float

        string keywords:
            'ipath': Meaning input path.  If the parameter verify path is set to true, it will verify each path that
                     has this tag.
            'opath': Meaning output path.  This means that the expected value is a path, but that will be used as
                        output.  So it won't be verifed.
    """
    def __init__(self, file_path: str, config_format: dict = None, verify_path: bool = True):
        """

        :param file_path: The path to the config file.
        :param config_format: A dictionary analog to the expected config file, but the values are the expected type
                              instead of ral values.
        :param verify_path: Whether to verify input path.
        """
        with open(file_path, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        if config_format is not None:
            verify_config(config, config_format, verify_path=verify_path)

        super().__init__(config)

    def override_config(self, kwargs: dict, exit_on_error: bool = True):
        """
        Override corresponding parameters in the config file.
        Key format:
            config.key1.key2.<...>
        Corresponding to:
            key1:
                key2:
                    ...
        :param kwargs: The keys specifying the path to the parameter to change
        :param exit_on_error: Whether to warn the user and exit if a key is invalid or ignore.
        :return: None
        """
        key: str
        for key, value in kwargs.items():
            if key.startswith("config."):
                path = key[7:].split(".")
                sub_config = self
                for sub_key in path[:-1]:
                    if sub_key in sub_config:
                        sub_config = sub_config[sub_key]
                    else:
                        if exit_on_error:
                            print(f"{Color(203)}Invalid key: {sub_key} at {key}!{ResetColor()}")
                            exit(-1)
                if path[-1] in sub_config:
                    sub_config[path[-1]] = value
                else:
                    if exit_on_error:
                        print(f"{Color(203)}Invalid key: '{path[-1]}' at '{key}'!  Impossible to override the config.{ResetColor()}")
                        exit(-1)


if __name__ == "__main__":
    config_format = {
        "data": {
            "window_size": int,
            "step_size": int,
            "train_path": "ipath",
            "valid_path": "ipath",
            "valid_mask_path": "ipath",
            "test_path": "ipath",
            "test_mask_path": "ipath",
            "shuffle": bool,
            "crop_border": int,
        },
        "model_config": {
            "model_dir": "opath",
            "backbone_name": str,
            "conv3_only": bool,
            "hidden_ratio": float,
            "flow_steps": int
        },
        "training": {
            "num_epochs": int,
            "learning_rate": float,
            "weight_decay": float,
            "validation_interval": int,
            "batch_size": int
        },
        "checkpoint_rate": int,
        "active_learning": {
            "window_size": int,
            "step_size": int,
            "uncertainty_score_path": str
        },
        "Evaluation": {
            "heatmap_path": "opath",
            "results_path": "opath",
        }
    }
    conf = ConfigFile("../configs/config.yml", config_format, verify_path=False)
    heat_path = conf["Evaluation"]["heatmap_path"]
    conf["Evaluation"]["results_path"] = "..."
    print(dict(conf))