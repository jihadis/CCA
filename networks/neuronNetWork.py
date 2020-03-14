from structrue.neuronStruct import NeuronStruct
from networks.layer.neuronLayer import NeuronLayer
from networks.layer.function.neuronFunction import NeuronFunction
from system.basic.logs.logSystem import LogSystem
from FileObjects.trainingParameterFileObject import *
from FileObjects.moudelFileObject import MoudelFileObject
from FileObjects.neuronNetworkFileObject import NeuronNetworkFileObject
from system.modelSystem import ModelSystem
import copy
from system.dataSetSystem import DataSetSystem
from system.basic.files.fileObjectSystem import FileObjectSystem
from system.preprocessorSystem import PreprocessorSystem
from system.train.trainingParameterSystem import TrainingParameterSystem
from system.train.trainingCounterSystem import TrainingCounterSystem
class NeuronNetWork(NeuronStruct): #willbe saved
    parameters,preprocessor,counters=None,None,None
    is_training=False

    def __init__(self,layers,_func=NeuronFunction(lambda x:x),name="",metadatas=dict({}),net_id=None,**parameters):


        default_metadatas = {
            "accuracy": 0.0,
            "epoch": 0,
            "version": 1.0,
            "shape": (0),
            "name":name
        }
        super().__init__(_func, name, metadatas, net_id)
        metadatas=dict(default_metadatas,**metadatas)

        self.parameters=TrainingParameterSystem.get_system().get_default(self)#训练管理器
        metadatas = dict(metadatas, **{k: k.name for k, v
                                       in self.parameters.get_parameters().items() if
                                       k in metadatas and isinstance(k, NeuronFunction)})
        self.parameters.update_parameters({k.replace("_","."):v for k,v in parameters.items()})
        self.start_tensors=[]
        self.metadatas=metadatas
        self.preprocessor=PreprocessorSystem.get_system().get_default(self)#预处理器
        LogSystem.broadcast("Preprocessors "+str(self.preprocessor.read()))
        self.counters=TrainingCounterSystem.get_system().get_default(self)#统计器
        LogSystem.broadcast("Counters " + str(self.counters.read()))
        #parmeter.save

        self.name=name
        self._training_func=_func
        self.update(layers)


    def get_layers(self):
        return self.layers.values()


    def set_dataset(self,datafile,name=None):
        if not name: name=datafile.name
        if name in self.parameters.get_parameters()["train.requireDatasets"]:
            DataSetSystem.get_system().copy_dataset(datafile,self.Id,name)
    #前面的processor可以处理后面的
    def set_preprocessor(self,preprocessor):
        system=PreprocessorSystem.get_system()
        self.preprocessor =system.set_preprocessor(self.Id,system.get_new(self).read().concat(preprocessor))

    def get_layer(self,layer_id):
        return self.layers[layer_id]

    def predict(self,start_tensors):

        self.start_tensors=start_tensors
        outputs=self.output()

        labels = DataSetSystem.get_dataset(DataSetSystem.get_system(),self, "train_label")
        if labels:
            outputs=labels.read()[outputs.argmax()]
        return outputs

    @PreprocessorSystem.excutor
    def input(self,start_tensors):

        self.start_tensors=start_tensors

        self.lineage(start_tensors)
        return self

    def empty(self,**kwargs):
        return super().empty(parameters=None,preprocessor=None,layers=[l.empty() for l in self.layers],**kwargs)

    def dump(self):

        FileObjectSystem.get_OrExecution(self.Id,lambda :NeuronNetworkFileObject(self.empty())).save()

    def back_ward(self,result):
        pass


    @LogSystem.logger
    def output(self,logger):#运行一次迭代之后的输出结果

        def loop(tensors,layers):
            if len(layers)>0:
                layer=layers.pop(0)
                layer.input(tensors)
                return loop(layer.output(),layers)
            return tensors
        layers=list(self.layers.values()).copy()
        self.lineage(layers[-1].get_matrix().toList(), "weights")
        result=loop(self.start_tensors, layers)

        self.lineage(result,"x_out")
        func_outputs=result
        params = self.parameters.get_parameters()
        if  params["network.training"] :
            func_outputs=self.back_ward(func_outputs) #用于权重反向更新

        return func_outputs

        # from controllers.workflow_controller.flowVaribale import FlowVaribale
        # return FlowVaribale([[0,1,24,1,1,4,1,2,3,4]],label=[[0,1,24,1,1,4,1,2,3,4][::-1]])


    def update(self,layers):#更新神经层

        self.layers = {l.Id:l for l in layers }

        #self.funcs={f.Id:f for f in layer_funcs if isinstance(f, NeuronFunction)}

        return self


    def concat(self,another):
        if isinstance(another, NeuronNetWork):
            new_layers=dict(another.layers,**self.layers)
            new_metadatas=dict(another.metadatas,**self.metadatas)
            new_network=NeuronNetWork(new_layers,metadatas=new_metadatas)
            return new_network


    def shape(self):
        return tuple([l.shape() for l in self.layers])



    def iteration(self,datasets,number,condition=lambda p,m:False,finish_callback=None):
        self.parameters.update_parameter("network.training",True)
        for i in range(number):
            if condition(self.parameters,self.metadatas):
                if finish_callback:
                    finish_callback()
                break

            # import numpy
            # from controllers.workflow_controller.flowVaribale import FlowVaribale
            # self.start_tensors=FlowVaribale(numpy.ones((1,256)).tolist(),label=[[1,0]])

            self.input(datasets)
            self.output()

            #print(self.metadatas["epoch"])
            #===================================counter
            params=self.parameters.get_parameters()

            print(self.metadatas["epoch"])

            if self.metadatas["epoch"]%params["train.counter.count.interval"]==0:
                self.lineage(self.metadatas["epoch"],"epoch")
                self.counters.count(self.get_lineages(),
                                    self.metadatas["epoch"]%
                                    params["train.counter.broadcast.interval"]==0,
                                    self.metadatas,self.Id,params["network.plotter"],self.parameters)
            self.metadatas["epoch"] += 1
        self.parameters.update_parameter("network.training", False)

#网络能够在训练完毕的情况下动态更新
#实现网络架构，权重参数，元数据，模型分离
#训练超参数同样脱离网络架构，由trainmanager管理,决定哪个模型使用哪些超参数