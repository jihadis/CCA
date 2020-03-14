import os
from system.parameterSystem import ParameterSystem
from initiator.initiator import Initiator

class ParameterInitiator(Initiator):

    def __init__(self,argv):
        exepath=argv[0].rstrip(argv[0].split("/")[-1])
        self.params=argv[1:]
        self.basic_defaults={
            "variable.system.exepath":exepath,
            "basic.project.name":"CCA_test",
            "basic.data.path.rootdir":exepath+".CCA/",

        }
        self.muteble_defaults={
            "basic.produce.path.product": self.basic_defaults["basic.data.path.rootdir"]+self.basic_defaults["basic.project.name"]+"/products/",
            "basic.produce.path.record": self.basic_defaults["basic.data.path.rootdir"]+self.basic_defaults["basic.project.name"]+"/records/",
            "basic.produce.path.data": self.basic_defaults["basic.data.path.rootdir"]+self.basic_defaults["basic.project.name"]+"/datas/",
            "basic.produce.path.offsets": self.basic_defaults["basic.data.path.rootdir"]+self.basic_defaults["basic.project.name"]+"/offsets/",
        }
        self.muteble_defaults.update({
            "basic.project.path.rootdir": exepath+self.basic_defaults["basic.project.name"],
            "basic.project.path.configures": exepath + self.basic_defaults["basic.project.name"]+"/config",
            "data.path.images":self.muteble_defaults["basic.produce.path.record"] + "images",
            "data.path.debugs": self.muteble_defaults["basic.produce.path.record"] + "debugs",
            "data.path.exceptions": self.muteble_defaults["basic.produce.path.record"] + "exceptions",
            "data.path.lineages": self.muteble_defaults["basic.produce.path.data"] + "lineages",
            "data.path.fileobjects": self.muteble_defaults["basic.produce.path.data"] + "fileobjects",
            "data.path.datasets":self.muteble_defaults["basic.produce.path.data"] + "datasets",
            "data.path.trains": self.muteble_defaults["basic.produce.path.data"] + "trains",
            "data.path.tests": self.muteble_defaults["basic.produce.path.data"] + "tests",
            "data.path.offsets": self.muteble_defaults["basic.produce.path.offsets"] ,
            "data.path.counters": self.muteble_defaults["basic.produce.path.offsets"]+"counters" ,
            "data.path.params": self.muteble_defaults["basic.produce.path.data"] + "params",
            "data.path.preprocessors": self.muteble_defaults["basic.produce.path.data"] + "preprocessors",
            "data.path.models": self.muteble_defaults["basic.produce.path.product"] + "models",
            "data.path.networks": self.muteble_defaults["basic.produce.path.product"] + "networks",
            "option.debug.exception":True,
            "option.debug.message": True,
            "option.debug.normal": True,
            "option.save.overlap": False,
            "option.save.exception": True,
            "option.save.message": False,
            "option.save.normal": False,
            "param.save.encoding": "utf-8",
            "param.save.interval": 60,


        })


        self.defaults=dict(self.basic_defaults,**self.muteble_defaults)
        

            
            
        super().__init__()


    def initialize(self):
        self.parameter=self.defaults.copy()
        configfile_path=self.parameter["basic.project.path.configures"]

        if os.path.exists(configfile_path):
            configfiles =["external.configure="+configfile_path+p for p in os.listdir(configfile_path)]
        else:
            configfiles=[]

        for i in configfiles+self.params:
            if "external.configure=" in i:
                self.parameter.update({j.split("=")[0]: j.split("=")[1] for j in open(i.split("=")[1]).readlines()})
            else:
                self.parameter[i.split("=")[0]] = i.split("=")[1]

        ParameterSystem(self.parameter)
        self.show_parameters()
        return True

    def show_parameters(self):
        from system.basic.logs.logSystem import LogSystem
        strs="\nAll Parameters of CCA {\n"
        system = ParameterSystem.get_system()
        strs+=("\n".join([w+":"+("\n   ["+"\n   [".join([str(k)+"]:  "+str(type(v))+"  "
            +str(v) for k,v in system._query(w).items()])) for w in ["variable","data","basic","param","option"]]))
        LogSystem.broadcast(strs+"\n}", "message")
