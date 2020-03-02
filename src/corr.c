#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <float.h>

#include "accelproc.h"
#include "vector.h"
#include "err.h"

void get_timecorr(
    double *t, 
    double *v, 
    unsigned int len, 
    double **tc_x, 
    double **tc_y, 
    unsigned int *tc_len,
    double *binw,
    double maxlag,
    double fac)
{
  
  // timecorrelation/autocorrelation
  // https://www.itl.nist.gov/div898/handbook/eda/section3/eda35c.htm

  // input guaranteed not to be NULL earlier, but lets check anyway
  if (t == NULL || v == NULL) {
    ferr(0, "get_timecorr", "input cannot be NULL (ptr t=%d, ptr v=%d)", t, v);
  }

  double *dt = diff(t, len);

  // double mindt = min(dt, len);
  double maxdt = max(dt, len);
  //bdt = (bdt == 0.0) ? (fac*maxdt) : bdt;
  if ((*binw) < 0.0) (*binw) = fac*maxdt;
  size_t nbins = ceil( (t[len-1] - t[0]) / (*binw));
  //fprintf(stderr, "LENGTH ALSO HERE %u %f  %f  %f %f %f\n", nbins, t[len-1], t[0], bdt, mindt, maxdt);

  if (maxlag < 0.0)
    maxlag = DBL_MAX;

  double *bins = calloc(nbins, sizeof(double));
  double tspan = t[len-1] - t[0];

  // get correlation
  for (size_t i = 0; i < len; i++) {
    for (size_t j = 0; j < len; j++) {
      // wrap to front
      size_t k = (i+j) % len;
      size_t wrapped = (i+j) / len;
      double dt = t[k] - t[i];
      if (wrapped) 
        dt += tspan;

      if (dt > maxlag)
        break;
      size_t bi = dt/(*binw);
      bins[bi] += v[i] * v[j];
    }
  }

  nbins = maxlag/(*binw);
  (*tc_len) = nbins;

  // norm, output
  double maxv = max(bins, nbins);
  (*tc_y) = malloc(nbins*sizeof(double));
  for (size_t i = 0; i < nbins; i++) {
    (*tc_y)[i] = bins[i]/maxv;
  }

  // get binx
  (*tc_x) = malloc(nbins*sizeof(double));
  for (size_t i = 0; i < nbins; i++) {
    double idx = (double)i;
    (*tc_x)[i] = (idx + 1.0)*(*binw);
  }

  // tidy up
  free(bins);
  free(dt);
}
