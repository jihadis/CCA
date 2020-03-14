from structrue.neuronStruct import NeuronStruct
class NeuronContection(NeuronStruct):

    def __init__(self,relationship,weight):
        if isinstance(relationship,tuple) and len(relationship)==2:
            self.relationship=relationship
            self.From=relationship[0]
            self.To=relationship[1]
            self.weight=weight
        else:
            raise RuntimeError("relationship must be type of tuple2")

    def update(self,weight):
        self.weight=weight

    def copy(self):
        pass