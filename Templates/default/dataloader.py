from data.datasets.dataset import make_dataset
from torch.utils.data import DataLoader

def make_dataloader(config):
    train_ds, test_ds = make_dataset(config)
    train_dataloader = DataLoader(train_ds, batch_size=config["data"]["batch_size"], shuffle=config["data"]["shuffle"])
    test_dataloader = DataLoader(test_ds,
                                 batch_size=config["data"]["batch_size"], shuffle=False)
    return train_dataloader, test_dataloader, None


