"""
source structure of any neurons
Subclass:
    NeuronContection
    NeuronNetWork
    NeuronFunction
    NeuronLayer
    Neuron

"""
from controllers.workflow_controller.flowVaribale import FlowVaribale
from initiator.starter import CCAstarter
#CCAstarter.start()
from abc import abstractmethod
from system.basic.files.offsetSystem import OffsetSystem

import copy as cp
import hashlib
import time
class NeuronStruct(object):
    Id=None
    name=None
    enable=True
    metadatas=None
    get_id=id
    def __init__(self,_func=None,name="",metadatas=None,id=None):
        from networks.layer.function.neuronFunction import NeuronFunction
        if _func and not isinstance(_func, NeuronFunction):
            raise Exception("Neuron FuncObject must be Type of NeuronFunction")
        self.name=name
        if not id:
            self.Id=hashlib.md5(bytes(str(NeuronStruct.get_id(self)),"utf-8")).hexdigest()
        else:
            self.Id=id
        self.metadatas=metadatas
        self._func=_func

    def set_Id(self,new_id):
        self.Id=new_id
        return self
    @abstractmethod
    def input(self,*args):
        pass

    @abstractmethod
    def output(self,*args)->list:
        pass

    @abstractmethod
    def update(self,*args):
        pass

    @abstractmethod
    def shape(self):
        pass

    @abstractmethod
    def dump(self):
        pass

    @abstractmethod
    def empty(self,**kwargs):
        from copy import deepcopy
        cobj=deepcopy(self)
        [setattr(cobj, k, v) for k,v in kwargs.items() if hasattr(cobj, k)]
        return cobj

    def __str__(self):
        return "<CCA object>\n"+str(self.metadatas)

    def get_metadata(self):
        return self.metadatas

    def set_metadata(self,k,v):
        self.metadatas[k]=v

    def clear_lineage(self):
        system = OffsetSystem.get_system()
        system.set_offset(self.Id,[])

    def get_lineages(self):
        system = OffsetSystem.get_system()
        return system.get_offset("lineages")
    def get_lineage(self,key=""):

        system = OffsetSystem.get_system()
        lineages = system.get_offset("lineages")
        if key in lineages:
            return system.get_offset("lineages")[key]
        else:
            return []
    def clean_lineage(self,key=""):
        system = OffsetSystem.get_system()
        lineages = system.get_offset("lineages")
        if key in lineages:lineages[key]=[]
    def concat(self,another):

        pass


    def lineage(self,obj,key=""):
        system=OffsetSystem.get_system()
        lineage=system.get_OrCreate("lineages",dict({}),True)
        if key not in lineage.keys():
            lineage[key]=[]
        lineage[key].append(obj)

    def copy(self):
        return cp.deepcopy(self)

    def isEnabled(self,b):
        self.enable=b

    def toVarialbe(self)->FlowVaribale:
        return FlowVaribale(self)

    def __str__(self):

        strs="\nCCAobject{\n"

        strs+=("\n".join([w+":"+("\n   ["+"\n   [".join([str(k)+"]:  "+str(type(v))+"  "
            +str(v) for k,v in self.metadatas.items()])) for w in ["metadatas"]]))
        return strs+"\n}"