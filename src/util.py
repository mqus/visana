from pandas import np

def project(val, max2, min2=0, max1=None, min1=0):
    if max1 is None:
        min1=np.min(val)
        max1=np.max(val)
        print(max1)
    return ((val - min1) * (max2 - min2)) / (max1 - min1) + min2