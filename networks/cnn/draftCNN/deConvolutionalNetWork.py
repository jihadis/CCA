from networks.bp.bpNeuronNetwork import BPNeuronNetwork
from networks.layer.function.neuronFunction import NeuronFunction
from networks.layer.function.neuronlossFunction import NeuronLossFunction

class DeConvolutionalNetWork(BPNeuronNetwork):
    def __init__(self, cnnlayers, id="", name="",_back_func=None,metadatas=dict({}),parameters=dict({})):
        metadatas = dict({
            "type": "DeConvolutionalNetWork"

        },**metadatas)

        parameters = dict({
            "train.lossfunc":NeuronLossFunction.cross_entropy()
            #lambda x,y:[math.log(x)*y for x,y in zip(x.softmax(),y[x.label])]

        },**parameters)
        if not _back_func:
            _back_func=NeuronFunction(self.back_ward)
        super().__init__(cnnlayers, id, name, metadatas,parameters)

