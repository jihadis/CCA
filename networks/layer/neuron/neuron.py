from controllers.workflow_controller.flowVaribale import  FlowVaribale
from networks.layer.function.neuronFunction import NeuronFunction
from structrue.neuronStruct import NeuronStruct
from system.basic.logs.logSystem import LogSystem
import numpy

class Neuron(NeuronStruct,object):#donst be exists
    tensor = None
    connections = None
    bias=0

    def __init__(self,id,bias=1,_func=NeuronFunction(lambda x:x),name="",clear_lineage=True):
        self.bias=bias
        self.Id=id
        self.clear_lineage=clear_lineage
        super().__init__(_func,id,name)

    def input(self,tensor):
        self.tensor=tensor
        return self

    @LogSystem.logger
    def output(self,logger):

        if self.tensor:
            self._func.input({(c.From, c.To): c.weight for c in self.connections})
            weights=self._func.output() #适用于drop Out
            logger.lineage(weights,self)
            beta=FlowVaribale(list(weights.values()))*(self.tensor)
            return beta+self.bias

    def update(self,connections,bias):
        self.connection=connections
        self.bias=bias
        return self

    def shape(self):
        return numpy.shape(self.tensor)