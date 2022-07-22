import numpy as np
import pandas as pd
import plotly.express as px


class MyDataset(Dataset):
    def __init__(self,
                 data,
                 label,
                 transform=None):
        self.data = data
        self.label = label
        self.transform = transform

    def __getitem__(self, index):
        return self.data[index], self.label[index]

    def __len__(self):
        return len(self.data)
