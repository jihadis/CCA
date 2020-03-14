from system.basic.files.offsetSystem import OffsetSystem
from FileObjects.dataSetFileObject import DataSetFileObject
import copy
class DataSetSystem(OffsetSystem):



    datasetGroup = "DataSets"
    _dataSetSystem = None
    from system.parameterSystem import ParameterSystem
    system = ParameterSystem.get_system()
    DataSetFileObject.set_default(datasetGroup, ParameterSystem.get_datas(system)["path.datasets"])
    system = OffsetSystem.get_system()
    _dataSets = OffsetSystem.get_OrCreate(system,datasetGroup, set({}))
    print(_dataSets)
    def __init__(self):
        if not DataSetSystem._dataSetSystem:

            DataSetSystem._dataSetSystem = self


        self.update_dataset()
        super().__init__()

    def k_cv(self,dataset,split):
        metas = dataset.matadatas
        metas["share"] = (metas["share"] + 1) % split

        return dataset.split(split)[metas["share"]]



    def eg_(self,dataset,split):

        return self.k_cv(dataset,10)

    #save the last share to make the test
    def normal_(self,dataset,split):

        return  dataset.split(split)[-1]

    validations={

       "K-CV":k_cv,
       "Eg":eg_,
       "Normal":normal_
    }


    @staticmethod
    def get_system():
        return DataSetSystem._dataSetSystem
    def delete_datasets(self,dataset_names,update=True,delete_file=True):

        for dataset_name in dataset_names:
            result = self.query(dataset_name)

            if len(result) > 0:
                for i in result:
                    self._dataSets.remove(i)
                    if delete_file:i.delete()

        if update:
            self.update_dataset()


    def copy_dataset(self,datasetfile,net_id,name):


        f=copy.copy(datasetfile)
        f.set_netid(net_id)
        f.name=name
        self._dataSets.add(f)
        return f

    def has_dataset(self,net,name=None):
        return len(self.query(name, lambda f: f.get_netid() == net.Id))>0


    def get_dataset(self,net,name=None,newversion=True,cross_validation=False):

        if name=="test_x" and cross_validation:
            files = [f for f in self.get_dataset(net,"train_x",False) if not f.metadatas["lineage"]]
            if len(files)>0:
                params=net.parameters.get_parameters()
                files = self.validations[params["test.validation"]](files[-1],params["test.validation.split"])
                files.name = "test_x"
                files.metadatas["share"]=files[-1].metadatas["share"]
                if not params["test.repeat"]:
                    self._dataSets.add(files.difference_set(files))

        else:

            files=self.query(name,lambda f:f.get_netid() == net.Id)
            if newversion:
                files=files[0]
        return files

    def delete_dataset(self, dataset,update=True):
        if dataset in self._dataSets:
            self._dataSets.remove(dataset)
            if update:
                self.update_dataset()

    def update_dataset(self):

        [file.clear()for file in self._dataSets if file]

        self.dump_offset(self.datasetGroup, self.datasetGroup)
        [file.recover() for file in self._dataSets if file]

    def query(self,name,condition=lambda x:True):

        return sorted([d for d in self._dataSets if (d.name==name or not name) and condition(d)]
                      ,key=lambda x:x.metadatas["version"])

    def get_OrCreate(self,dataset_name="",default_value=None,save=False):

        result=self.query(dataset_name)

        if len(result)>0:
            if len(result)==1:
                return result[0]
            return result
        f=DataSetFileObject(default_value,dataset_name,visual=True)

        self._dataSets.add(f)

        self.update_dataset()
        if save: f.save()
        return f

    def get_OrExecution(self,dataset_name, func,save=False,net_id=""):

        from preprocessors.preProcesser import PreProcessor
        from controllers.workflow_controller.flowVaribale import FlowVaribale
        result = self.query(dataset_name)
        if len(result)>0:
            if len(result)==1:
                return result[0]
            return result

        if isinstance(func,PreProcessor):
            default_value=func.input(FlowVaribale([])).output()
        else:
            default_value=func()

        f = DataSetFileObject(default_value, dataset_name, visual=True).set_netid(net_id)

        self._dataSets.add(f)
        self.update_dataset()
        if save:
            f.read()
            f.save()
        return f


