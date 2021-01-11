#define _POSIX_C_SOURCE 200809L
#include <limits.h>
#include <stdio.h>
#include <float.h>

#include "accelproc.h"
#include "vector.h"




int get_next_peak(double *x, size_t len, size_t *counted, double threshold)
{
  // get index of largest uncounted peak
  double peak = DBL_MIN;
  size_t peak_index = -1;

  for (size_t i = 0 ; i < len ; i++) {
    if (counted[i])
      continue;

    if (x[i] > peak && x[i] > threshold) {
      peak = x[i];
      peak_index = i;
    }
  }

  return peak_index;
}




void peakdet(double* signal, 
    size_t len, 
    double threshold, 
    double **peaks, 
    size_t **peak_indices, 
    size_t *npeaks, 
    int mode)
{

  // get minimum in points sequence
  // this is the start of a peak
  // step back until points voltage goes beyond thresh
  // this is the end of the peak

  double  *_peaks = calloc(len, sizeof(double)); // more than enough space for all peaks
  size_t  *_indcs = calloc(len, sizeof(size_t));
  size_t *counted = calloc(len, sizeof(size_t));


  double *signal_directioned = calloc(len, sizeof(double));
  for (size_t i = 0; i < len; i++) {
    double si = signal[i];
    switch (mode) {
      case PEAKDET_MODE_NEGATIVE:
        si = si*-1.0;
        break;
      case PEAKDET_MODE_BOTH:
        si = (si > 0) ? si : -si;
        break;
    }
    signal_directioned[i] = si;
  }

  size_t c = 0;
  for (c = 0; c < len; c++) {
    int peak = get_next_peak(signal_directioned, len, counted, threshold);
    if (peak < 0)
      break;

    // go back from peak, marking off parts of the same peak
    for (size_t i = peak; i > 0; i--) {
      counted[i] = 1;
      if (signal_directioned[i] < threshold)
        break;
    }

    // go forward from peak, marking off parts of the same peak
    for (size_t i = peak; i < len; i++) {
      counted[i] = 1;
      if (signal_directioned[i] < threshold)
        break;
    }

    _peaks[c] = signal[peak];
    _indcs[c] = (size_t)peak;
  };


  if (c == 0) {

    free(_peaks);
    free(_indcs);

    (*peaks) = NULL;
    (*peak_indices) = NULL;
    (*npeaks) = 0;

  }
  else {

    // shrink to actual number of peaks
    _peaks = realloc(_peaks, sizeof(double)*c);
    _indcs = realloc(_indcs, sizeof(double)*c);

    (*peaks) = _peaks;
    (*peak_indices) = _indcs;
    (*npeaks) = c;

  }

  free(signal_directioned);

}
