import torch
import torch.nn as nn

class PupilDetectionModel(nn.Module):
    def __init__(self):
        super(PupilDetectionModel, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 16, 3, 1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, 1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(32, 16, 2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose2d(16, 1, 2, stride=2),
        )
        self.fc = nn.Linear(1 * 64 * 64, 3)  # Final fully connected layer to output cx, cy, radius

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        x = x.view(x.size(0), -1)  # Flatten the tensor for the fully connected layer
        x = self.fc(x)  # Output: cx, cy, radius
        return x
