# rheoproc.nansafemath
# uses the numpy nan-ufuncs to do maths with data with gaps in it.
# 'import rheoproc.nansafemath as np' (mostly) a drop-in replacement for 'import numpy as np' if you only need basic maths.

from numpy import nanmin as min
from numpy import nanmax as max
from numpy import nanmean as mean
from numpy import nanmean as average
from numpy import nansum as sum
from numpy import nanprod as prod
from numpy import nancumsum as cumsum
from numpy import nancumprod as cumprod
from numpy import nanvar as var
from numpy import nanstd as std
from numpy import nanmedian as median
from numpy import nanquantile as quantile
from numpy import nanpercentile as percentile
from numpy import subtract, multiply, add, divide
