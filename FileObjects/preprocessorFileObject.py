
from preprocessors.preProcesser import PreProcessor
from FileObjects.fileObject import FileObject
class PreprocessorFileObject(FileObject):
    def __init__(self,preprocessor,net_id="",name="",visual=True):
        if isinstance(preprocessor,PreProcessor):
            from system.preprocessorSystem import PreprocessorSystem

            self._net_id = net_id
            self.name = name
            super().__init__(data=preprocessor,group=PreprocessorSystem.preProcessorGroup,visual=visual)

    def get_preprocessor(self):
        return self.read()
    def set_netid(self,net_id):
        self._net_id=net_id
        return self
    def get_netid(self):
        return self._net_id

    def set_preprocessor(self,pre):
        self._data=pre