#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <float.h>

#include "accelproc.h"

void get_timecorr(
    double *t, 
    double *v, 
    unsigned int len, 
    double **tc_x, 
    double **tc_y, 
    unsigned int *tc_len,
    double *binw,
    double maxlag)
{
  
  // timecorrelation/autocorrelation
  // https://www.itl.nist.gov/div898/handbook/eda/section3/eda35c.htm

  if (t == NULL || v == NULL) {
    fprintf(stderr, "\033[31mFATAL ERROR!\033[0m get_timecorr: input cannot be NULL\n");
    exit(1);
  }

  double *dt = diff(t, len);

  double mindt = min(dt, len);
  double maxdt = max(dt, len);
  double bdt = mindt, fac = 0.0005;
  //bdt = (bdt == 0.0) ? (fac*maxdt) : bdt;
  bdt = ((*binw) < 0.0) ? fac*maxdt : (*binw);
  unsigned int nbins = ceil( (t[len-1] - t[0]) / bdt);
  //fprintf(stderr, "LENGTH ALSO HERE %u %f  %f  %f %f %f\n", nbins, t[len-1], t[0], bdt, mindt, maxdt);
  (*tc_len) = nbins;

  if (maxlag < 0.0)
    maxlag = DBL_MAX;

  double *bins = calloc(nbins, sizeof(double));

  // get correlation
  for (unsigned int i = 0; i < len; i++) {
    for (unsigned int j = i+1; j < len; j++) {
      double dt = t[j] - t[i];
      if (dt > maxlag)
        break;
      unsigned int bi = dt/bdt;
      bins[bi] += v[i] * v[j];
    }
  }

  // norm, output
  double maxv = max(bins, nbins);
  (*tc_y) = malloc(nbins*sizeof(double));
  for (unsigned int i = 0; i < nbins; i++) {
    (*tc_y)[i] = bins[i]/maxv;
  }

  // get binx
  (*tc_x) = malloc(nbins*sizeof(double));
  for (unsigned int i = 0; i < nbins; i++) {
    double idx = (double)i;
    (*tc_x)[i] = (idx + 1.0)*bdt;
  }

  // tidy up
  free(bins);
  free(dt);
}
