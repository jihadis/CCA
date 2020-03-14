from networks.neuronNetWork import NeuronNetWork
from system.train.trainingParameterSystem import TrainingParameterSystem
from FileObjects.trainingParameterFileObject import TrainingParameterFileObject
from controllers.workflow_controller.flowVaribale import FlowVaribale
from networks.cnn.draftCNN.convolutionalNetWork import ConvolutionalNetWork
from networks.cnn.draftCNN.deConvolutionalNetWork import DeConvolutionalNetWork
from system.train.trainingParameterSystem import TrainingParameterSystem
from networks.layer.function.neuronlossFunction import NeuronLossFunction
from system.basic.logs.logSystem import LogSystem
from system.preprocessorSystem import PreprocessorSystem
import math
from system.dataSetSystem import DataSetSystem
import numpy as np
class GanNetwork(ConvolutionalNetWork,DeConvolutionalNetWork):

    def __init__(self,g_layers,d_layers,name=""):
        super().__init__(g_layers,name+"_Gnet")
        super().parameters.update_parameters({"train.lossfunc":NeuronLossFunction.math_log(),"network.gan":self})

        self.generator=super()
        self.tag=FlowVaribale([lambda x:x,lambda x:-(1-x)])
        self.generator.loss_func=self._generator_loss

        DeConvolutionalNetWork.__init__(d_layers,name+"_Gnet")
        DeConvolutionalNetWork.parameters.update_parameters({"train.lossfunc":NeuronLossFunction.gan_likelihood(),"network.gan":self})

        self.discriminator = DeConvolutionalNetWork
        self.discriminator.loss_func=self._discriminator_loss
        self.parameters.update_parameters({"train.linearInsert": True})
    @TrainingParameterSystem.creator
    @LogSystem.logger
    def _generator_loss(self,train_params,logger,fake_image,func=None):
        params = train_params.get_parameters()
        network = params["network.gan"]
        fake_tensor = network.discriminator.input(fake_image).output()
        if not func:
            func = params["train.lossfunc"]
        loss = func(fake_tensor)
        logger.log(loss, "Network:id=" + self.Id + " ,type=" + str(type(self)) + " ,loss=" + loss)
        return loss,fake_tensor


    @TrainingParameterSystem.creator
    @LogSystem.logger
    def _discriminator_loss(self,train_params,logger,scope_vector,func=None):
        params = train_params.get_parameters()
        network= params["network.gan"]
        size = network.generator.get_layers()[-1].shape()
        fake_image = network.generator.input(FlowVaribale.getRandomGaussian(size)).output()
        fake_scope_vector=self.input(fake_image).output()
        if not func:
            func = params["train.lossfunc"]

        loss = func(math.log(fake_scope_vector),-math.log(1-scope_vector))
        logger.log(loss, "Network:id=" + self.Id + " ,type=" + str(type(self)) + " ,loss=" + loss)

        return loss, self.tag[scope_vector.label](scope_vector)

    @PreprocessorSystem.excutor
    def input(self,start_tensors=None):
        if not start_tensors:
            gaussian=FlowVaribale.getRandomGaussian(self.generator.shape()[0])
            self.generator.input(gaussian)
        self.start_tensors = start_tensors
        self.lineage(start_tensors)
        return self


    def output(self):
        if not self.start_tensors:
            return self.generator.output()
        return self.discriminator.output()
    def g_output(self):
        return self.generator.output()

    def d_output(self):
        return self.discriminator.output()
    def loss_func(self,train_params,logger,x,func=None):
        pass 


    def iteration(self, number ,condition=lambda x:False):

            params = self.parameters.get_parameters()
            if not params["train.condition"]:
                def GANcondition(p):
                    if self.metadatas["epoch"] % params["train.generator.each"]==0:

                        if params["train.linearInsert"]:
                            size=self.generator.shape()[0]
                            gaussians =[FlowVaribale.getRandomGaussian(size) for i in range(2)]
                            gaussians =[gaussians[0][:i]+gaussians[1][i:] for i in range(size)]
                            for g in gaussians:
                                self.input(g).g_output()
                        else:
                            self.input().output()
                    return condition(p)
            else:
                GANcondition=params["train.condition"]
            return super().iteration( number, GANcondition)




