config_format = {
    "data":{
        "batch_size": int,
        "shuffle": bool
    },
    "training":{
        "num_epochs": int,
        "learning_rate": float,
        "weight_decay": float,
    },
    "model":{
        "model_dir": "opath",
        "model_name": "opath",
        "dropout2d": float,
        "dropout": float
    },
    "scheduler":{
        "n_iter_restart": int,
        "factor_increase": int,
        "min_lr": float
    }
}