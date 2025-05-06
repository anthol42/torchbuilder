import torch
from torch.utils.data import Dataset
from torchvision import datasets
from torchvision.transforms import ToTensor
import matplotlib.pyplot as plt


def make_dataset(config):
    training_data = datasets.MNIST(
        root=config["data"]["path"],
        train=True,
        download=True,
        transform=ToTensor()
    )

    test_data = datasets.MNIST(
        root=config["data"]["path"],
        train=False,
        download=True,
        transform=ToTensor()
    )
    return training_data, test_data

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    train, test = make_dataset({})
    img, label = train[0]
    plt.imshow(img.squeeze(0))
    plt.show()