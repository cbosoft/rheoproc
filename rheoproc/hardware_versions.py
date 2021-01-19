# rheoproc.hardware_version
# named hardware versions defined in this file intended to make SQL queries to the database simpler/less obtuse
# instead of
#   query = 'SELECT * FROM LOGS WHERE [HARDWARE VERSION]>$RANDOM_NUMBERS;'
# it becomes a little more readable:
#   query = f'SELECT * FROM LOGS WHERE [HARDWARE VERSION]>{HW_VER_PND_SPLIT};'

HW_VER_PND_MONO = 20191209 # added pnd: data is combined into a single channel
HW_VER_PND_SPLIT = 20200109 # pnd channel split to positive and negative. work needs to be done to recombine.
HW_VER_PND_FILT = 20200110 # adc decoupling capacitor added
HW_VER_NEWLC = 20200908 # changed to low-range LC

# TODO document remaining hardware versions
