"""
    NeuronLayerSystem be used for build layer quickly

"""
from networks.layer.neuronLayer import NeuronLayer
from system.parameterSystem import ParameterSystem

from networks.layer.contection.neuronContection import NeuronContection
from networks.layer.neuron.neuron import Neuron
from algorithms.matrix.matrixSystem import MatrixSystem

from controllers.workflow_controller.flowVaribale import FlowVaribale
class NeuronLayerSystem():
    @staticmethod
    def layer_initiator(func):
        def wapper(*args, **kwargs):
            layer = func(*args, **kwargs)
            layer.initiator = lambda: wapper(*args, **kwargs)
            return layer

        return wapper


    #需要大做文章的
    default_params={"weight_init":MatrixSystem.getRandn,
            "weight_sigma":0.01,
            "weight_mean":0,
    }
    def __init__(self,namespace="",random_weight=True,**kwargs):
        self.params=dict(self.default_params,**kwargs)
        self.namespace=namespace
        from system.factory.neuronLayerFactory import NeuronLayerFactory
        self.factory = NeuronLayerFactory()

    #project -> cca_script.py -> network model(size,network_id_name,accurry).APIFILE

    #将每个神经元具象化，求导步骤（导函数）更改为 layerinput output



"""
   @staticmethod
    @layer_initiator# 设定初始化权重和神经元的方法
    def full_connected_layer(layer=NeuronLayer.empty(),inputs_outputs=(1,1),name="",weights=None,bias=1):
        if not weights:#getorelse
            weights=FlowVaribale(self.params["weight_init"]\
                (inputs_outputs,self.params["weight_sigma"],self.params["weight_mean"]).tolist())
        inputs,outputs=inputs_outputs
        layername=self.namespace+"_"+name
        neurons = [Neuron(layername+"_"+str(o),bias) for o in range(outputs)]
        contections=[NeuronContection(("before_"+str(i),layername+"_"+str(o)),weights[i][o]) for i in range(inputs) for o in range(outputs)]
        layer.update(neurons,contections,name=name)
        return layer

"""