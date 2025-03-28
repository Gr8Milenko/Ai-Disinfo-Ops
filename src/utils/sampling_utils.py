import numpy as np

def entropy(probabilities):
    return -np.sum(probabilities * np.log(probabilities + 1e-9), axis=1)
