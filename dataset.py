# datasets of the project
#Imports
import numpy as np
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer

import config
import metrics
import myutils as utils


class JustificationCueDataset(Dataset):
    def __init__(self, data):
        self.data = data
        for i,inputs in enumerate(self.data):
            inputs['input_ids'] = torch.tensor(inputs['input_ids'])
            inputs['attention_mask'] = torch.tensor(inputs['attention_mask'])
            inputs['labels'] = torch.tensor(inputs['labels'])
            inputs['token_type_ids'] = torch.tensor(inputs['token_type_ids'])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


class IterativeJustificationCueDataset(Dataset):
    def __init__(self, data):
        self.data = data
        for i, inputs in enumerate(self.data):
            inputs['input_ids'] = torch.tensor(inputs['input_ids'])
            inputs['attention_mask'] = torch.tensor(inputs['attention_mask'])
            inputs['labels'] = torch.tensor(inputs['labels'])
            inputs['token_type_ids'] = torch.tensor(inputs['token_type_ids'])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


class SpanJustificationCueDataset(Dataset):
    def __init__(self, data):
        self.data = data
        for i, inputs in enumerate(self.data):
            inputs['input_ids'] = torch.tensor(inputs['input_ids'])
            inputs['attention_mask'] = torch.tensor(inputs['attention_mask'])
            inputs['start_positions'] = torch.tensor(inputs['start_positions'])
            inputs['end_positions'] = torch.tensor(inputs['end_positions'])
            inputs['token_type_ids'] = torch.tensor(inputs['token_type_ids'])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


class GradingDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]