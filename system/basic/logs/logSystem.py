

from system.parameterSystem import ParameterSystem


from initiator.initiator import Initiator
from sys import _getframe as g
import time
class LogSystem(Initiator,object):
    _Logger=None



    def __init__(self):
        if LogSystem._Logger==None:
            LogSystem._Logger = self
            self._registed=set({})

    @staticmethod
    def broadcast(mess,type="normal"):
        system=ParameterSystem.get_system()
        if ParameterSystem.get_options(system)["debug."+type]:
            print("["+LogSystem.get_time()+"|Type="+type+"]:"+mess+"\n")

    @staticmethod
    def logger(func):
        LogSystem._Logger._registed.add(func)
        def weapper(self,*args,**kwargs):
            result = func(self, LogSystem._Logger, *args, **kwargs)
            return result
        return weapper

    @staticmethod
    def get_time(code="%Y-%m-%d %H:%M:%S"):
        return time.strftime(code,time.localtime())

    @staticmethod
    def format(line):
        log = "[{}];Project={},Mode={},Type={},Name={},Length={},Content={},{}"

        return log.format(*line)

    def log(self,obj,content="",level="normal"):
        system=ParameterSystem.get_system()
        length="NaN "
        location="called by "+g(3).f_code.co_name+" inline "+str(g(3).f_lineno)
        if hasattr(obj,"__len__"):length=str(len(obj)/1024)
        log_params=[LogSystem.get_time(),
                    ParameterSystem.get_basics(system)["project.name"],
                    level,str(type(obj)),str(obj),length+"kb",content,location]
        formated = LogSystem.format(log_params)
        if level=="exception":
            self.write_errlog(formated)
        else:
            self.write_log(formated,obj,level)

    def write_errlog(self,formated):
        system = ParameterSystem.get_system()
        options = ParameterSystem.get_options(system)
        datas = ParameterSystem.get_datas(system)
        if options["save.exception"]:
            import os
            if not os.path.exists(datas["path.exceptions"]):
                os.makedirs(datas["path.exceptions"])
            with open(datas["path.exceptions"]+"/exception_"+LogSystem.get_time("%Y-%m-%d"),"a+") as f:
                f.write(formated+"\n")


    def write_log(self,formated,obj,level):
        from system.basic.files.fileObjectSystem import FileObjectSystem
        system = ParameterSystem.get_system()
        options=ParameterSystem.get_options(system)
        on_secreen,on_save=ParameterSystem.get_parameters(system,level,options)
        if on_secreen:
            print(formated)
        if on_save:
            group = "log." + level
            fileObjects=FileObjectSystem.get_fileObjects()
            datas = ParameterSystem.get_datas(system)
            if group not in fileObjects.keys():
                from FileObjects.logFileObject import LogFileObject
                log_fileObjects=[LogFileObject(obj,datas["path.debugs"],group=group)]
                FileObjectSystem.update_fileObject(log_fileObjects)
            else :
                log_fileObjects=fileObjects[group]
            for log_fileObject in log_fileObjects:
                log_fileObject.append(formated)




