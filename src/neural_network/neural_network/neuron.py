import numpy as np

class NeuralNetwork:

    def __init__(self):
        self.input_size = 9
        self.hidden_size = 16
        self.output_size = 1

        self.w1 = np.randn(self.input_size, self.hidden_size)

        self.b1 = np.zeros(self.hidden_size)

        self.w2 = np.random.randn(
            self.hidden_size,
            self.output_size
        )

        self.b2 = np.zeros(self.output_size)

    def forward(self, x):

        z1 = np.dot(x, self.w1) + self.b1

        a1 = np.maximum(0, z1)

        z2 = np.dot(a1, self.w2) + self.b2
        z2 = np.dot(a1, self.w2) + self.b2
        z2 = np.dot(a1, self.w2) + self.b2

        return z2
