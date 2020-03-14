import torch
import numpy as np
import PIL.Image
from controllers.workflow_controller import flowStep


class InputFormatController(flowStep.FlowStepController):
    def __init__(self,vectors):
        self.vectors=super().createVariable(vectors)

    def toGray(self,alpha=1):
        for vector in np.array(self.vectors):
            v = vector
            if len(v.shape) > 2:
                pixels = v.reshape((v.shape[0] * v.shape[1], v.shape[2]))
                result=list(np.array([(0.3 * pixel[0] + 0.6 * pixel[1] + 0.1 * pixel[2])*alpha
                               for pixel in pixels]).reshape(v.shape[:2]))
                return super().createVariable(result,self.vectors.flow_id,[hash(self.vectors)])






    def twoValues(self,mode="normal",threshold=125):
        vectors=np.array(self.vectors)
        for vector in vectors:
            if mode == "mean":
                threshold = vector.mean()
            if mode == "ostu": #max variance of gray
                variance=[]
                for t in range(255):
                    bg=vector[vector<t]
                    w0=bg.size/vector.size;w1=1-w0
                    m0,m1=bg.mean(),(vector-bg).mean()
                    variance.append((w0*w1*(m0-m1)**2,t))
                threshold=sorted(variance,key=lambda e:e[0])[-1][1]
            vector[vector>=threshold]=255
            vector[vector<threshold]=0
        return super().createVariable(list(vectors),self.vectors.flow_id,[hash(self.vectors)])


        #sss

vectors=[[



         [[22,44,66],[22,44,66]],
         [[22,44,66],[22,44,66]]



]]

print(np.array(vectors).mean())



