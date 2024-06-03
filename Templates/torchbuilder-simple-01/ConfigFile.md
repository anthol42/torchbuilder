# ConfigFile
## Description
This class is designed specifically to facilitate the interaction with YAML config files.
It loads, analyze, verify and dumps config file automatically.  In addition, it is aas easy 
to use as a dictionary.  It also calculates the number of time each key is read and warns you 
if a key is not used.  When config files and the project becomes big, it is hard to know if 
each key is still in used.  If not, one might think he is changing parameters but isn't changing
anything.  This could lead to undesirable comportment and maybe even bugs.  This is why
this object will warn you if such keys aren't used.

## How it works
1. Initiate the configFile object with the path to the file and the config format.
2. Use it like any dictionary in your code
3. At the end of the script, print the stats to know if a key wasn't used.

## Examples
```python
config_format = {
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
}
config = ConfigFile("configs/config.yml", config_format, verify_path=True)

# Use it like any other dictinary
lr = config["training"]["learning_rate"]

# Print the statistics
print(config.stats())
```


## Config Format
Config format is a dictionary analog to the expected config file, but the leafs are python
types or keyword as string, instead of actual values.

### The leafs of the config file dictionary can be:

Any python base class
- float
- int
- str
- list
- Tuples of python class ex: (str, float) would mean that strings or floats are accepted
- 'ipath': This tells the ConfigFile that it is an input path.  If the input path option is checke,
it will verify if the path exists.
- 'opath': This tells the ConfigFile that it is suppose to be an output path.