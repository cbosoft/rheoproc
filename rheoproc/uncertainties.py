from rheoproc.sql import execute_sql

def get_percentage_uncertainty(parameter:str, database:str='../data/.database.db'):
    '''returns percentage uncertainty in measurement named $parameter'''

    parameter = parameter.upper()
    res = execute_sql(f'SELECT PERCENTAGE_UNCERTAINTY FROM UNCERTAINTIES WHERE PROPERTY="{parameter}";', database)[0]
    res = float(res['PERCENTAGE_UNCERTAINTY'])
    return res
