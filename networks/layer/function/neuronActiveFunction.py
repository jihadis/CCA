from networks.layer.function.neuronFunction import NeuronFunction
from controllers.workflow_controller.flowVaribale import FlowVaribale
from algorithms.tools.Toolkit import *
import math
class NeuronActiveFunction(NeuronFunction):
    def __init__(self,function,name="",id=""):
        #FlowVaribale.addGardFunction(function)
        super().__init__(function,name=name,id=id)


    @staticmethod
    def softmax():
        func=lambda x:x.softMax()
        name="softmax"
        return NeuronActiveFunction(func,name)

    @staticmethod
    def sigmoid():
        func=lambda x:x.sigmoid()
        name="sigmoid"
        return NeuronActiveFunction(func,name)

    @staticmethod
    def relu():

        func = lambda x: x.forEvery(lambda elem:int(elem>0)*elem )
        name = "relu"
        return NeuronActiveFunction(func, name)

    @staticmethod
    def tanh():
        def sigmoid(elem):
            return 1 / (1 + math.exp(-elem))
        func = lambda x: x.forEvery(lambda elem:2 * sigmoid(2 * elem) - 1)
        name = "tanh"
        return NeuronActiveFunction(func, name)
