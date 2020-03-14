
from system.basic.logs.logSystem import LogSystem
from FileObjects.fileObject import FileObject
class LogFileObject(FileObject):

    def __init__(self,data,path=None,encoding="utf-8",group="file"):
        self.encoding=encoding
        super().__init__(data,path,group)

    @LogSystem.logger
    def writeline(self,logger,line,encoding="utf-8"):
        return self.append(logger.format(line),encoding)
