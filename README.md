# rheoproc - Rheometer data processing

Processing library for my [rheometer](https://github.com/cbosoft/rheometer). Uses the power of libraries like `numpy` and
`scipy` to tease physical measurements from my raw data - stored efficiently in tar archives and indexed in an SQLite
database. The most time consuming parts (encoder processing and peak detection) are written in `c`, leveraging the awesome and
simple `python`-`c` api.

Also features a remote processing server which can be run headless and a client can simply request the desired logs to be
processed and returned. Very handy when I was writing my thesis on my laptop away from my uni computer (thanks COVID) and
didn't want my legs to burn under the load.