from structrue.neuronStruct import NeuronStruct
import sys
class NeuronFunction(NeuronStruct):

    def __init__(self,function,name="",id="",args=[]):
        self.name=name
        self.locals=sys._getframe(1).f_locals
        self.funcArgs=args

        self.update(function)
        super().__init__(self,id)

    def update(self,function):

        self.function = function

    def input(self,*args):
        self.funcArgs = args

        return self
    def output(self):

        return self.function(*self.funcArgs)


