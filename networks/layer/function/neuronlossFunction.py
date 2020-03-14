from networks.layer.function.neuronFunction import NeuronFunction
import math
class NeuronLossFunction(NeuronFunction):

    def __init__(self,function,name="",id=""):
        super().__init__(function,name=name,id=id)

    @staticmethod
    def cross_entropy():

        import math
        def func(x, y):return sum([math.log(x)*y for x,y in zip(x.softmax(),y)])
        name="cross_entropy"
        return NeuronLossFunction(func,name)

    @staticmethod
    def mean_square():
        def func(x,y):
            print(x)
            print(y)
            return 1/len(x)*((x-y)**2).sum()
        name="mean_square"
        return NeuronLossFunction(func,name)
    @staticmethod
    def math_log():
        def func(x):math.log(x)
        name="math_log"
        return NeuronLossFunction(func,name)
    @staticmethod
    def gan_likelihood():
        def func(r, f):math.log(r)+math.log(1-f)
        name = "gan_likelihood"
        return NeuronLossFunction(func, name)

    @staticmethod
    def gan_infolikelihood():

        def func(r,f,l):math.log(r)+math.log(1-f)-l
        name = "gan_infolikelihood"
        return NeuronLossFunction(func, name)