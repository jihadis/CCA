import sys
from system.basic.logs.logSystem import LogSystem
#start systems
def start():
    print("Starting CCA..")
    from initiator.parameterInitiator import ParameterInitiator
    Initiator=ParameterInitiator(sys.argv)
    if Initiator.initialize():
        systems=[Initiator]
        LogSystem.broadcast("starting all systems..","message")
        systems.append(LogSystem())
        LogSystem.broadcast("LogSystem started")
        from system.basic.logs.expectionSystem import ExpectionSystem
        systems.append(ExpectionSystem())
        LogSystem.broadcast("ExpectionSystem started")
        from system.basic.files.fileObjectSystem import FileObjectSystem
        systems.append(FileObjectSystem())
        LogSystem.broadcast("FileObjectSystem started")
        from system.basic.files.offsetSystem import OffsetSystem
        systems.append(OffsetSystem())
        LogSystem.broadcast("OffsetSystem started")
        from system.modelSystem import ModelSystem
        systems.append(ModelSystem())
        LogSystem.broadcast("ModelSystem started")
        from system.preprocessorSystem import PreprocessorSystem
        systems.append(PreprocessorSystem())
        LogSystem.broadcast("PreprocessorSystem started")
        from system.train.trainingParameterSystem import TrainingParameterSystem
        systems.append(TrainingParameterSystem())
        LogSystem.broadcast("TrainingParameterSystem started")
        from system.dataSetSystem import DataSetSystem
        systems.append(DataSetSystem())
        LogSystem.broadcast("DataSetSystem started")
        from system.train.trainingCounterSystem import TrainingCounterSystem
        systems.append(TrainingCounterSystem())
        LogSystem.broadcast("TrainingCounterSystem started")
        LogSystem.broadcast("all systems is start successfully", "message")

        print("============================================")
        return systems

if __name__=="__main__":
    start()