from controllers.workflow_controller import flowStep
from algorithms.tools.Toolkit import *
import pickle
import inspect
import math
from numpy import matlib
import numpy as np
import random
from functools import reduce
import copy
from controllers.counter_controller import counter

@flowStep.FlowStepController.insertVariable()
def _d_sigmoid(x):
    return FlowVaribale(forEvery(lambda elem:1/(1 + math.exp(-elem))*(1-1/(1 + math.exp(-elem))),x))
class FlowVaribale(list,flowStep.FlowStepController):
    labels=[]
    #it will be use a lot of memory
    def __init__(self, vectors, flow_id="".join(random.sample([str(i) for i in range(100)], 4)), step_result=False,label=[]):
        self.labels = label
        self.all_labels = {"y": label}
        self.flow_id = flow_id
        self.hash = "".join(random.sample([str(i) for i in range(10)], 9))
        self.step_result = step_result
        if not hasattr(vectors,"__iter__")or isinstance(vectors,str):
            vectors=[vectors]
        self.id=id(vectors)

        super().__init__(vectors)

    def submitVariable(self,variable,sync=None,labels=None):
        if not labels:labels=self.labels
        return super().\
            createVariable(variable,self.flow_id,self.step_result,labels,sync)

    def reduce(self,func):
        from functools import reduce
        return self.submitVariable(reduce(func,self))
    def elemcount(self):
        x=[0]
        forEvery(lambda e:x.append(x.pop()+1),self)
        return x[0]
    @flowStep.FlowStepController.insertVariable()
    def __mul__(self, other):

        if hasattr(other, "__iter__"):
            result=(np.array(other) * self).tolist()
            if isinstance(other,FlowVaribale)and other.step_result:
                return self.submitVariable(result,[(other,other.__rmul__,(self),{})])
            return self.submitVariable(result)
        return self.submitVariable(forEvery(lambda elem:elem*other,self))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        return self.__mul__(other)
    @staticmethod
    def max_depath(elem):
        depath=[]
        forEveryWithIndex(elem, lambda e, i, v: depath.append(len(i)))

        return max(depath)
    def _getLabel(self,label,getlabel=False):
        # sp = np.shape(self.labels)
        #
        # if len(sp)==1 and sp[0]==1 :
        #     if label==self.labels[0]:
        #         return self
        #     return None
        def f(elem, index):
            if FlowVaribale(self.labels).get(index)==label:
                if getlabel:
                    return label
                return elem
            return


        return forEveryWithIndex(self,f,axis=self.max_depath(self.labels),clear_null=True)


    def sum(self,axis=0):
        if axis==0:
            v = [0]
            def f(e):v[0]+=e
            forEvery(f,self)
            return self.submitVariable([v])
        return self.submitVariable(np.array(self).sum(axis).tolist(),labels=self.labels)
    def sample(self,num=1):
        res=[]
        while len(res)<num and num<=len(self):
            r=random.randint(0, len(self) - 1)
            if r not in res:res.append(r)
        return self.submitVariable([self.toList()[r] for r in res],labels=[self.labels[r] for r in res])
    def __setitem__(self, item, value):

        if hasattr(item, "__iter__"):

            if self.all(lambda x:isinstance(x,int),item):

                def f(idxelems,i,v):
                    if i==tuple(item):
                        return value
                    return idxelems
                value=copy.copy(forEveryWithIndex(self,f,axis=len(item)))
            self.clear()
            self.extend(value)
        else:
            super().__setitem__(item,value)
    def get(self, item,labels=None):
        res=self.__getitem__(item,labels)
        if not hasattr(res,"__iter__"):
            return self.submitVariable([res])
        if len(res)==1:
            return res.toList()[0]
        return res

    def __getitem__(self, item,labels=None):
        if  isinstance(item,slice) or (isinstance(item,tuple) and slice in [type(i) for i in item]):
            litem = item
            if not isinstance(item,slice):
                litem=item[:len(np.shape(self.labels))]

            return self.submitVariable(numpy.array(self)[item].tolist(),
                                       labels=numpy.array(self.labels)[litem].tolist())
        if hasattr(item,"__iter__"):
            if len(item)==0:
                return self
            elif self.all(lambda x:isinstance(x,str),item):
                return self.submitVariable(forEvery(self._getLabel,item)
                            ,labels=FlowVaribale(forEvery(lambda e:self._getLabel(e,True),item)).toList())
            elif self.all(lambda x:isinstance(x,int),item):

                def f(idxelems,getlabels=False):
                    elem=self.toList()
                    if getlabels:
                        elem=self.labels
                    for idxelem in idxelems:
                        if len(elem)>idxelem and hasattr(elem,"__iter__") and not isinstance(elem,str) :

                            elem=elem[idxelem]
                    return elem
                res=forEveryWithIndex(item,lambda e:f(e),axis=len(np.shape(item))-1)
                labels=forEveryWithIndex(item,lambda e:f(e,True),axis=len(np.shape(item))-1)
                if not isinstance(res, list):
                    res = [res]
                if not isinstance(labels, list):
                    labels = [labels]
                return self.submitVariable(res,labels=labels)
        elif isinstance(item,int):

            elem=super().__getitem__(item)

            if not isinstance(elem,list):
                return elem
            if isinstance(self.labels,list) and item<len(self.labels):
                labels=self.labels[item]
            return self.submitVariable(elem,labels=labels)


        return super().__getitem__(item)
    @flowStep.FlowStepController.insertVariable()
    def __truediv__(self, other):
        if hasattr(other, "__iter__"):
            result = (np.array(self)/other).tolist()
            if isinstance(other, FlowVaribale)and other.step_result:

                return self.submitVariable(result,[(other,other.__rtruediv__,(self),{})])
            return self.submitVariable(result)
        return self.submitVariable(forEvery(lambda elem: elem / other,self))

    def __rtruediv__(self, other):
        return self.__truediv__(self=other,other=self)

    def __itruediv__(self, other):
        return self.__truediv__(other)

    @flowStep.FlowStepController.insertVariable()
    def __neg__(self):
        return self.submitVariable(forEvery(lambda elem: -elem,self))

    @flowStep.FlowStepController.insertVariable()
    def dot(self,y):
        return self.submitVariable(np.dot(self,y).tolist(),labels=[])

    @flowStep.FlowStepController.insertVariable()
    def ldot(self,x):
        return self.submitVariable(np.dot(x,self).tolist(),labels=[])

    @flowStep.FlowStepController.insertVariable()
    def __add__(self,other):
        if isinstance(other,tuple):
            return self.submitVariable(self.toList()+list(other))
        if hasattr(other, "__iter__"):
            result=(np.array(self)+other).tolist()
            if isinstance(other, FlowVaribale) and other.step_result:
                return self.submitVariable(result,[(other,other.__radd__,(self),{})])
            return  self.submitVariable(result)
        else:
            return self.submitVariable(forEvery(lambda elem:elem+other,self))

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, order):
        return self.__add__(order)

    def __mod__(self, other):
        if hasattr(other, "__iter__"):
            result=(np.array(self)%other).tolist()
            return  self.submitVariable(result)
        else:
            return self.submitVariable(forEvery(lambda elem:elem%other,self))


    @flowStep.FlowStepController.insertVariable()
    def __sub__(self, other):
        if hasattr(other, "__iter__"):
            result=(np.array(self)-other).tolist()
            if isinstance(other, FlowVaribale) and other.step_result:
                return self.submitVariable(result,[(other,other.__rsub__,(self),{})])
            return  self.submitVariable(result)
        else:
            return self.submitVariable(forEvery(lambda elem:elem-other,self))

    def __rsub__(self, other):
        return self.__add__(self=-other, other=self)

    def __isub__(self, other):
        return self.__sub__(other)


    @flowStep.FlowStepController.insertVariable()
    def __pow__(self, power, modulo=None):

        return self.submitVariable(forEvery(lambda elem:
                                elem**power,self))
    def __ipow__(self, other):
        return self.__pow__(other)

    def shuffle(self):
        r=numpy.array(list(zip(self.toList(), self.labels)))
        numpy.random.shuffle(r)
        return self.submitVariable(r[:,0].tolist(),labels=r[:,1].tolist())

    def flat(self,tree=None):
        if tree==None:tree=self
        res = []
        for i in tree:
            if isinstance(i, list):
                res.extend(self.flat(i))
            else:
                res.append(i)
        return self.submitVariable(res)
    def groupby_label(self,axis=0,external_label=None):

        if external_label:
            labels = FlowVaribale(external_label)
            self.labels=external_label
        else:
            labels = FlowVaribale(self.labels)
        def f(e,i):
            if len(i)==axis:
                la=set({})
                forEvery(lambda e:la.add(e),labels[i])
                labels[i]=list(la)

                return [self[i][l]for l in la]
            return e
        return self.submitVariable(forEveryWithIndex(self,f,axis),labels=labels)
    def sequece(self,axis=1,full=None):

        if FlowVaribale.max_depath(self)>1:

            length=self.flat(self.forEvery(lambda e:len(e),axis=axis))
            min_length, max_length = min(length),max(length)

            def f(e):
                if full  and len(e) <max_length:
                    return e+self.full((max_length-len(e)),full)
                elif not full and len(e)> min_length:
                    return e[:min_length]
                return e
            return self.forEvery(f,axis=axis)
    @staticmethod
    def full(shape,value):
        return FlowVaribale(np.full(shape,value).tolist())
    @flowStep.FlowStepController.insertVariable()
    def relu(self):

        return  self.submitVariable(forEvery(lambda elem:int(elem>0)*elem,self))






    @flowStep.FlowStepController.insertVariable(_d_sigmoid)
    def sigmoid(self):

        return  self.submitVariable(forEvery(lambda elem:1 / (1 + math.exp(-elem)),self))

    @flowStep.FlowStepController.insertVariable()
    def softMax(self):

        marge=sum(forEvery(math.exp,self[0]))
        return self.submitVariable(forEvery(lambda elem:math.exp(elem)/marge,self[0]))
    def pad(self,padding=1):
        return self.submitVariable(numpy.pad(self.toList(),
            ((0, 0),(0, 0),(padding, padding),(padding,padding)),mode='constant'))

    @flowStep.FlowStepController.insertVariable()
    def mean(self):
        return self.submitVariable([np.array(self).mean()],labels=[])

    def set(self,value):
        super().__init__(value)
        return self
    def toList(self):
        # def tl(l):
        #     if isinstance(l, FlowVaribale):
        #         l=list(l)
        #     return l
        # return forEvery(tl,self)
        return list(self)
    def concat(self,order):
        return self.submitVariable(super().__add__(order),labels=self.labels+order.label)
    def all(self,condition,item=None):
        if not item:
            item=self
        self.real=True
        def wapper(elem):
            if not condition(elem):
                self.real=False

        forEvery(wapper,item)
        return self.real

    @flowStep.FlowStepController.insertVariable()
    def forEvery(self,func,*args,**kwargs):
        result=forEveryWithIndex(self,func,*args,**kwargs)
        return self.submitVariable(result)

    def apply_labels(self,key="y"):
        self.labels=self.all_labels[key]
        return self

    def set_labels(self,l,key="y"):
        self.labels =l
        self.all_labels[key]=l

    def get_labels(self,key="y"):
        return self.all_labels[key]
    def transpose(self,indexs):
        return self.submitVariable(np.transpose(self.toList(),indexs).tolist(),labels=self.labels)
    def shape(self):
        return np.shape(np.array(self.toList()))
    def reshape(self,shape):

        return self.submitVariable(np.reshape(self,shape).tolist(),labels=self.labels)#np.reshape(self.labels,shape[:len(np.shape(self.labels))]).tolist()

    @staticmethod
    def ones( shape):
        if len(shape)==0:
            return []
        return FlowVaribale(np.ones(shape).tolist())
    def indexes(self):
        return self.submitVariable(forEveryWithIndex(list(self),lambda elem,index,v:list(index)))
    def track(self):
        return counter.TrackerController.track(self)

    def requireGrad(self,r):
        self.step_result=r



    @flowStep.FlowStepController.insertVariable()
    def fullGrad(self,x=None,default_func=True):
        return self.submitVariable(super().grad(self,x,False,default_func))
    def T(self):
        return self.submitVariable(np.array(self).T.tolist())
    @flowStep.FlowStepController.insertVariable()
    def Grad(self,x=None,default_func=True):

        return self.submitVariable(super().grad(self,x,True,default_func))

    def save(self,path):
        pickle.dump(self,path)

    @staticmethod
    def getRandom(size,step):

        return FlowVaribale(random.randint(0,size))*step

    @staticmethod
    def Lagrange(p,x=None):
        lp=list(range(len(p)))
        if not x:x=lp
        return lambda v:sum([p[j]*reduce(lambda x,y:x*y,[(v-x[i])/(x[j]-x[i])for i in lp if i!=j])for j in lp])

    @staticmethod
    def getRandomGaussian(size, sigma=1e-6, mean=0):

        return FlowVaribale((sigma * np.matlib.randn(size) + mean).tolist())
    @staticmethod
    def addGradFunction(func):

        if func !=flowStep.FlowStepController.insertVariable:
            setattr(FlowVaribale,func.__name__,flowStep.FlowStepController.insertVariable(func))
        else:
            setattr(FlowVaribale,func.__name__,func)
        return getattr(FlowVaribale,func.__name__)