import torch

def make_optimizer(parameters, config):
    return torch.optim.Adam(
        parameters, lr=config["training_config"]["learning_rate"],
        weight_decay=config["training_config"]["weight_decay"])