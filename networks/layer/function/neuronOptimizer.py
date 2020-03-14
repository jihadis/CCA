from networks.layer.function.neuronFunction import NeuronFunction
from algorithms.tools.Toolkit import *
import math
class NeuronOptimizer(NeuronFunction):

    def __init__(self, function, name="", id="",**kwargs):



        self.parameters=dict(kwargs)
        super().__init__(function, name=name, id=id)
        self.name = name
    def output(self,**kwargs):

        #return self.funcArgs[-2:]
        return self.function(dict(self.parameters,**kwargs),*self.funcArgs)





    @staticmethod
    def L1(name="L1"):
        def l1(p,x,w,b,dw,db):
            #abs_sum=w.forEvery(lambda e: sum([abs(i)for i in e]),-2,True)
            sgn=w.forEvery(lambda wi:(int(wi>=0)-0.5)*2*int(w!=0))
            dw=dw-p["lambda"]*p["alpha"]*sgn/len(x)
            return dw,db
        return NeuronOptimizer(l1, name)

    @staticmethod
    def L2(name="L2"):
        def l2(p,x,w,b,dw,db):

            #square_sum=w.forEvery(lambda w:sum([abs(i)**2 for i in w]),-2,True)
            #aa=w*p["lambda"]*p["alpha"]/len(x)

            dw=dw+w*p["lambda"]*p["alpha"]/len(x) # w*(1−ηλ/n)-dw = w-(dw+(w*ηλ/n))
            return dw,db
        return NeuronOptimizer(l2,name)

    @staticmethod
    def RmsProp(name="RmsProp"):
        def rmsprop(p,x,w,b,dw,db):

            beta=0.9
            sdw=beta*p["sdw"]+(1-beta)*dw
            sdb=beta*p["sdb"]+(1-beta)*db
            dw/=math.sqrt(sdw)+1e-8
            db/=math.sqrt(sdb)+1e-8
            return dw,db
        return NeuronOptimizer(rmsprop,name,sdw=0,sdb=0)

    @staticmethod
    def Adam(name="Adam"):

        def func(p,x,w,b,dw,db):
            pass
        return NeuronOptimizer(func,name)

    @staticmethod
    def AdaGard():
        pass

    @staticmethod
    def AdaDelta():
        pass

    @staticmethod
    def Momentum():
        pass
    @staticmethod
    def empty():
        return NeuronOptimizer(lambda x:x,"Null")