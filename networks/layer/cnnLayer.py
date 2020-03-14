from networks.layer.neuronLayer import NeuronLayer
from structrue.neuronStruct import NeuronStruct
from structrue.neuronStruct import NeuronStruct
from controllers.workflow_controller.flowVaribale import FlowVaribale as FlowVar
from system.basic.logs.logSystem import LogSystem
from system.basic.logs.expectionSystem import ExpectionSystem
from functools import reduce
from controllers.workflow_controller.flowVaribale import FlowVaribale
import numpy
from algorithms.tools.Toolkit import *
from networks.layer.function.neuronFunction import NeuronFunction
class CnnLayer(NeuronLayer):
    all_sample_patchs=[]
    def __init__(self,shape,kernals,biases,padding=1,stride=1,
                 _func=NeuronFunction(lambda p:p.sum(2)),name="",dropout=(),clear_lineage=True):
        self.shape=shape
        self._kernals=kernals
        self.stride=stride
        self._biases=biases
        self.padding=padding

        super().__init__([],[],_func,name,dropout,clear_lineage)
    @staticmethod
    def DecnnLayer(*args,**kwargs):
        cnnlayer=CnnLayer(*args,**kwargs)

        def update(self, delta, learning_rate, optimizer=None):
            linages = self.get_lineage(self.Id)
            input_tensors, patchs, actfunc_in, actfunc_out = linages[-3:]
            weights = self.get_matrix()
            biases = self.get_biases()
            weights_gradint = weights - (delta * patchs).sum(2) * learning_rate
            biases_gradint = biases - delta * learning_rate
            self.set_matrix(weights_gradint)
            self.set_biases(biases_gradint)
            delta = CnnLayer(weights,stride=1/self.stride).input(delta).output() * actfunc_out.Grad(
                actfunc_in)
            return delta

        cnnlayer.update=update
        return cnnlayer

    def get_biases(self):
        return self._biases

    def set_biases(self,biases):
        self._biases=biases

    def get_matrix(self):
        return self._kernals

    def set_matrix(self,m):
        self._kernals=m
    #data structure : each sample [chanels [ featuremaps[] ]]

    def update(self, delta,**parameters):
        linages = self.get_lineage(self.Id)
        input_tensors,patchs, actfunc_in, actfunc_out = linages[-4:]
        weights = self.get_matrix()
        biases = self.get_biases()
        weights_gradint = weights - (delta * patchs).sum(2) * parameters["alpha"]
        biases_gradint = biases - delta * parameters["alpha"]
        self.set_matrix(weights_gradint)
        self.set_biases(biases_gradint)
        delta = CnnLayer(weights, padding=len(weights.shape()[1]) - 1).input(delta).output() * actfunc_out.Grad(actfunc_in)
        return delta
    def shape(self):
        return self.shape
    # def input(self,tensors):
    #     if tensors.shape()[-len(self.shape):]!=self.shape:
    #         raise Exception("wrong input shape"+tensors.shape()[-2:]+" Required:"+self.shape)
    #     self.input_tensors = tensors
    #     return self

    def insert_padding(self,map):
        l=self.stride
        if self.stride>1:
            l=1
        z=numpy.zeros(FlowVar(FlowVar(numpy.shape(map))+(2*self.padding))/l)
        def set_zeros(elem,index,v):
            if (index%(1/l)).all(lambda x:x==0):
                z[FlowVar(index)+self.padding]=elem
        forEveryWithIndex(map,set_zeros)
        return FlowVar(z.tolist())

    def get_patchs(self,map,size):
        def f(elem,index,v):
            if self.stride<=1 or (index%self.stride).all(lambda x:x==0):
                return map[size.indexes()+list(index)]
        return forEveryWithIndex(map,f,clear_null=True)
    #
    def naive_convolution(self,sample):
        all_patchs=[]
        def f(featuremap,index,v):
            kernals=self._kernals[index]
            biases=self._biases[index]
            results=[]
            for kernal,bias in zip(kernals,biases):
                size=list(numpy.shape(kernal))
                #featuremap=self.insert_padding(featuremap)
                patchs=self.get_patchs(featuremap.pad(self.padding),size)
                all_patchs.append(patchs)
                results.append(self._func.input((patchs*kernal).sum(-2)+bias).output())
            return results
        self.all_sample_patchs.append(all_patchs)
        return forEveryWithIndex(sample,f,axis=2)
    #
    def fast_convolution(self,sample):
    @LogSystem.logger

    @ExpectionSystem.error_logger
    def output(self,logger):
        if self.clearlineage: self.clear_lineage()
        layer_results =[self.naive_convolution(sample) for sample in self.input_tensors]
        self.lineage(self.all_sample_patchs,self.Id)
        self.lineage(layer_results,self.Id)
        self._func.input(layer_results)
        func_outputs = self._func.output()  # 用于激活函数或者损失函数
        self.lineage(func_outputs,self.Id)
        return func_outputs

