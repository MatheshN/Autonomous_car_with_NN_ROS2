import rclpy
import numpy as np
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
import os
import csv

class NeuralNetwork(Node):
    
    def input_layer(self, input, w, b):
        self.x_train = os.join("/home/mathesh/autonomous_car_nn/dataset/")
        self.x_test = self.create_subscription(Processed_Image, "/livecamera","callback", 10)
        self.w = w
        self.b = b
        if input == "train":
            for n in self.x_train.row:
                self.neuron1 = np.array(self.x_train) * self.w + self.b
        else :
            try:
                while(1):
                    self.neuron1 = np.array(self.x_test) * self.w + self.b
            except KeyboardInterrupt:
                pass

    def ReLU1(self): #converts negative output to 0
        self.layer1_output = self.neuron1 
        self.layer1_relu = np.maximum(self.layer1_output)

    def layer2(self):
        self.neuron2 = np.array(self.layer1_relu) * self.w + self.b

    def ReLU2(self):
        self.layer2_output = self.neuron2
        self.layer2_relu = np.maximum(self.layer2_output)

    def hidden_layer(self):
        self.neuron3 = np.array(self.layer2_relu) * self.w +self.b

    def ReLU3(self):
        self.final_output = self.neuron3
        self.final_relu = np.maximum(self.final_output)

    



