from networks.layer.neuronLayer import NeuronLayer
from networks.layer.cnnLayer import CnnLayer
from networks.layer.poolingLayer import PoolingLayer
import numpy
from networks.layer.function.neuronActiveFunction import NeuronActiveFunction
from controllers.workflow_controller.flowVaribale import FlowVaribale


def layer_initiator(func):
    def wapper(self, *args, **kwargs):

        layer = func(self, *args, **kwargs)
        layer.initiator = lambda: wapper(self,*args, **kwargs)
        return layer

    return wapper

class NeuronLayerFactory():





    @layer_initiator
    def convlotional(self,shape,name="",kernals=None,biases=FlowVaribale([1])
                                                ,padding=1,strides=1,active_func=NeuronActiveFunction.relu(),mean=0,variance=1e-2):

        if isinstance(kernals,tuple):
            if len(kernals)>2:biases=FlowVaribale.ones(kernals[:-2])
            kernals=FlowVaribale.getRandomGaussian(kernals,variance, mean)

        return CnnLayer(shape,name,kernals,biases,padding,strides,active_func,name)
    def pooling(self,shape,name="",kernalsize=None,mode="avg",padding=0,strides=1,modelist={"avg":False,"max":True}):
        return PoolingLayer(shape,kernalsize,modelist[mode],padding,strides,name)

    def letNet_5(self,outputsize):
        return [
            self.convlotional((32, 32), "conv_0", (6 ,5, 5), strides=1, padding=0),
            self.pooling((6 ,28, 28), "pool_1", (2, 2), strides=2, padding=0),
            self.convlotional((6,14, 14), "conv_1", (16,5, 5), strides=1, padding=0),
            self.pooling((16, 10, 10), "pool_1", (2, 2), strides=2, padding=0),
        ]+self.layers((400,120,84))+[self.fullConnected((84,outputsize),"fc_out",active_func=NeuronActiveFunction.softmax())]

    def AlexNet(self,outputsize,input_channels=3):
        return [
            self.convlotional((input_channels,227,227),"conv_0",(96,11,11),strides=4),
            self.pooling((96,57,57),"pool_1",(3,3),strides=2),
            # Dropout 96,28,28
            self.convlotional((96,16,16),"conv_1",(256,5,5),strides=1),
            self.pooling((256,28,28),"pool_2",(3,3),strides=2),
            # Dropout 256,13,13
            self.convlotional((256, 13, 13),"conv_2",(384,3,3),strides=1),
            self.convlotional((384, 13, 13), "conv_3", (384, 3, 3), strides=1),
            self.convlotional((384, 13, 13), "conv_4", (256, 3, 3), strides=1),
            #Dropout 256,6,6
            self.pooling((256,13,13),"pool_3",(3,3),strides=2)
        ]+self.layers((4096,4096))+[self.fullConnected((4096,outputsize),"fc_out",active_func=NeuronActiveFunction.softmax())]

    def layers(self,shapes,creator=None,*params):
        if not creator:creator=self.fullConnected
        if isinstance(shapes,tuple):shapes=[(shapes[i],shapes[i+1]) for i in range(len(shapes)) if i+1<len(shapes)]
        return [creator(shape=shapes[i], *list(list(params) + [[]]).pop(0)) for i in range(len(shapes))]



    @layer_initiator

    def fullConnected(self,shape,name="",weight=None,bias=None
                      ,active_func=NeuronActiveFunction.sigmoid(),mean=0,variance=1e-2):
        if not weight:
            weight = FlowVaribale.getRandomGaussian(shape, variance, mean)
        if not bias:
            bias = FlowVaribale(numpy.ones(shape[-1]).tolist())

        return NeuronLayer(weight,bias,active_func,name)
