class FileTypeError(Exception):
    '''Unexpected file type encountered.'''


class TooManyResultsError(Exception):
    '''Too many results returned from query.'''


class QueryError(Exception):
    '''Something went wrong executing an SQL query'''


class PathError(Exception):
    '''Path is not valid'''

class PathNotAFileError(PathError):
    '''Path is not a file or does not exist.'''

class PathNotADirError(PathError):
    '''Path is not a directory or does not exist.'''


class TimeRationalError(Exception):
    '''Rationalisation of two timeseries has gone wrong and the result does not match.'''


class CategoryError(Exception):
    '''The data you requested cannot be found. The category for the data was not requested.'''


class DataUnavailableError(Exception):
    '''The data you requested is missing in the original log file and therefore cannot be obtained.'''
