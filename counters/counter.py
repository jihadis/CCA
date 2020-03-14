from structrue.neuronStruct import NeuronStruct
from system.basic.logs.logSystem import LogSystem
import random
class Counter(NeuronStruct):
    net_id=-1
    settable_parameters={
        "plot.type":1,
        "plot.polar":1,
        "plot.aspectRatio":5,
        "plot.priority":5,
        "plot.alpha": 1,
        "plot.color":1,
        "plot.rule":1
    }
    default={
            "plot.type":"plot",
            "plot.params":dict({}),
            "plot.polar":False,
            "plot.aspectRatio":0.65,
            "plot.priority":1.0,
            "plot.alpha": 1.0,
            "plot.color":random.sample(["r","g","b","y"],1)[0],
            "plot.rule": "train.counter.count.interval"
        }
    def __init__(self,func,name="",metadatas=dict({})):
        super().__init__(name=name)
        self.metadatas=dict(self.default,**metadatas)

        self.func=func

    def set_netId(self,net_id):
        self.net_id = net_id
        return self
    def input(self,lineage,net_id):
        self.input_lineage=lineage
        self.net_id=net_id
        return self
    def output(self,broadcast=False):
        result=self.func(self.input_lineage)
        self.lineage(result,(self.net_id,self.name))
        if broadcast:LogSystem.broadcast(str(result),"message")
