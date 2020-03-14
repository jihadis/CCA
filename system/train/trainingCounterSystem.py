from system.basic.files.offsetSystem import OffsetSystem
from FileObjects.TrainingCounterFileObject import TrainingCounterFileObject
from plotter.networkPlotter import NetworkPlotter
import math
import numpy
from algorithms.tools.Toolkit import *
from counters.counter import Counter
class TrainingCounterSystem(OffsetSystem):
    trainingCounterGroup = "trainingCounters"
    _trainingCounterSystem = None
    from system.parameterSystem import ParameterSystem
    system = ParameterSystem.get_system()
    TrainingCounterFileObject.set_default(trainingCounterGroup, ParameterSystem.get_datas(system)["path.counters"])
    system = OffsetSystem.get_system()
    _counters = OffsetSystem.get_OrCreate(system, trainingCounterGroup, dict({}))

    def __init__(self):
        default_counter = {
            "Loss": TrainingCounterSystem.Loss_Counter(),

            "L1": TrainingCounterSystem.L1_Counter(),
            "L2": TrainingCounterSystem.L2_Counter(),

            "Accuracy":TrainingCounterSystem.accuracy_Counter(),
            "TrainSpeed":TrainingCounterSystem.trainSpeed_Counter()
            # "Roc": TrainingCounterSystem.Roc_Counter(),
            # "P-R": TrainingCounterSystem.Pr_Counter(),
        }
        if not TrainingCounterSystem._trainingCounterSystem:
            TrainingCounterSystem._trainingCounterSystem = self
        default_parameters = TrainingCounterFileObject(list(default_counter.values()), visual=True)


        def updates(c):
            return default_parameters.update_counters(list(dict(default_counter,**c).values()))
        self.network_default_counters = {
            "ConvolutionalNetWork": lambda :updates({

            }),
            "GanNetwork": lambda :updates({
                "Loss":TrainingCounterSystem.Gan_Loss_Counter
            }),
            "InfoGanNetwork":lambda : updates({
                "Loss":TrainingCounterSystem.Info_Loss_Counter

            }),

            "NeuronNetWork": lambda :updates({})

        }
        super().__init__()


    def plot(self,net_id,counters,net_metadatas,parameters):

            NetworkPlotter.plot_OrCreate(net_id,counters,net_metadatas,parameters)


    @staticmethod
    def trainSpeed_Counter(name="TrainSpeed"):

        import time
        def func(lineage,old_epoch = [0, time.time()]):
            import time
            if lineage["epoch"]==[]:
                return []
            time=time.time()
            dv=(lineage["epoch"][-1] - old_epoch[0])
            if dv!=0:
                res=(lineage["epoch"][-1]-old_epoch[0]) / (time - old_epoch[1])
                old_epoch.clear()
                old_epoch.extend([lineage["epoch"][-1],time])
                return res
            return 0
        return Counter(func, name)
    @staticmethod
    def get_system():
        return TrainingCounterSystem._trainingCounterSystem
    @staticmethod
    def accuracy_Counter(name="accuracy"):
        def func(lineage):
            if lineage["accuracy"]==[]:
                return []
            return lineage["accuracy"][-1]
        return Counter(func, name)

    @staticmethod
    def Auc_Counter(name="Auc"):
        def func(lineage):
            total_auc = []
            for i in range(numpy.shape(lineage["y_out"])[-1]):
                auc = sum([(lineage["x_out"][j + 1][i] - lineage["x_out"][j][i]) * (
                            lineage["y_out"][j + 1] + lineage["y_out"][j])
                           for j in range(len(lineage["y_out"]) - 1)]) / 2
                total_auc.append(auc)
            return total_auc
        return Counter(func,name)

    @staticmethod
    def Roc_Counter():
        def func(lineage):
            total_roc=[]
            types=numpy.shape(lineage["y_out"])[-1]
            for i in range(types):
                total_real=len([j for j in lineage["y_out"] if numpy.argmax(j)==i])
                total_fake=len(lineage["y_out"])-total_real
                predict_real=len([1 for x,y in zip(lineage["x_out"],lineage["y_out"])if(numpy.argmax(x),numpy.argmax(y))==(i,i)])
                predict_fake=len([1 for x,y in zip(lineage["x_out"],lineage["y_out"])if numpy.argmax(x)==i and  numpy.argmax(y)!=i])*(types-1)
                real_positive=predict_real/total_real
                fake_positive=predict_fake/total_fake
                roc=real_positive/fake_positive
                total_roc.append(roc)
            return total_roc
        return Counter(func,"roc")

    @staticmethod
    def Pr_Counter():
        def func(lineage):
            lineage["roc"]
        return Counter(func,"p-r")

    @staticmethod
    def Loss_Counter(name="loss"):
        def func(lineage):
            if "loss" in lineage:
                return lineage["loss"][-1]
            return []

        return Counter(func,name,metadatas={"plot.color":"r","plot.priority":1.5,"plot.aspectRatio":0.88})

    @staticmethod
    def L1_Counter():
        def func(lineage):
            v = [0]
            def f(e): v[0] += abs(e)
            forEvery(f,lineage["weights"][-1])
            return v[0]

        return Counter(func,"L1",metadatas={"plot.color":"g"})

    @staticmethod
    def L2_Counter():
        def func(lineage):

            v = [0]
            def f(e): v[0] += e**2
            forEvery(f, lineage["weights"][-1])
            return math.sqrt(v[0])

        return Counter(func, "L2 (Variance)",metadatas={"plot.color":"b"})

    @staticmethod
    def Gan_Loss_Counter():
        def func(lineage):
            return math.log(lineage["GAN-G_loss"])+math.log(1-lineage["GAN-D_loss"])
        return Counter(func,"GanLoss")

    @staticmethod
    def Info_Loss_Counter():
        def func(lineage):
            return (lineage["InfoGAN-Type"][0]-lineage["InfoGAN-Q_out"][0])**2
        return Counter(func, "Infoloss")


    def delete_counter(self, counter,update=True):
        if counter in self._counters:
            self._counters.remove(counter)
            if update:
                self.update_counter()
    def update_counter(self):

        [file.clear()for file in self._counters if file]
        self.dump_offset(TrainingCounterSystem.trainingCounterGroup, TrainingCounterSystem.trainingCounterGroup)
        [file.recover() for file in self._counters if file]

    def get_OrCreate(self, counter_name="", default_value=None, loop_update=False,net_metadatas=None):
        if counter_name in self._counters.keys():
            return self._counters[counter_name]
        #f = TrainingCounterFileObject(super().get_OrCreate(counter_name, default_value, loop_update),net_metadatas)
        self.update_counter()
        return default_value

    def get_default(self, net_obj):
        name = [c.__name__ for c in type(net_obj).mro() if c.__name__ in self.network_default_counters.keys()][0]
        return self.get_OrCreate(net_obj.Id, self.network_default_counters[name]().set_netid(net_obj.Id)
                                 ,net_metadatas=net_obj.metadatas)