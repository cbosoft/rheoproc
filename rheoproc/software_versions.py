# rheoproc.software_versions
# annotated software versions to ease the creation of SQL queries.
# instead of
#   query = 'SELECT * FROM LOGS WHERE [SOFTWARE VERSION]>$RANDOM_NUMBERS;'
# it becomes a little more readable:
#   query = f'SELECT * FROM LOGS WHERE [SOFTWARE VERSION]>{SW_VER_COMPLETE_LOG};'

SW_VER_LIMITED_LOG = 20190101 # logs produced under this hardware version log from after settle time
SW_VER_COMPLETE_LOG = 20191018 # logs produced under this ver log from before startup to end: including warmup

# TODO annotate rest of versions
