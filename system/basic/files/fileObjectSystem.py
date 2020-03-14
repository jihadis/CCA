import pickle
import os
from functools import reduce
from system.parameterSystem import ParameterSystem
from system.basic.logs.expectionSystem import ExpectionSystem

from initiator.initiator import Initiator
class FileObjectSystem(Initiator,object):

    _FileObjects={}
    _recovers={}
    @staticmethod
    @ExpectionSystem.error_logger
    def create_fileObject(data,name,group):
        from FileObjects.fileObject import FileObject
        return FileObject(data,name,group)
    @staticmethod
    @ExpectionSystem.error_logger
    def dump_fileObject(fileobject):
        from FileObjects.fileObject import FileObject
        if isinstance(fileobject,FileObject):
            fileobject.clear()
            system = ParameterSystem.get_system()
            path = ParameterSystem.get_datas(system)["path.fileobjects"]
            if not os.path.exists(path):
                os.makedirs(path)
            pickle.dump(fileobject,open(path + "/fileobject_" + fileobject.md5,"wb"),0)
            fileobject.recover()

        else:
            raise EOFError("param fileobject is not type of FileObject")

    @staticmethod
    @ExpectionSystem.error_logger
    def delete_fileObject(fileobject):
        from FileObjects.fileObject import FileObject
        if isinstance(fileobject, FileObject):
            system = ParameterSystem.get_system()
            path = ParameterSystem.get_datas(system)["path.fileobjects"]
            signal=path+"/"+"fileobject_"+fileobject.md5
            if os.path.exists(signal):
                os.remove(signal)


    @staticmethod
    @ExpectionSystem.error_logger
    def update_fileObject(fileobject):
        FileObjectSystem.dump_fileObject(fileobject)
        if not fileobject.group in FileObjectSystem._FileObjects.keys():
            FileObjectSystem._FileObjects[fileobject.group]=[]
        FileObjectSystem._FileObjects[fileobject.group] += [fileobject]
    @staticmethod
    @ExpectionSystem.error_logger
    def get_OrCreate(key,default_value):
        if key in FileObjectSystem._FileObjects.keys():
            return FileObjectSystem._FileObjects[key]
        FileObjectSystem._FileObjects[key]=[FileObjectSystem.create_fileObject(*default_value)]
        return FileObjectSystem._FileObjects[key]

    @staticmethod
    @ExpectionSystem.error_logger
    def get_OrExecution(key,func):
        if key in FileObjectSystem._FileObjects.keys():
            return FileObjectSystem._FileObjects[key]
        FileObjectSystem._FileObjects[key] = [func()]
        return FileObjectSystem._FileObjects[key]


    @staticmethod
    @ExpectionSystem.error_logger
    def read_fileObjects():
        system = ParameterSystem.get_system()
        allfiles = FileObjectSystem.read_all(ParameterSystem.get_datas(system)["path.fileobjects"])
        [f.recover() for f in allfiles]
        file_dict = {file_object.group for file_object in allfiles}
        file_objects = {k: reduce(lambda x, y: x + [y], [[]] + [f for f in allfiles if f.group == k]) for k in
                        file_dict}
        FileObjectSystem._FileObjects=file_objects

    @staticmethod
    @ExpectionSystem.error_logger
    def get_fileObjects():
        if not FileObjectSystem._FileObjects:
            FileObjectSystem.read_fileObjects()
        return FileObjectSystem._FileObjects

    @staticmethod
    @ExpectionSystem.error_logger
    def get_fileObject(group,name=None):
        if not FileObjectSystem._FileObjects:
            FileObjectSystem.read_fileObjects()
        if group in FileObjectSystem._FileObjects.keys():
            group_file=FileObjectSystem._FileObjects[group]
            if name:
                return [f for f in group_file if f.name==name]
            return group_file
        return []

    @staticmethod
    @ExpectionSystem.error_logger
    def read_all(dir):
        allfile = []
        if not os.path.exists(dir):
            os.makedirs(dir)
        else:
            for file in os.listdir(dir):
                with open(dir + "/" + file, "rb") as f:
                    allfile.append(pickle.load(f))
        return allfile

