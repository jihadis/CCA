import numpy as np
import math
import pickle
import sys
from controllers.workflow_controller import flowVaribale
from controllers import learningController
from algorithms.grad import gradSystem
from algorithms.matrix import matrixSystem
from functools import reduce

import copy
class FlowStepController(learningController.Controller):
    # consts

    flows={}
    lineage={}

    #怎么求导：？？
    #答：应用线性代数就行了。
    #a -> x^2 -> b

    #controller functions
    def createVariable(self,vectors,flow_id=None,step_result=None,labels=None,sync=None):
        result=flowVaribale.FlowVaribale(vectors,flow_id,step_result,labels)
        if sync!=None:
            for variable,func,args,kwargs in sync:
                if step_result:
                    temp=variable.step_result
                    variable.step_result=True
                    FlowStepController.setLineAge(variable,func,args,kwargs,result)
                    variable.step_result=temp
        return result
    def getBackwards(self,y,x):#得到反向变量结构树
        backwards = []
        if x.flow_id==y.flow_id:
            def loop(xn,backward):

                        if xn.hash in FlowStepController.flows.keys() and gradSystem.GradSystem.isGrad(xn):
                            backward+=[xn]
                        if xn.hash==y.hash:
                            backwards.append(backward)
                        elif xn.hash in FlowStepController.lineage[x.flow_id].keys():
                            [loop(FlowStepController.flows[i][xn.hash],copy.copy(backward))
                                    for i in FlowStepController.lineage[x.flow_id][xn.hash]]
            loop(x,[])
        return backwards
    @staticmethod
    def setLineAge(variable, func, args, kwargs, result):#创建结构树，类似于SPARK RDD的关系
        if variable.step_result:
            if result.hash not in FlowStepController.flows.keys():
                FlowStepController.flows[result.hash]=dict({})
            FlowStepController.flows[result.hash][variable.hash]= gradSystem.GradSystem.createGrad(variable, func, args, kwargs, result)
            if variable.flow_id not in FlowStepController.lineage.keys():
                FlowStepController.lineage[variable.flow_id] = dict({})
            if variable.hash not in FlowStepController.lineage[variable.flow_id].keys():
                FlowStepController.lineage[variable.flow_id][variable.hash] = []
            FlowStepController.lineage[variable.flow_id][variable.hash].append(result.hash)

    @staticmethod
    def insertVariable(d_func=None):
        def wapper(func):
            if d_func!=None:gradSystem.GradSystem.d_functions[func]=d_func
            def inner_wapper(variable,*args,**kwargs):

                if isinstance(variable, flowVaribale.FlowVaribale):
                    result=func(variable,*args,**kwargs)
                    if variable.step_result:
                        if isinstance(result,dict):
                            FlowStepController.setLineAge(result["variable"],func,
                                                          result["args"],result["kwargs"],result["result"])
                            return result["result"]
                        else:
                            FlowStepController.setLineAge(variable,func,list(args),kwargs,result)
                    return result

                else:
                    raise RuntimeError("variable must be type of flowVaribale.FlowVaribale")
            return inner_wapper
        return wapper

    #neuron functions

    # def sigmoid(self,x):
    #     return 1/(1+math.exp(-x))
    #
    # def softmax(self,results):
    #     marge=sum([math.exp(result)for result in results])
    #     return [math.exp(result)/marge for result in results]

    def grad(self,y,x=None,diagonal=False,default_func=False): #导数(得到导函数值）

        if not x:x=FlowStepController.flows[list(FlowStepController.lineage[y.flow_id].keys())[0]]

        if x.hash==y.hash: raise RuntimeError("can not derivation to itself.")
        grad_lines=self.getBackwards(y,x)
        if len(grad_lines)==0:raise RuntimeError("has no derivation relationship between x and y.")

        results=[reduce(lambda x,y:(np.array(x) * y).tolist(), [gradSystem.GradSystem.requireGrad(grad,default_func=default_func)
                                                                for grad in grad_line]) for grad_line in grad_lines]

        #是否忽略线性函数变换只返回对角矩阵
        if not diagonal:

            return results

        #找出最大形式
        ##################

        diagonal_grads=[matrixSystem.MatrixSystem.getDiagonal(r[0],sorted([np.shape(g.get_variable().toList()) for g in r[1]], key=lambda s: len(s))[0]) for r in zip(results,grad_lines)]
        return np.around(reduce(lambda x, y:(np.array(x)+y).tolist() ,diagonal_grads),5).tolist()




    def partial_grad(self,value): #偏导数
        return

    def plot(self):#绘制
        return

    def get_gard(self):#得到导函数(全微分)
        return
