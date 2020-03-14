from FileObjects.fileObject import FileObject


class OffsetFileObject(FileObject):

    def __init__(self,data=None,name="",group=None,visual=False,metadatas=dict(),loaded=False):
        self.metadatas=dict({},**metadatas)

        if not group:
            from system.dataSetSystem import OffsetSystem
            group=OffsetSystem.offsetGroup

        super().__init__(data=data,group=group,name=name,visual=visual,loaded=loaded)


    def clear(self):
        if isinstance(self.metadatas,dict):
            self.metadatas=":;:".join([str(kv[0])+"][]["+str(kv[1]) for kv in self.metadatas.items()])
            super().clear()

    def recover(self):
        if isinstance(self.metadatas,str):

            if "][][" in  self.metadatas:
                self.metadatas={kv.split("][][")[0]:kv.split("][][")[1] for kv in self.metadatas.split(":;:")}
            else:
                self.metadatas = dict({})
            super().recover()

