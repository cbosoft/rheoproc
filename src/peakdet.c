#define _POSIX_C_SOURCE 200809L
#include <limits.h>
#include <float.h>

#include "accelproc.h"
#include "vector.h"




size_t get_uncounted_limit(double *x, size_t len, size_t *counted, int negative_peaks, double threshold)
{
  double lim = negative_peaks ? DBL_MAX : DBL_MIN;
  double dircoef = negative_peaks ? -1.0 : 1.0;
  size_t limat = 0;

  for (size_t i = 0 ; i < len ; i++) {
    if (counted[i])
      continue;

    if (dircoef*x[i] > dircoef*lim && dircoef*x[i] > dircoef*threshold) {
      lim = x[i];
      limat = i;
    }
  }
  
  return limat;
}




void peakdet(double* signal, 
    size_t len, 
    double threshold, 
    double **peaks, 
    size_t **peak_indices, 
    size_t *npeaks, 
    int negative_peaks) 
{

  // get minimum in points sequence
  // this is the start of a peak
  // step back until points voltage goes beyond thresh
  // this is the end of the peak

  double  *_peaks = calloc(len, sizeof(double)); // more than enough space for all peaks
  size_t  *_indcs = calloc(len, sizeof(size_t));
  size_t *counted = calloc(len, sizeof(size_t));

  size_t c = 0;
  double dircoef = negative_peaks ? -1.0 : 1.0;
  size_t mindex;

  do {
    mindex = get_uncounted_limit(signal, len, counted, negative_peaks, threshold);

    for (size_t i = mindex; i > 0; i--) {
      counted[i] = 1;
      if (dircoef*signal[i] < dircoef*threshold)
        break;
    }
    for (size_t i = mindex; i < len; i++) {
      counted[i] = 1;
      if (dircoef*signal[i] < dircoef*threshold)
        break;
    }

    _peaks[c] = signal[mindex];
    _indcs[c] = mindex;
    c ++;
  } while (mindex > 0);


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

}
