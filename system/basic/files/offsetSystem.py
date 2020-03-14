from system.basic.files.fileObjectSystem import FileObjectSystem
import time
from system.parameterSystem import ParameterSystem
from system.basic.logs.expectionSystem import ExpectionSystem
from FileObjects.fileObject import FileObject
#包含所有与工程有关的偏移量文件
class OffsetSystem(FileObjectSystem):
    _offsetSystem=None
    _offsets={}#container of varibales
    _loop_dumps=set({})
    offsetGroup="offsetGroup"
    system = ParameterSystem.get_system()
    FileObject.set_default(offsetGroup,ParameterSystem.get_datas(system)["path.offsets"])
    def __init__(self):
        if not OffsetSystem._offsetSystem:
            OffsetSystem._offsetSystem = self
            fileObjects=self.get_fileObject(OffsetSystem.offsetGroup)
            self.read_offsets(fileObjects)
            #threading.Thread(target=self.loop_dump).start()

    def read_offsets(self,fileObjects):
        datas = {f.metadatas["offset_group"]:f.read() for f in fileObjects if f.enable  and  "offset_group" in f.metadatas.keys()}######
        OffsetSystem._offsets = datas

            

    @staticmethod
    def get_system():
        if OffsetSystem._offsetSystem:
            return OffsetSystem._offsetSystem

    def get_OrExecution(self,offset_Id, func):
        from preprocessors.preProcesser import PreProcessor
        if self.get_offset(offset_Id)!=None:

            return self.get_offset(offset_Id)
        if isinstance(func,PreProcessor):
            default_value=func.input([]).output()
        else:
            default_value=func()

        if isinstance(default_value,tuple):
            default_value=super().create_fileObject(*default_value)

        return self.update_offset(offset_Id, default_value)

    def get_OrCreate(self,offset_Id,default_value,loop_update=False):

        if self.get_offset(offset_Id)!=None:
            return self.get_offset(offset_Id)
        if loop_update:
            OffsetSystem._loop_dumps.add(offset_Id)
        if isinstance(default_value,tuple):
            default_value=super().create_fileObject(*default_value)
        return self.update_offset(offset_Id, default_value)

    def loop_dump(self):#执行定期保存任务
        system=ParameterSystem.get_system()
        interval=ParameterSystem.get_params(system)["save.interval"]
        while True:
            time.sleep(interval)
            for offset_Id in OffsetSystem._loop_dumps:
                self.dump_offset(offset_Id)

    def get_offset(self, offset_Id):
        if offset_Id in OffsetSystem._offsets.keys():
            return OffsetSystem._offsets[offset_Id]



    @ExpectionSystem.error_logger
    def update_offset(self, group, obj,name=None):
        r=self.set_offset(group,obj)
        self.dump_offset(group,name)
        return r
    def create_offsetFileObject(self,data,name):
        from FileObjects.offsetFileObject import OffsetFileObject
        return OffsetFileObject(data,name)

    @ExpectionSystem.error_logger
    def dump_offset(self, offset_Id,name=None):


        fileObjects=self.get_fileObject(OffsetSystem.offsetGroup,name)

        if offset_Id not in [f.metadatas["offset_group"] for f in fileObjects if hasattr(f,"metadatas")]:
            fileObject=self.create_offsetFileObject(OffsetSystem._offsets[offset_Id],name)
            fileObject.metadatas["offset_group"]=offset_Id
            fileObject.save()
            self.dump_fileObject(fileObject)

        else:

            [f.update(OffsetSystem._offsets[offset_Id]) for f in fileObjects if hasattr(f,"metadatas") and f.metadatas["offset_group"]==offset_Id]
        #根据当前_offsets[offset_Id] 通过FileOBJECT 保存到系统目录

    @ExpectionSystem.error_logger
    def set_offset(self, offset_Id,obj):
        OffsetSystem._offsets[offset_Id] = obj
        return obj
    