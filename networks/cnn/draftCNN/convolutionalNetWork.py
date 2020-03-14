from networks.bp.bpNeuronNetwork import BPNeuronNetwork
from networks.layer.function.neuronFunction import NeuronFunction
from networks.layer.function.neuronlossFunction import NeuronLossFunction

class ConvolutionalNetWork(BPNeuronNetwork):

    optimizer = None
    def __init__(self, cnnlayers, name="",_back_func=None,metadatas=dict({})):
        metadatas = dict({
            "type": "ConvolutionalNetWork"

        },**metadatas)


        if not _back_func:
            _back_func=NeuronFunction(self.back_ward)
        super().__init__(cnnlayers, name, metadatas)





    """
        def upsampling(self,delta,size=(2,2)):
        numbers=numpy.full(size,1/size[0]*size[1]).tolist()
        return CnnLayer(numbers,delta,step=1/math.sqrt(size[0]*size[1]))
        
        
     def get_genurte(self):
        pass
    @TrainingParameterSystem.creator
    def update_layers(self, train_params, losses):
        if isinstance(train_params,TrainingParameterFileObject):
            params=train_params.get_parameters()
            layers= self.get_layers()
            linages = layers[-1].get_lineage()
            pointer = 3
            patchs,actfunc_in, actfunc_out = linages[-pointer:]
            delta = losses * actfunc_out.Grad(actfunc_in)

            for layer in  layers[::-2]:
                weights=layer.get_matrix()
                biases = layer.get_biases()
                biases_gradint = biases - delta * params["train.alpha"]
                layer.set_biases(biases_gradint)
                weights_gradint =weights - delta * patchs * params["train.alpha"]
                layer.set_matrix(weights_gradint)

                linages = layer.get_lineage()
                patchs,actfunc_in, actfunc_out = linages[-pointer:]
                graded=actfunc_out.Grad(actfunc_in)

                if layers.index(layer)>0:
                    prev_layer=layers[layers.index(layer)-1]
                    if isinstance(prev_layer,PoolingLayer):
                        delta = weights * self.upsampling(delta,numpy.shape(prev_layer.get_matrix())) * graded
                    elif isinstance(prev_layer,CnnLayer):
                        delta = CnnLayer(weights, padding=len(weights.shape()[1]) - 1).input(delta).output() * graded

                    elif isinstance(prev_layer,NeuronLayer):
                        delta = weights * delta * graded
    """