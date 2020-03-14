from FileObjects.offsetFileObject import OffsetFileObject
from controllers.workflow_controller.flowVaribale import FlowVaribale
class DataSetFileObject(OffsetFileObject):
    _Alltypes=["train_y","train_x","train"]
    TrainY,TrainX,Train=_Alltypes

    def __init__(self,data=None,name="",net_id="",group=None,visual=True,type=Train,metadatas=dict({}),loaded=False):
        self._net_id = net_id
        self.metadatas=dict({
            "type":type,
            "version":1,
            "share":0,
            "lineage":None,
        },**metadatas)
        if not group:
            from system.dataSetSystem import DataSetSystem
            group=DataSetSystem.datasetGroup
        super().__init__(data=data,name=name,visual=visual,group=group,metadatas=self.metadatas,loaded=loaded)
    def set_type(self,type):
        if type in DataSetFileObject._Alltypes:
            self.metadatas["type"]=type
    def get_type(self):
        return self.metadatas["type"]
    def set_netid(self,net_id):
        self._net_id=net_id
        return self
    def get_netid(self):
        return self._net_id

    def difference_set(self,another):
        result=[]
        for i in self.read():
            if i not in another.read():
                result.append(i)
        return DataSetFileObject(net_id=self._net_id
                                             ,name=self.name,data=result
                                    , metadatas = {"lineage": "difference_set","version":self.metadatas["version"]+1})




    def split(self,size=5):
        results = []
        block=len(self._data)/size
        location =block
        for l in range(size):
            results.append(DataSetFileObject(net_id=self._net_id
                                             ,name=self.name,data=self._data[block*l:location]
                                             ,metadatas={"lineage":"splited_"+str(l),"version":self.metadatas["version"]+1}))

            location=block*(l+1)
            if location>len(self._data):
                location=len(self._data)
        return results
    def length(self):
        return len(self._data)
    def cut(self,locations):
        results=[]
        start_location=0

        for l in locations+[self.length()]:
            f=DataSetFileObject(net_id=self._net_id
                              , name=self.name, data=self.read()[start_location:l]
                              , metadatas={"lineage": "cuted_" + str(l), "version": self.metadatas["version"]}
                                ,loaded=True)

            results.append(f)
            start_location=l
        return results
    def shuffle(self):
        self._data=self.read().shuffle()
        return self

    def zip(self,batch=1):

        # self._data = self._data.groupby_label(external_label=[str(id(i)) for i in self._data.labels])
        # import numpy
        # print(self._data.shape(),numpy.array(self._data).reshape((256,657)))
        r = {str(id(i)): i for i in self.read().labels}
        self._data=self._data.groupby_label(external_label=[str(id(i)) for i in self._data.labels]).sequece()

        def reshape(x):

            return x.transpose((1,0)+tuple(range(2,len(x.shape()))))

        self._data=reshape(self._data)
        vars=[]
        labels=[]

        for i in range(int(len(self._data)/batch)):
            vars+=(reshape(self._data[i*batch:(i+1)*batch]).reduce(lambda x,y:list(x)+list(y))).toList()

            labels+=(reshape(FlowVaribale([self._data.labels for i in range(batch)])).reduce(lambda x,y:list(x)+list(y))).toList()
        self._data.set(vars)
        self._data.labels=[r[i] for i in labels]
        print(len(labels),batch,labels)

        #zipped = list([[[self._data[i][j], self._data.labels[j]] for j in range(len(self._data[i]))] for i in range(batch)])

        # zipped=list(zip(*[[[j,l]for j in self._data[l]] for l in self._data.labels]))
        # zipped=FlowVaribale(zipped).reduce(lambda x,y:list(x)+list(y))
        # self._data.set(zipped[:,0])
        # self._data.labels=[r[l] for l in zipped[:,1]]
        return self
    def marge(self,datasets):
        if len(datasets)>1:
            from functools import reduce
            return self.set(reduce(lambda x,y:x.read().concat(y.read()),datasets))

    def delete(self):
        result=super().delete()
        from system.dataSetSystem import DataSetSystem
        system=DataSetSystem.get_system()
        DataSetSystem.delete_dataset(system,self.name)
        DataSetSystem.update_dataset(system)

        return result