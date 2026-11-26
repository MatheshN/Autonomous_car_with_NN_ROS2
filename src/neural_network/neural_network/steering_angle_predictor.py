import os
import csv 
import cv2
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader

class DrivingDataset(Dataset):
    def __init__(self, dataset_dir):
        self.dataset_dir = dataset_dir
        self.samples = []
        csv_path = os.path.join(self.dataset_dir, 'data.csv')
        with open(csv_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                self.samples.append((row['image_path'], float(row['steering_angle'])))
        # print(self.samples[1])
    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx : int):
        rel_path, steering = self.samples[idx]
        full_path = os.path.join(self.dataset_dir, rel_path)

        # print(type(full_path))

        img = cv2.imread(full_path)
        if img is None:
            raise FileNotFoundError(f"Could Not load image at {full_path}")

        cropped = img[180:440, :]
        resized = cv2.resize(cropped, (200,66), interpolation = cv2.INTER_AREA)

        img_normalized = (resized/127.5)-1
        img_chw = np.transpose(img_normalized, (2,0,1))

        return torch.tensor(img_chw, dtype=torch.float32), torch.tensor([steering], dtype= torch.float32)

class CarNN(nn.Module):
    def __init__(self):
        super(CarNN, self).__init__()

        #1. Convolutional Layers (Feature Extraction)
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 24, kernel_size = 5, stride = 2),
            nn.ELU(),
            nn.Conv2d(25, 36, kernel_size = 5, stride = 2),
            nn.ELU(),
            nn.Conv2d(36, 48, kernel_size = 5, stride = 2),
            nn.ELU(),
            nn.Conv2d(48, 64, kernel_size = 5, stride = 1),
            nn.ELU(),
            nn.Conv2d(64, 64, kernel_size = 3, stride = 1),
            nn.ELU()

        )

        #2. Fully Connected Layers (Decision Making)
        self.fc_layers = nn.sequential(
            nn.Flatten(),
            nn.Linear(1152, 100),
            nn.ELU(),
            nn.Linear(100, 50),
            nn.ELU(),
            nn.Linear(50, 10),
            nn.ELU(),
            nn.Linear(10, 1) # Final output: 1 single steering angle
        )

    def forward(self, x):
        features = self.conv_layers(x)
        steering_prediction = self.fc_layers(features)
        return steering_prediction

def train():

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training on device: {device}")

    dataset_path = os.path.expanduser()

# d = DrivingDataset("/home/mathesh/autonomous_car_nn/dataset")
# print(type(d.samples[1]))
# d.__getitem__(2)
# print()
