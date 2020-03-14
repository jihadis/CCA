from networks.gan.ganNetWork import GanNetwork
from networks.bp.bpNeuronNetwork import BPNeuronNetwork
from system.train.trainingParameterSystem import TrainingParameterSystem
from system.basic.logs.logSystem import LogSystem
from controllers.workflow_controller.flowVaribale import FlowVaribale
from system.layer.neuronLayerSystem import NeuronLayerSystem
from system.preprocessorSystem import PreprocessorSystem
#continuous variables : (length,meanValue,+-area)
class InfoGanNetwork(GanNetwork):
    def __init__(self,g_layers,d_layers,types_variables=(0,1),continuous_variables=(6,2,0),name="InfoGAN"):
        super().__init__(g_layers,d_layers,name=name)

        self.spreader=BPNeuronNetwork(NeuronLayerSystem.factory.fullConnected(d_layers[-2].shape(),
                                            types_variables[0]+continuous_variables[0]), id, name+"_Qnet")
        self.generator.loss_func=self._generator_loss
        self.set_continuous_variables(continuous_variables)
        self.set_type_variables(types_variables)
    
    #区别在于：Gloss 增加Q的类别损失正则化项， Dloss 增加Q的反向传播
    @PreprocessorSystem.excutor
    def input(self,start_tensors=None,start_continuous_tensors=None,start_type_tensors=None):
        super().input(start_tensors)
        params = self.parameters.get_parameters()
        if not start_tensors:
            if not start_type_tensors:
                start_type_tensors = FlowVaribale.getRandom(*params["train.variables.types"])
            if not start_continuous_tensors:
                start_continuous_tensors = FlowVaribale.getRandomGaussian(*params["train.variables.continuous"])
            type_input=start_type_tensors+start_continuous_tensors
            self.lineage(type_input,"InfoGAN-Type")
            self.generator.start_tensors=self.generator.start_tensors+type_input  ##整合随机类型值

    def set_type_variables(self,variables):
        self.parameters.update_parameters({"train.variables.types":variables})
        self.generator.layers[0].concat(((variables[0],0)))

    def set_continuous_variables(self,variables):
        self.parameters.update_parameters({"train.variables.continuous": variables})
        self.generator.layers[0].concat((variables[0],0))



    @TrainingParameterSystem.creator
    @LogSystem.logger
    def _generator_loss(self,train_params,logger,fake_image,func=None):

        loss,fake_tensor=self.generator.loss_func(train_params,logger,fake_image,func)
        edge_layer=self.discriminator.get_layers()[-2]
        lv=edge_layer.get_last_value
        type_tensor=self.spreader.input(lv).output()
        self.lineage(type_tensor,"InfoGAN-Q_out")
        type_loss=1-sum((type_tensor-self.generator.input_type_tensor).abs()) #L1
        self.lineage(type_loss,"InfoGAN-L1")
        self.lineage(loss*type_loss,"InfoGAN-G_loss")
        return loss*type_loss,fake_tensor*type_loss


    @TrainingParameterSystem.creator
    @LogSystem.logger
    def _discriminator_loss(self,train_params,logger,real_tensor,func=None):
        loss, fake_tensor = self.discriminator.loss_func(train_params, logger, real_tensor, func)
        type_loss=fake_tensor-fake_tensor.label
        self.spreader.back_ward(type_loss)
        return loss, fake_tensor

    def iteration(self,number ,condition=lambda x:False):
        params=self.parameters.get_parameters()
        if not params["train.condition"]:
            return super().iteration(number,condition)
        return super().iteration(number, condition)
