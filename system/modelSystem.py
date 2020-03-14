from system.basic.files.offsetSystem import OffsetSystem
from system.parameterSystem import ParameterSystem
from models.neuronNetWorkModel import NeuronNetWorkModel
from FileObjects.moudelFileObject import MoudelFileObject
class ModelSystem(OffsetSystem):
    modelGroup = "Models"
    _modelSystem = None

    system = ParameterSystem.get_system()
    MoudelFileObject.set_default(modelGroup, ParameterSystem.get_datas(system)["path.models"])
    system = OffsetSystem.get_system()
    _Models = OffsetSystem.get_OrCreate(system, modelGroup, set({}))

    def __init__(self):
        if not ModelSystem._modelSystem:
            ModelSystem._modelSystem = self
        super().__init__()

    @staticmethod
    def get_system():
        return ModelSystem._modelSystem

    def get_models(self,net_id,condition=lambda f:True):

        return [f for f in ModelSystem._Models if isinstance(f,MoudelFileObject) and f.get_netid()==net_id and condition(f)]

    #get top accuracy model
    def get_best(self,net_id):
        return sorted(self.get_models(net_id),key=lambda f:f.metadatas["accuracy"])[0]

    # get most epoch model
    def get_old(self,net_id):
        return sorted(self.get_models(net_id), key=lambda f: f.metadatas["epoch"])[0]

    def get_version(self,net_id,v=1.0):
        return self.get_models(net_id,condition=lambda f:f.metadatas["version"]==v)

    def update(self,net_id,metadatas,model):
        if isinstance(model,NeuronNetWorkModel):
            modelobj=self.get_old(net_id)
            modelobj.metadatas=metadatas
            modelobj.update(model)
            modelobj.save()


    def create_model(self,net):

        model = NeuronNetWorkModel([l.get_matrix() for l in net.layers.values()],
                                   [l.get_biases() for l in net.layers.values()])
        model_file=MoudelFileObject(net.Id, net.get_metadata(), model)
        ModelSystem._Models.add(model_file)
        self.dump_offset(ModelSystem.modelGroup, ModelSystem.modelGroup)
        return model_file

    def save_orlap(self,model):

        system = ParameterSystem.get_system()
        overlap = system.get_options()["save.overlap"]
        model_system = ModelSystem.get_system()
        if overlap :
            model_system.update(model.get_netid(),model.metadatas, model.get_model())
        else:
            model.save()

