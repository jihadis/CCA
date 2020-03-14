from networks.layer.cnnLayer import CnnLayer
import numpy as np
import math
from networks.layer.function.neuronFunction import NeuronFunction
class PoolingLayer(CnnLayer):

    def __init__(self,shape,size,mode=0,padding=1,step=1,_func=None,name=""):
        self.mode=mode

        if not _func:
            _func=NeuronFunction(lambda p:self.pooling(p))
        super().__init__(shape,np.ones(size),[0],padding,step,_func,name)


    def output(self):
        if self.mode:
            return self.input_tensors.max(2)
        return self.input_tensors.mean(2)

    def unpooling(self,delta):
        size=np.shape(self._kernals)
        numbers=np.full(size,1/size[0]*size[1]).tolist()
        return CnnLayer(numbers,step=1/math.sqrt(size[0]*size[1])).input(delta).output()

    def update(self, delta, learning_rate, optimizer=None):
        delta = self.unpooling(delta)
        return delta
