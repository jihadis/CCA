from FileObjects.offsetFileObject import OffsetFileObject
class MoudelFileObject(OffsetFileObject):


    def __init__(self,net_id,metadatas,_model,visual=True,name="",*args,**kwargs):
        self._net_id=net_id
        self.metadatas=dict({
            "version":0,
            "epoch":0,
            "accuracy":0
        },**metadatas)
        from system.modelSystem import ModelSystem
        super().__init__(_model,group=ModelSystem.modelGroup,visual=visual,name=name,*args,**kwargs)

    def get_netid(self):
        return self._net_id

    def get_model(self):
        return self.read()

