from FileObjects.fileObject import FileObject


class TrainingParameterFileObject(FileObject):
    default_parameters={}

    def __init__(self,parameters,net_id="",name="",*args,**kwargs):
        from system.train.trainingParameterSystem import TrainingParameterSystem
        parameters=dict(self.default_parameters,**parameters)
        self._net_id=net_id
        self.name=name
        super().__init__(data=parameters,group=TrainingParameterSystem.trainingGroup,*args,**kwargs)

    def get_parameters(self,keyword=""):
        if keyword!="":
            return {k.replace(keyword + ".", ""): v for k, v in self.read().items() if k.startswith(keyword)}
        return self.read()

    def update_parameters(self,news):
        self._data=dict(self._data,**news)
        return self

    def update_parameter(self,k,v):
        self._data[k]=v

    def set_netid(self,net_id):
        self._net_id=net_id
        return self
    def get_netid(self):
        return self._net_id

    # def __str__(self):
    #     return super().__str__()