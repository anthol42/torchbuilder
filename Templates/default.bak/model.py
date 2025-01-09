import torch
from torch import nn
from torchinfo import summary
import torch.nn.functional as F

class Block(nn.Module):
    def __init__(self, in_channels, out_channels, dropout):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=3, padding=1, bias=False)
        self.bnorm1 = nn.BatchNorm2d(out_channels)
        self.act1 = nn.PReLU()
        self.conv2 = nn.Conv2d(in_channels=out_channels, out_channels=out_channels, kernel_size=3, padding=1, bias=False)
        self.bnorm2 = nn.BatchNorm2d(out_channels)
        self.act2 = nn.PReLU()
        self.dropout = nn.Dropout2d(dropout)

    def forward(self, x):
        z1 = self.act1(self.bnorm1(self.conv1(x)))
        z2 = self.act2(self.bnorm2(self.conv2(z1)))
        return self.dropout(z2)

class Classifier(nn.Module):
    def __init__(self, config):
        super().__init__()
        dropout = config["model"]["dropout"]

        self.b1 = Block(1, 32, config["model"]["dropout2d"])
        self.pool1 = nn.MaxPool2d(2)

        self.b2 = Block(32, 64, config["model"]["dropout2d"])
        self.pool2 = nn.MaxPool2d(2)

        self.b3 = Block(64, 128, config["model"]["dropout2d"])
        self.pool3 = nn.MaxPool2d(2)

        self.b4 = Block(128, 256, config["model"]["dropout2d"])

        self.adaptive_pool = nn.AdaptiveAvgPool2d(1)
        self.flatten = nn.Flatten()
        self.dropout1 = nn.Dropout(dropout)
        self.fc1 = nn.Linear(256, 512, bias=False)
        self.bn1 = nn.BatchNorm1d(512)
        self.act = nn.GELU()
        self.dropout2 = nn.Dropout(dropout)
        self.fc2 = nn.Linear(512, 10)

    def forward(self, x, softmax=False):
        h = self.pool1(self.b1(x))
        h = self.pool2(self.b2(h))
        h = self.pool3(self.b3(h))
        embeddings = self.flatten(self.adaptive_pool(self.b4(h)))
        z = self.act(self.bn1(self.fc1(self.dropout1(embeddings))))
        z = self.fc2(self.dropout2(z))

        if softmax:
            z = torch.softmax(z, dim=1)
        return z


if __name__=='__main__':
    config = {"model": {"dropout2d": 0.25, "dropout": 0.5}}
    model = MICRANet(config)
    # torch.randn((64,3,))
    summary(model, input_size=(64, 1, 28, 28))