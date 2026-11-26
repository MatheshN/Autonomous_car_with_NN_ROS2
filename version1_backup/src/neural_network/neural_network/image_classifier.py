import torch
import numpy as np

#converting tensor directly from data
data = [[1,2], [3,4]]
print(data)
print(type(data))
x_data = torch.tensor(data)
print(x_data)
print(type(x_data))

#converting tensor from a Numpy array

np_array = np.array(data)
x_np = torch.from_numpy(np_array)
print(x_np)


#from another tensor

x_ones = torch.ones_like(x_data)
print(f"Ones Tensor: \n{x_ones } \n")

x_rand = torch.rand_like(x_data, dtype=torch.float)
print(f"Random Tensor: \n {x_rand} \n" )

# rand_like
# ones_like
# from_numpy
# torch