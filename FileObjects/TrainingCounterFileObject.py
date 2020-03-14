from FileObjects.fileObject import FileObject
class TrainingCounterFileObject(FileObject):
    def __init__(self,counter,net_id="",name="",visual=True):

            from system.train.trainingCounterSystem import TrainingCounterSystem

            self._net_id = net_id
            self.name = name
            super().__init__(data=counter,group=TrainingCounterSystem.trainingCounterGroup,visual=visual)

    def get_counter(self):
        return self.read()
    def set_netid(self,net_id):
        self._net_id=net_id
        return self
    def get_netid(self):
        return self._net_id
    def update_counters(self,counter):
        self._data=set(self.read()).union(counter)
        return self
    def count(self,lineage,broadcast=False,net_metadatas=None,net_id=None,plot=False,parameters=None):
        if broadcast:
            from system.basic.logs.logSystem import LogSystem
            LogSystem.broadcast("====Count of trainings====\n  netid:"+net_id+"\n","message")
        counters=self.read()
        for counter in counters:
            counter.input(lineage,net_id).output(broadcast)
        from system.train.trainingCounterSystem import TrainingCounterSystem
        if broadcast and plot:
            TrainingCounterSystem.get_system().plot(net_id,counters,net_metadatas,parameters)
    def set_counters(self,ctr):
        self._data=ctr