from networks.neuronNetWork import NeuronNetWork
from system.train.trainingParameterSystem import TrainingParameterSystem
from FileObjects.trainingParameterFileObject import TrainingParameterFileObject
from networks.layer.function.neuronFunction import NeuronFunction
from models.neuronNetWorkModel import NeuronNetWorkModel
from system.parameterSystem import ParameterSystem
from system.modelSystem import ModelSystem
from controllers.workflow_controller.flowVaribale import FlowVaribale
from system.basic.logs.logSystem import LogSystem
from FileObjects.moudelFileObject import MoudelFileObject
from system.dataSetSystem import DataSetSystem
import numpy as np
import numpy
class BPNeuronNetwork(NeuronNetWork):
    optimizer=None

    def __init__(self,layers,name="cca_bp_network",_back_func=None,metadatas=dict({}),net_id=None,**parameters):
        metadatas=dict({
            "type":"BPNeuronNetwork",
            "train.optimizer":"Null",
            "train.lossfunc":"Null",
        },**metadatas)
        if not _back_func:
            _func=NeuronFunction(self.back_ward)
        super().__init__(layers,_back_func,name,metadatas,net_id,**parameters)


    losses=[]
    def initiator(self):
        for l in self.layers:
            if hasattr(l,"initiator"):
                self.layers[self.layers.index(l)]=l.initiator()

    @LogSystem.logger
    def loss_func(self,logger,x,func=None):
        y=x.labels
        params = self.parameters.get_parameters()
        if not func:
            func=params["train.lossfunc"]
        loss=func.input(x,y).output()
        self.lineage(loss,"loss")
        self.lineage(y, "y_out")
        return loss,x-y



    def accuracy_func(self,x):

        x_max = [numpy.argmax(i) for i in x]
        y_max = [numpy.argmax(np.array(list(i), dtype="float")) for i in x.labels]
        accuracy = np.mean(np.equal(x_max, y_max))  # 对比求平均值


        return accuracy


    def update_layers(self, losses):

            delta = losses
            for layer in list(self.layers.values())[::-1]:
                delta=layer.update(delta,**self.parameters.get_parameters("train.layer"))




    """
    @TrainingParameterSystem.creator
    def update_layers(self,train_params,losses):

        if isinstance(train_params,TrainingParameterFileObject):
            params=train_params.get_parameters()
            linages = self.layers[-1].get_lineage()
            pointer=2
            actfunc_in,actfunc_out=linages[-pointer:]
            delta=losses*actfunc_out.Grad(actfunc_in)
            for layer in self.layers[::-2]:

                weights=layer.get_matrix()
                biases=layer.get_biases()
                weights_gradint=(weights.T()-actfunc_in*delta*params["train.alpha"]).T()
                layer.set_matrix(weights_gradint)

                linages = layer.get_lineage()
                biases_gradint=biases-delta*params["train.alpha"]
                layer.set_biases(biases_gradint)

                actfunc_in, actfunc_out = linages[-pointer:]
                delta=weights*delta*actfunc_out.Grad(actfunc_in)

                params["train.optimizer"](locals())
    """
    def back_ward(self,result):

        loss_scope,losses=self.loss_func(result)

        self.update_layers(losses)
        return loss_scope

    def iteration(self,number,condition=lambda p,m:False,finish_callback=None,cross_validation=False,**parameters):

            params = dict(self.parameters.get_parameters(),**{k.replace("_","."):v for k,v in parameters.items()})
            if cross_validation:
                for i in range(params["test.validation.split"]):

                    self.iteration(number,condition,lambda :self.initiator(),cross_validation=True)
                    self.lineage("final_accuracy", self.get_lineage("accuracy")[-1])

                total = self.get_lineage("final_accuracy")[-params["test.validation.split"]:]
                total_accuracy = sum(total) / len(total)
                self.lineage(total, "cv_total_accuracys")
                LogSystem.broadcast("total_accuracy :" + str(total_accuracy), "message")
                return total_accuracy,sum([abs(t-total_accuracy) for t in total])
            else:
                if not params["train.condition"]:
                    def BPcondition(p,metadatas):
                        params = dict(self.parameters.get_parameters(),
                                      **{k.replace("_", "."): v for k, v in parameters.items()})
                        if metadatas["epoch"]%params["train.save.interval"]==0: #######
                            model_system=ModelSystem.get_system()
                            model=model_system.create_model(self)
                            model_system.save_orlap(model)
                        system = DataSetSystem.get_system()
                        if metadatas["epoch"]%params["test.interval"]==0 and system.has_dataset(self,"test_x"):
                            dataset=system.get_dataset(self,"test_x",cross_validation=cross_validation)
                            self.parameters.update_parameter("network.training", False)

                            result=self.input(dataset.read()).output()
                            self.parameters.update_parameter("network.training", True)

                            accuracy = self.accuracy_func(result)
                            print("acc",accuracy)
                            metadatas["accuracy"]=accuracy
                            self.lineage(accuracy,"accuracy")
                            # if dataset.metadatas["lineage"]:#///
                            #     system.delete_dataset(dataset)


                            return accuracy>params["test.stop.accuracy"]



                        return condition(p,metadatas)
                else:
                    BPcondition=params["train.condition"]
                system = DataSetSystem.get_system()
                train_dataset=system.get_dataset(self,"train_x")
                super().iteration(train_dataset.read(),number,BPcondition,finish_callback)

                return max(self.get_lineage("accuracy"))


