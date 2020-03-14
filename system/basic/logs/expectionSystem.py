
from initiator.initiator import Initiator
class ExpectionSystem(Initiator,object):
    _Err_Logger = None

    def __init__(self):
        if ExpectionSystem._Err_Logger==None:
            ExpectionSystem._Err_Logger = self
            self._Err_Logger._registed=set({})
            super().__init__()
    @staticmethod
    def error_logger(func):
        ExpectionSystem._Err_Logger._registed.add(func)
        def warpper( *args, **kwargs):
            try:
                result = func( *args, **kwargs)
                return result
            except Exception as e:
                ExpectionSystem._Err_Logger.err_log(e)
                return False
        return warpper



    def err_log(self,e):
        from system.basic.logs.logSystem import LogSystem
        LogSystem._Logger.log(e,repr(e),"exception")
        raise e
