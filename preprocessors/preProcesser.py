from structrue.neuronStruct import NeuronStruct
def i(x):return x
class PreProcessor(NeuronStruct):

    def __init__(self,input=i,output=i,name="", metadatas = dict({}),onlytraining=False,dont_filter=False):



        self.input_func=input
        self.output_func=output
        metadatas = dict({
            "name":name,
            "type": "PreProcessor",
            "external": False,
            "concats":[]
        }, **metadatas)
        super().__init__(name=name,metadatas=metadatas)
        self._synchronisms=[]
        self._processed=dict({})
        self._enable=True
        self.onlytraining=onlytraining
        self.dont_filter=dont_filter
    def enable(self,b):
        self._enable=b
    def get_concats(self):
        return self._synchronisms
    def empty(self,**kwargs):
        return super().empty(_synchronisms=
                        [p.empty() for p in self._synchronisms],_processed=dict({}),start_tensors=None,**kwargs)
    def input(self,tensors):
        self.start_tensors=tensors
        return self

    def forEvery(self,func):
        func(self)
        [s.forEvery(func) for s in self._synchronisms]



    def get_processed(self,result):

        if self._enable:
            #result=self.output_func(result)
            if self.start_tensors.id in self._processed.keys()and self.onlytraining :
                print("in",self.name,result)
                result=self._processed[self.start_tensors.id]
            else:
                result=self.output_func(self.input_func(self.start_tensors))
                if not self.dont_filter and self.onlytraining:
                    self._processed[self.start_tensors.id]=result
        return result
    def output(self,*args):
        result=self.get_processed(self.start_tensors)
        for p in self._synchronisms:
            if isinstance(p, PreProcessor):
                result = p.input(result).output()
        return result
    def set_netid(self,id):
        self.set_Id(id)
        return self
    def get_line(self):
        return self._synchronisms
    def concat(self,another):
        if isinstance(another,PreProcessor):
            if another.name==self.name:
                return another
            self.metadatas["concats"].append((another,another.name))
            self._synchronisms.append(another)
        return self
