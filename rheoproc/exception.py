class GenericRheoprocException(Exception):
    '''Base class from which rheproc exceptions derive'''

class FileTypeError(GenericRheoprocException):
    '''Unexpected file type encountered.'''


class TooManyResultsError(GenericRheoprocException):
    '''Too many results returned from query.'''


class QueryError(GenericRheoprocException):
    '''Something went wrong executing an SQL query'''


class PathError(GenericRheoprocException):
    '''Path is not valid'''

class PathNotAFileError(PathError):
    '''Path is not a file or does not exist.'''

class PathNotADirError(PathError):
    '''Path is not a directory or does not exist.'''


class TimeRationalError(GenericRheoprocException):
    '''Rationalisation of two timeseries has gone wrong and the result does not match.'''


class CategoryError(GenericRheoprocException):
    '''The data you requested cannot be found. The category for the data was not requested.'''


class DataUnavailableError(GenericRheoprocException):
    '''The data you requested is missing in the original log file and therefore cannot be obtained.'''


class NaNError(GenericRheoprocException):
    '''A NaN was encountered where there should be a number.'''

class ZeroSpeedError(GenericRheoprocException):
    '''Zero speed was found; is the calc corrupt?'''
