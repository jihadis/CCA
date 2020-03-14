"""
Parameter of CCA

Format : project.type.[....]

projects:
    CCA(python) #AI engine
    BCC(python) #network service
    BSS(scala) #bigdata
types :
    option   #true or false
    param   #static values
    variable #muteble values
    basic    #project settings
    data     #file paths
"""
from initiator.initiator import Initiator
class ParameterSystem(Initiator,object):
    _parameterSystem=None
    _parameters=None
    def __init__(self,parameters={}):

        ParameterSystem._parameters = parameters
        if not ParameterSystem._parameterSystem:
            ParameterSystem._parameterSystem=self


    @staticmethod
    def get_system():
        if ParameterSystem._parameterSystem:
            return ParameterSystem._parameterSystem
    def get_options(self):
        return self._query("option")
    def get_params(self):
        return self._query("param")
    def get_basics(self):
        return self._query("basic")
    def get_datas(self):
        return self._query("data")
    def get_variables(self):
        return self._query("variable")
    def _query(self,word):
        return {p.lstrip(word+"."): v for p, v in ParameterSystem._parameters.items() if word==p.split(".")[0]}
    def update(self,keyword,value):
        ParameterSystem._parameters[keyword]=value
    def delete(self,keyword):
        ParameterSystem._parameters.pop(keyword)
    def get_parameter(self, keyword):
        return ParameterSystem._parameters[keyword]
    def get_parameters(self,keyword="",dict=None):
        if not dict:dict=ParameterSystem._parameters
        return {p:v for p,v in dict if keyword in p}