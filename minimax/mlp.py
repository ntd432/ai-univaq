import torch.nn as nn

class FlexibleMLP(nn.Module):
    def __init__(self, layer_sizes, activation_fn=nn.Softmax):
        super(FlexibleMLP, self).__init__()
        layers = []

        # Create the layers dynamically based on layer_sizes
        for i in range(len(layer_sizes) - 1):
            layers.append(nn.Linear(layer_sizes[i], layer_sizes[i + 1]))
            if i < len(layer_sizes) - 2:  # Add softmax to the last layer only
                layers.append(nn.Softmax(dim=1))
            # else:  # No activation after the last layer
            #     layers.append(activation_fn())

        # Combine all layers into a sequential model
        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x)