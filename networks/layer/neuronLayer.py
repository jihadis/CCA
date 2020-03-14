from structrue.neuronStruct import NeuronStruct
from controllers.workflow_controller.flowVaribale import FlowVaribale
from system.basic.logs.logSystem import LogSystem
from system.basic.logs.expectionSystem import ExpectionSystem
from functools import reduce
import numpy
from algorithms.tools.Toolkit import *
import copy
from networks.layer.function.neuronFunction import NeuronFunction
class NeuronLayer(NeuronStruct):

    matrix,biases=None,None
    def __init__(self,matrix,biases,_func=NeuronFunction(lambda x:x),name="",dropout=(),clear_lineage=True):
        self.clearlineage=clear_lineage
        self.matrix=matrix
        self.biases=biases
        self.initiator=lambda :NeuronLayer(matrix,biases,_func,name,clear_lineage).set_Id(self.Id)
        super().__init__(_func,name,{"weight_shape":numpy.shape(self.matrix)})

    def empty(self,**kwargs):
        return super().empty(matrix=None,biases=None,**kwargs)

    def get_biases(self):
        return FlowVaribale(self.biases)

    def set_biases(self,biases):
        self.biases=self.biases

    def get_last_value(self):
        return self.get_lineage("")[-1]

    def get_matrix(self):
        return FlowVaribale(self.matrix)
    def set_matrix(self,m):
        self.matrix=m

    def shape(self):
        return len(self.matrix)
    def input(self,tensors):
        if self.clearlineage: self.clean_lineage(self.Id)
        self.input_tensors=tensors
        self.lineage(self.input_tensors,self.Id)
        return self
    @LogSystem.logger
    @ExpectionSystem.error_logger
    def output(self,logger):#计算该层神经元的输出值.


        layer_results=self.input_tensors.dot(self.matrix)+self.biases
        layer_results.requireGrad(True)
        self.lineage(layer_results,self.Id)
        self._func.input(layer_results)
        func_outputs=self._func.output() #用于激活函数或者损失函数
        self.lineage(func_outputs,self.Id)

        return func_outputs

    def update(self,delta,**parameters):


        linages = self.get_lineage(self.Id)
        input_x,actfunc_in, actfunc_out = linages[-3:]


        weights=self.get_matrix()
        biases = self.get_biases()

        db=delta*(actfunc_out.fullGrad(actfunc_in)[0])

        delta=(db.dot(weights.T()))
        #delta=FlowVaribale.ones((1,weights.shape()[0]))


        dw=FlowVaribale([FlowVaribale([(input_x*i).toList()[0] for i in d_b]).T() for d_b in db])

        #dw=delta
        dw=dw.sum(-3)/len(input_x)
        db=db.sum(-2)/len(input_x)
        for o in parameters["optimizers"]:
             o.input(input_x, weights, biases, dw, db)
             dw,db=o.output(**parameters)
        # for d_w in dw:weights-=d_w*parameters["alpha"]
        # for d_b in db:biases -=d_b*parameters["alpha"]
        weights_gradint = weights - dw * parameters["alpha"]
        biases_gradint = biases - db * parameters["alpha"]
        self.set_matrix(weights_gradint)
        self.set_biases(biases_gradint)
        # self.set_matrix(weights)
        # self.set_biases(biases)
        return delta

    def concat(self,another_struct):
        new_matrix=FlowVaribale.getRandomGaussian(self.matrix.shape()+another_struct)
        new_matrix[self.matrix.labels]=self.matrix;self.matrix=new_matrix
        new_biases=FlowVaribale.ones((1,self.biases.shape()+another_struct[-1]))
        new_biases[self.biases.labels]=self.biases;self.biases=new_biases














    """
        def update(self,neurons,contections,_func,name=""):
        def parse_contection(contections):  # 决定开始的时候给那些神经元赋值

            linked_contections = {c.From: [] for c in contections if c.enable}
            contections_dict = {c.relationship: c for c in contections}
            for c in contections:
                if c.enable:
                    linked_contections[c.From].append(c)  # 多向链表结构
            [n.update(_func,n.bias) for n in neurons]
            input_nodes = [k for k in list(linked_contections.keys()) if k not in
                           [c.To for c in contections]]
            output_nodes = [k.Id for k in list(neurons) if k.Id not in
                           [c.From for c in contections]]
            return input_nodes,output_nodes, contections_dict, linked_contections

        if isinstance(neurons,list):
            self.neurons={n.Id:n for n in neurons}
        self.input_nodes,self.output_nodes,self.contections_dict,self.linked_contections=\
            parse_contection(contections)
        return self
        layer_outputs={}
        def loop(nodes,outputs):
            def out(node,output):
                stage_outputs = []
                for to in self.linked_contections[node.From]:
                    self.neurons[to.To].input(output)
                    stage_outputs.append(self.neurons[to.To].output(to.weight))
                if node.To in list(self.linked_contections.keys()):
                    return self.linked_contections[node.To], stage_outputs
                else:
                    if node.To not in layer_outputs.keys():
                        layer_outputs[node.To] = stage_outputs
                    else:
                        self.marge_func(layer_outputs,stage_outputs,node)
                    return None, None
            if nodes and outputs:
                [loop(*out(node,output)) for node,output in zip(nodes,outputs) ]

        for input_node,input_tensor in zip(self.input_nodes,self.input_tensors):
            next_neurons=self.linked_contections[input_node]
            loop(next_neurons,[input_tensor]*len(next_neurons))
    
    
        def color(r,g,b):
            print(r,g,b)
        loss=125
        255*3 ,255 *6,255*1
        
        for i in range(kebord):
            255-125/len(kebord)*i
            
        [R,G,B,RG,RB,GB]
        
        matrix/6
    """

