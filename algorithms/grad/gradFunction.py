import copy
import numpy
class Grad():
    d=10**-6
    cased = False
    def __init__(self, variable, func, args, kwargs,result):
        self.variable =variable
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result=result
        self.hash = result.hash

    def get_variable(self):
        return copy.copy(self.variable)
    def call(self, variable):

        f=self.func(variable,*self.args,**self.kwargs)
        #f(dx)-f(x)=df
        f.set((numpy.array(f.toList())-self.result.toList()).tolist())

        return f