from system.basic.files.offsetSystem import OffsetSystem
from FileObjects.preprocessorFileObject import PreprocessorFileObject
from preprocessors.preProcesser import PreProcessor
from controllers.workflow_controller.flowVaribale import FlowVaribale
import numpy as np
import random
from system.basic.logs.logSystem import LogSystem
class PreprocessorSystem(OffsetSystem):

    preProcessorGroup="PreProcessor"
    default_preprocessor,_preprocessorSystem = None,None
    from system.parameterSystem import ParameterSystem

    system = ParameterSystem.get_system()
    PreprocessorFileObject.set_default(preProcessorGroup, ParameterSystem.get_datas(system)["path.preprocessors"])


    def __init__(self):
        if not PreprocessorSystem._preprocessorSystem:
            PreprocessorSystem.default_preprocessor = PreprocessorFileObject(PreProcessor())
            PreprocessorSystem._preprocessorSystem = self
        system = OffsetSystem.get_system()
        PreprocessorSystem._preprocessors = OffsetSystem.get_OrCreate(system, self.preProcessorGroup, dict({}))



        super().__init__()
    @staticmethod
    def inputSelection_Preprocessor(method,batchsize=1):
        def BGD(vectors):
            return vectors
        def SGD(vectors,i=[-1]):
            i[0] += 1
            from controllers.workflow_controller.flowVaribale import FlowVaribale
            return FlowVaribale([vectors[ i[0] % len(vectors)]],label=[vectors[ i[0] % len(vectors)].labels])
        def MBGD(vectors,variable={"batch":0}):
            variable["batch"]%=int(len(vectors)/batchsize)
            i=variable["batch"]*batchsize
            variable["batch"] += 1
            return vectors[i:i+batchsize]

        return PreProcessor(locals()[method],name="inputSelection("+method+")",onlytraining=True,dont_filter=True)

    @staticmethod
    def get_system():
        return PreprocessorSystem._preprocessorSystem

    @staticmethod
    def imgload_Preprocessor(root_dir, type=("png","jpg","bmp"),resize=(36,36),limit=1e10,onehot=False,types=1e10):

        def imgload(vectors=None, file_path=root_dir+"\\", dir_name="", img_names=[], count=[0],typeset=set()):
            import os
            from PIL import Image
            LogSystem.broadcast("start loading images at "+dir_name)
            for path in os.listdir(file_path):
                if os.path.isdir(file_path + path) and count[0] < limit and len(typeset)<types:
                    typeset.add(dir_name+ "." + path)
                    imgload(vectors, file_path + path+"\\", dir_name + "." + path)
                elif path.split(".")[-1] in type and count[0] < limit:
                    count[0] += 1
                    from pylab import array
                    img_names += [[array(Image.open(file_path + path).resize(resize, Image.ANTIALIAS)).tolist(), dir_name]]
            if dir_name=="":
                arr=np.array(img_names)
                if onehot:
                    arr[:,1]=PreprocessorSystem.one_hotcode(arr[:,1])[0]

                return FlowVaribale(arr[:,0].tolist(),label=arr[:,1].tolist())
        return PreProcessor(output=imgload,name="imgload",metadatas={"external":True})

    @staticmethod
    def one_hotcode(types):
        code_dict={list(set(types))[i]:[int(j==i) for j in range(len(set(types)))] for i in range(len(set(types)))}
        codes=[code_dict[t]for t in types]
        return codes,code_dict

    @staticmethod
    def twovalue_Preprocessor(mode="normal", threshold=200):
        def twoValues(vectors,threshold=threshold):


            labels,vectors = vectors.labels,np.array(vectors)
            def k(e):
                return e[0]
            for vector in vectors:

                if mode == "mean":
                    threshold = vector.mean()
                if mode == "ostu":  # max variance of gray
                    variance = []
                    for t in range(255):
                        bg = vector[vector < t]
                        w0 = bg.size / vector.size
                        w1 = 1 - w0
                        m0, m1 = bg.mean(), (vector - bg).mean()
                        variance.append((w0 * w1 * (m0 - m1) ** 2, t))
                    threshold = sorted(variance, key=k)[-1][1]
            return FlowVaribale(np.where(vectors > threshold, 0, 1).tolist(),label=labels)
        return PreProcessor(output=twoValues,name="twovalue")

    @staticmethod
    def gray_Preprocessor(alpha=1):
        def toGray(vectors):
            vs=vectors.shape()
            if vs[-1]>2 and len(vs)>3:
                return (vectors.reshape((vs[0],vs[1] * vs[2], vs[3])) * [0.3, 0.6, 0.9]).sum(-1) * alpha
            return vectors.reshape((vs[0],vs[1] * vs[2]))* alpha
        return PreProcessor(output=toGray,name="gray")

    def get_default(self,net_obj):
        if net_obj.Id in PreprocessorSystem._preprocessors.keys():
            return PreprocessorSystem._preprocessors[net_obj.Id]
        return self.get_new(net_obj)
    def get_new(self,net_obj):
        params = net_obj.parameters.get_parameters()
        return self.set_preprocessor(net_obj.Id, PreprocessorSystem.inputSelection_Preprocessor
        (params["train.method"], params["train.mbgd.batchsize"]))
    def set_preprocessor(self, Id,obj):
        obj=PreprocessorFileObject(obj.set_netid(Id))
        PreprocessorSystem._preprocessors[Id]=obj
        self.dump_offset(PreprocessorSystem.preProcessorGroup,PreprocessorSystem.preProcessorGroup)
        return obj

    def get_preprocessor(self,Id):
        if Id in PreprocessorSystem._preprocessors.keys():
            return PreprocessorSystem._preprocessors[Id]
    @staticmethod
    def excutor(func):
        def wapper(self,tensors):

            if hasattr(self,"preprocessor") and self.preprocessor!=None:
                def f (e):
                    if e.onlytraining:
                        e.enable(self.parameters.get_parameters()["network.training"])
                self.preprocessor.read().forEvery(f)
                tensors=self.preprocessor.read().input(tensors).output()
            return func(self,tensors)
        return wapper
