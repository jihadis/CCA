import dill
import os
import hashlib
import sys
import time
from system.basic.logs.expectionSystem import ExpectionSystem
from system.basic.files.fileObjectSystem import FileObjectSystem



class FileObject(object): #需要动态更新的文件对象

    save_dirctorys={"file":"/".join(sys.argv[0].split("/")[:-1])+"/dump_files/"}
    path,dir,group,name,md5,_data,_loaded =None,None,None,None,None,None,None

    def __init__(self, data=None,name=None, group="file", enable=True,
                 visual=False,loaded=False):

        if not name:
            name="dumpfile_"+hashlib.md5(bytes(str(time.time()),"utf-8")).hexdigest()
        self.md5=hashlib.md5(bytes(str(group+name),"utf-8")).hexdigest()
        self.dir=self.get_default(group)
        self.name=name
        self.path = self.dir+'/' + self.name
        self.group=group
        self.enable = enable
        self._loaded=loaded
        if not visual:
            FileObjectSystem.dump_fileObject(self)
        self._data=data

    @ExpectionSystem.error_logger
    def recover(self):
        if self.md5 in FileObjectSystem._recovers.keys():
            self._data,self._loaded=FileObjectSystem._recovers[self.md5]
    @ExpectionSystem.error_logger
    def clear(self):
        FileObjectSystem._recovers[self.md5]=[self._data,self._loaded]
        self._data,self._loaded=None,False

    @ExpectionSystem.error_logger
    def set(self,value):
        self._data=value
    @ExpectionSystem.error_logger
    def read(self,encoding=None):
        if os.path.exists(self.path)and (not self._data or not self._loaded) :
            self._loaded=True
            self._data=dill.load(open(self.path,"rb",encoding=encoding))
            return self._data
        return self._data

    @ExpectionSystem.error_logger
    def delete(self):
        try:
            os.remove(self.path)
            self._data, self._loaded = None, False

        except FileNotFoundError:
            return False
        return True

    @ExpectionSystem.error_logger
    def save(self,encoding=None):



        if self._data:
            if not os.path.exists(self.dir):
                os.makedirs(self.dir)
            dill.dump(self._data, open(self.path, "wb", encoding=encoding))
            # logger.log(self._data,"saving fileObject at "+self.path)
            self._loaded = False


    @ExpectionSystem.error_logger
    def isFull(self):
        return os.path.exists(self.path)

    @ExpectionSystem.error_logger
    def isLoaded(self):
        return self._loaded

    @ExpectionSystem.error_logger
    def update(self,data,encoding=None):
        self._loaded=True
        self._data=data
        self.save(encoding)

    @ExpectionSystem.error_logger
    def append(self,line,encoding="utf-8"):
        if not self.path and self.group in FileObject.save_dirctorys.keys():
            self.path=FileObject.save_dirctorys[self.group]+self.name
        open(self.path,"a+",encoding=encoding).write(line+"\n")
        self._loaded = False
    def get_default(self,group):
        if group in FileObject.save_dirctorys.keys():
            return FileObject.save_dirctorys[group]
    @staticmethod
    @ExpectionSystem.error_logger
    def set_default(group,dir):
        FileObject.save_dirctorys[group]=dir

