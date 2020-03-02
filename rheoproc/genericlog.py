from rheoproc.varproplog import VariablePropertiesLog

class GenericLog(VariablePropertiesLog):

    def get_start_time(self):
        raise NotImplementedError('This method has not been implemented; use derived class with this implemented properly.')

    def get_end_time(self):
        raise NotImplementedError('This method has not been implemented; use derived class with this implemented properly.')
