from  FileObjects.moudelFileObject import MoudelFileObject

from FileObjects.fileObject import FileObject


class NeuronNetworkFileObject(FileObject):

    def __init__(self,_network,*args,**kwargs):
        self._network=_network
        super().__init__(_network,*args,**kwargs)

    def Insert_Model(self,model): #插入权重偏置
        if isinstance(model,MoudelFileObject):

            self.model=model.get_model()

            ############################神经网络中插入模型
            network = self.get_network()
            if len(self.model) == len(network):
                layers=network.get_layers()
                for i in range(len(layers)):
                    layer=layers[i]
                    weights=self.model.weights[i]
                    biases=self.model.biases[i]
                    layer.set_matrix(weights)
                    layer.set_biases(biases)

    def Insert_Preprocessor(self,preprocessor):#插入预处理器模块*

        self._data.preprocessor=preprocessor.get_preprocessor()

    def Insert_Trainingparameter(self,trainingparameter):#插入训练模块(优化器,超参数,正则化,反向传播)

        self._data.trainingparameter=trainingparameter.get_parameters()



    def get_network(self):
        return self.read()

    #预处理器，模型，神经网络,生成预测结果
    def predict(self,start_tensor):
        network=self.get_network()
        from networks.neuronNetWork import NeuronNetWork
        if isinstance(network,NeuronNetWork):
            result=network.input([start_tensor]).output()
            return result

