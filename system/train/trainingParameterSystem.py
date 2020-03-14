from system.basic.files.offsetSystem import OffsetSystem
from system.parameterSystem import ParameterSystem
from networks.layer.function.neuronlossFunction import NeuronLossFunction
from networks.layer.function.neuronOptimizer import NeuronOptimizer
from networks.layer.function.neuronActiveFunction import NeuronActiveFunction

class TrainingParameterSystem(OffsetSystem):



    trainingGroup="TrainingParameters"

    #在面试前，至少过一遍下面的算法

    #settable parameters when you running networks
    settable_parameters={
        "network.training":1,
        "network.plotter":1,
        "train.repeat":1,
        "train.counter.count.interval":200,
        "train.counter.broadcast.interval":1500,
        "test.validation.split":20,
        "train.layer.alpha":3,
        "train.layer.lambda":0.02,
        "train.mbgd.batchsize":200,
        "test.interval":400,
        "test.stop.accuracy":1,
    }
    default_parameters={
            #training stage mode
            "network.training":False,

            "network.plotter": True,

            #defined name of dataset for network
            "train.requireDatasets":["train_x","test_x"],
            #method of network inputs
            "train.method":["SGD","BGD","MBGD"],

            "train.repeat":True,

            "train.counter.count.interval":10,

            "train.counter.broadcast.interval":100,

            "test.repeat": False,#分离出测试的数据集，是否也用来训练

            #cross validation about test
            "test.validation":["2-CV","K-CV","Eg","LOO-CV","Normal"],

            "test.validation.split":5,

            "train.layer.alpha":0.1,

            "train.layer.lambda":1e-3,

            "train.layer.optimizers": [NeuronOptimizer.L2() ],#NeuronOptimizer.L1()

            "train.mbgd.batchsize":10,

            "train.lossfunc":NeuronLossFunction.mean_square(),

            "train.save.interval":500,

            "train.activefunc":NeuronActiveFunction.sigmoid(),

            "test.interval": 100,

            "train.condition":None,

            "test.stop.accuracy": 1.999,

        # 非监督学习该种参数无效
    }


    def get_default(self,net_obj):
        name=[c.__name__ for c in type(net_obj).mro() if c.__name__ in self.network_default_parameters.keys()][0]
        return self.get_OrCreate(net_obj.Id,self.network_default_parameters[name]().set_netid(net_obj.Id))





    _trainingParameterSystem=None
    system = OffsetSystem.get_system()
    _trainingfiles = OffsetSystem.get_OrCreate(system, trainingGroup, dict({}))
    def __init__(self):
        from system.parameterSystem import ParameterSystem
        system = ParameterSystem.get_system()
        from FileObjects.trainingParameterFileObject import TrainingParameterFileObject
        TrainingParameterFileObject.set_default(TrainingParameterSystem.trainingGroup, ParameterSystem.get_datas(system)["path.params"])
        default_parameters = TrainingParameterFileObject(TrainingParameterSystem.default_parameters,visual=True)

        self.network_default_parameters = {
            "ConvolutionalNetWork": lambda :default_parameters.update_parameters({
                "train.lossfunc": NeuronLossFunction.cross_entropy(),
                "train.activefunc": NeuronActiveFunction.relu(),
                "train.requireDatasets":["train_x","train_y"],
                "train.method":"SGD"
            }),
            "GanNetwork": lambda :default_parameters.update_parameters({
                "train.lossfunc": NeuronLossFunction.gan_likelihood(),
                "train.activefunc": NeuronActiveFunction.relu(),
                "train.requireDatasets": ["train_x"]
                ,"train.method":"SGD"
            }),
            "InfoGanNetwork": lambda :default_parameters.update_parameters({
                "train.lossfunc": NeuronLossFunction.gan_infolikelihood()
            }),
            "BPNeuronNetwork": lambda :default_parameters.update_parameters({
                "train.method": "MBGD"
            }),
            "NeuronNetWork": lambda :default_parameters.update_parameters({
                "train.method": "BGD"
            }),
        }

        if not TrainingParameterSystem._trainingParameterSystem:
            TrainingParameterSystem._trainingParameterSystem = self
        super().__init__()

    @staticmethod
    def creator(func):

        def wapper(self,*args,**kwargs):
            from FileObjects.trainingParameterFileObject import TrainingParameterFileObject
            system=TrainingParameterSystem.get_system()
            default_value=TrainingParameterFileObject.default_parameters
            path=ParameterSystem.get_system().get_datas()["path.offsets"]+"/train_parameters"
            params=system.get_OrCreate(self.Id,[path,default_value,self.Id])
            return func(self,params,*args,**kwargs)
        return wapper

    @staticmethod
    def get_system():
        return TrainingParameterSystem._trainingParameterSystem
    def get_OrCreate(self,id,default_value,loop_update=False):
         from FileObjects.trainingParameterFileObject import TrainingParameterFileObject
         files = super().get_offset(self.trainingGroup)


         if id not in files.keys():
             if isinstance(default_value,list):
                 default_value=TrainingParameterFileObject(*default_value,net_id=id)
             elif isinstance(default_value,dict):
                 default_value = TrainingParameterFileObject(default_value, net_id=id)
             files[id]=default_value
         file=files[id]
         if isinstance(file, list):
             return self.set_trainingfile(id, [f for f in file if
                                               isinstance(f, TrainingParameterFileObject) and f.get_netid() == id])
         return self.set_trainingfile(id, file)

    def update_trainingfile(self, group, obj):
        self.set_trainingfile(group,obj)
        self.dump_trainingfiles()

    def dump_trainingfiles(self):

       super().dump_offset(self.trainingGroup,self.trainingGroup)

    def set_trainingfile(self, id,obj):
        TrainingParameterSystem._trainingfiles[id] = obj
        super().dump_offset(self.trainingGroup, self.trainingGroup)
        return obj

