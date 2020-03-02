#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <errno.h>
#include <string.h>
#include <math.h>
#include <pthread.h>
#include <float.h>

#include "vector.h"

#define MESGLEN 100

void ferr(int showerrno, const char *source, const char* fmt, ...)
{
  char mesg[MESGLEN] = {0};

  va_list ap;

  va_start(ap, fmt);
  vsnprintf(mesg, MESGLEN-1, fmt, ap);
  va_end(ap);

  time_t rt;
  struct tm *info;
  char timestr[MESGLEN] = {0};

  time(&rt);
  info = localtime(&rt);
  strftime(timestr, MESGLEN-1, "%x %X", info);

  fprintf(stderr, "  (%s) FATAL ERROR! in %s: %s", timestr, source, mesg);
  if (showerrno)
    fprintf(stderr, " (%d) %s", errno, strerror(errno));
  fprintf(stderr, "\n");

  exit(1);
}

static size_t __njobs;

void set_n_jobs(size_t njobs)
{
  __njobs = njobs;
}



double *linspace(double from, double to, size_t len)
{
  double *rv = malloc(len*sizeof(double));
  double tof = (double)to;
  double fromf = (double)from;
  double stepf = ( tof - fromf ) / ( (double)(len - 1) );

  for (size_t i = 0; i < len; i++) {
    double iif = (double)i;
    rv[i] = (double)round( (iif * stepf) + fromf );
  }

  return rv;
}




double *logspace(double from, double to, size_t len)
{
  double lfrom = log(from), lto = log(to);
  double *rv = linspace(lfrom, lto, len);

  for (size_t i  = 0; i < len; i++) {
    rv[i] = pow(10.0, rv[i]);
  }

  return rv;
}




double * apply( double* in, size_t len, double (*f)(double))
{
  double *rv = malloc(len*sizeof(double));

  for (size_t i = 0; i < len; i++){
    rv[i] = f(in[i]);
  }
  return rv;
}



double add(double v1, double v2) { return v1 + v2; }
double subtract(double v1, double v2) { return v1 - v2; }
double multiply(double v1, double v2) { return v1 * v2; }
double divide(double v1, double v2) { return v1 / v2; }




double *apply2( double *in1, double *in2, size_t len, double (*f)(double, double))
{
  double *rv = malloc(len*sizeof(double));

  for (size_t i = 0; i < len; i++){
    rv[i] = f(in1[i], in2[i]);
  }
  return rv;
}




double *zeros(size_t len)
{
  double *rv = malloc(len*sizeof(double));

  for (size_t i = 0; i < len; i++){
    rv[i] = 0.0;
  }
  return rv;
}




double *ones(size_t len)
{
  double *rv = malloc(len*sizeof(double));

  for (size_t i = 0; i < len; i++){
    rv[i] = 1.0;
  }
  return rv;
}



double *copy(double *source, size_t len)
{
  double *rv = malloc(sizeof(double)*len);

  for(size_t i = 0; i < len; i++) {
    rv[i] = source[i];
  }
  return rv;
}



double *cat( double *source, size_t len, double *add, size_t addlen)
{
  double *rv = malloc(sizeof(double)*(len+addlen));

  for(size_t i = 0; i < len; i++) {
    rv[i] = source[i];
  }

  for(size_t i = len; i < len+addlen; i++) {
    rv[i] = add[i-len];
  }

  return rv;
}




double *diff(double* x, size_t len)
{
  double *rv = malloc(sizeof(double)*(len-1));
  size_t i, j;

  for (i=0; i < (len-1); i++) {
    j = i+1;
    rv[i] = x[j] - x[i];
  }

  return rv;
}



double *slice( double *x, size_t len, size_t start, size_t stop, size_t skip)
{
  if (stop > len) 
    ferr(0, "slice", "stop > len");
  
  if (skip == 0)
    skip = 1;

  size_t olen = (stop - start) / skip;
  double *rv = malloc(sizeof(double)*olen);
  for (size_t i = start, j = 0; i < stop; i += skip, j++) {
    rv[j] = x[i];
  }
  return rv;
}




double get_fit_sumse(
    double *x, 
    double *y, 
    size_t len, 
    double *coefs, 
    size_t ncoefs)
{
  double calc_se(double o, double g) { 
    return pow(o - g, 2.0); 
  }
  double calcfit(double xi) { 
    double rv = 0.0; 
    for (size_t i = 0; i < ncoefs; i++) 
      rv += coefs[i] * pow(xi, (double)i); 
    return rv; 
  }
  double *t = apply(x, len, &calcfit);
  double *se = apply2(y, t, len, &calc_se);
  double sumse = sum(se, len);
  free(t);
  free(se);
  return sumse;
}




double *polyfit(
    double *X, 
    double *Y, 
    size_t len, 
    size_t degree)
{
  // https://github.com/natedomin/polyfit
  size_t maxdeg = 5;
  
  double *B = calloc(maxdeg+1, sizeof(double));
  double *P = calloc(((maxdeg+1)*2)+1, sizeof(double));
  double *A = calloc((maxdeg+1)*2*(maxdeg+1), sizeof(double));

  double x, y, powx;

  size_t i, j, k;

  if (len <= degree || degree > maxdeg)
      return NULL;

  // Identify the column vector
  for (i = 0; i < len; i++) {
    x    = X[i];
    y    = Y[i];
    powx = 1.0;

    for (j = 0; j < (degree + 1); j++) {
      B[j] = B[j] + (y * powx);
      powx  = powx * x;
    }
  }

  // Initialize the PowX array
  P[0] = len;

  // Compute the sum of the Powers of X
  for (i = 0; i < len; i++) {
    x    = X[i];
    powx = X[i];

    for (j = 1; j < ((2 * (degree + 1)) + 1); j++) {
      P[j] = P[j] + powx;
      powx  = powx * x;
    }
  }

  // Initialize the reduction matrix
  //
  for (i = 0; i < (degree + 1); i++) {
    for (j = 0; j < (degree + 1); j++) {
      A[(i * (2 * (degree + 1))) + j] = P[i+j];
    }

    A[(i*(2 * (degree + 1))) + (i + (degree + 1))] = 1;
  }

  // Move the Identity matrix portion of the redux matrix
  // to the left side (find the inverse of the left side
  // of the redux matrix
  for (i = 0; i < (degree + 1); i++) {
    x = A[(i * (2 * (degree + 1))) + i];
    if (x != 0) {
      for (k = 0; k < (2 * (degree + 1)); k++) {
        A[(i * (2 * (degree + 1))) + k] = A[(i * (2 * (degree + 1))) + k] / x;
      }

      for (j = 0; j < (degree + 1); j++) {
        if ((j - i) != 0) {
          y = A[(j * (2 * (degree + 1))) + i];
          for (k = 0; k < (2 * (degree + 1)); k++) {
            A[(j * (2 * (degree + 1))) + k] = A[(j * (2 * (degree + 1))) + k] - y * A[(i * (2 * (degree + 1))) + k];
          }
        }
      }
    }
    else
    {
        // Cannot work with singular matrices
        return NULL;
    }
  }
  
  double *coefficients = calloc(degree+1, sizeof(double));
  // Calculate and Identify the coefficients
  for (i = 0; i < (degree + 1); i++) {
    for (j = 0; j < (degree + 1); j++) {
      x = 0;
      for (k = 0; k < (degree + 1); k++) {
        x = x + (A[(i * (2 * (degree + 1))) + (k + (degree + 1))] * B[k]);
      }
      coefficients[i] = x;
    }
  }
  free(A);
  free(B);
  free(P);
  return coefficients;
}



double *linearfit(double *x, double *y, size_t len)
{
  double midx = average(x, len);
  double midy = average(y, len);

  double get_size_t(double m) { return midy - m*midx; }

  double get_sumse(
      double *x, 
      double *y, 
      size_t len, 
      double gradient) {
    double size_terrupt = get_size_t(gradient);
    double applyfit(double v) { return size_terrupt+(gradient*v); }
    double *fity = apply(x, len, &applyfit);
    double getse(double y1, double y2) {
      return pow(y1 - y2, 2.0);
    }
    double *se = apply2(y, fity, len, &getse);
    double sumse = sum(se, len);
    free(se);
    free(fity);
    return sumse;
  }

  double change = 0.1, m = 1.0;
  for (size_t i = 0; i < len+100; i++) {
    double err1 = get_sumse(x, y, len, m);
    m += change;
    double err2 = get_sumse(x, y, len, m);
    if (err2 > err1) {
      m -= change;
      change *= -0.8;
    }
    else {
      change *= 1.2;
    }
  }
  double *coefs = malloc(sizeof(double)*2);
  coefs[0] = get_size_t(m);
  coefs[1] = m;
  return coefs;
}



double interpolate(
    double *x, 
    double *y, 
    size_t len, 
    double ix)
{

  size_t p1 = len, p2 = len;
  if (ix < x[0]) {
    p1 = 0;
    p2 = len*0.1;

    if (p1 == p2) p2 ++;
  }
  else if (ix > x[len-1]) {
    p1 = len-1;
    p2 = len*0.9;

    if (p1 == p2) p2 --;
  }
  else {
    // find surrounding xs
    for (size_t i = 0, j = 1; j < len; i++, j++) {
      if (x[i] == ix)
        return y[i];
      if (x[j] == ix)
        return y[j];
      if (x[i] < ix && x[j] > ix) {
        p1 = i;
        p2 = j;
      }
    }
    if (p1 == p2) 
      ferr(0, "interpolate", "could not find points surrounding ix");
  }

  double m_num = (y[p1] - y[p2]);
  double m_den = (x[p1] - x[p2]);

  if (m_den == 0.0)
    ferr(0, "interpolate", "inf result!");

  if (isnan(m_num) || isnan(m_den)) 
    ferr(0, "interpolate", "NaN result!");
  
  double m = m_num / m_den;
  double yi = (m * (ix - x[p2])) + y[p2];
  return yi;
}



double *rearrange(
    double *x, 
    size_t len,
    size_t *arrangement, 
    size_t alen)
{
  double *rv = ones(alen);

  for (size_t i = 0; i < alen; i++) {
    size_t j = arrangement[i];

    if (j >= len)
      ferr(0,
          "rearrange", 
          "new arrangement index outside of vector length (%u > %u)", 
          j, len);

    rv[i] = x[j];
  }

  return rv;
}


typedef struct sc_td_t {
  size_t from;
  size_t to;
  double *x;
  double val;
} sc_td_t;

void *setconstthread(void *vtd) 
{
  sc_td_t *td = (sc_td_t*)vtd;
  for (size_t i = td->from; i < td->to; i++) td->x[i] = td->val;
  return NULL;
}

void set_constant(double *x, size_t len, double v)
{
  pthread_t threads[__njobs];
  sc_td_t data[__njobs];
  size_t each = len/__njobs;

  for (size_t i = 0; i < __njobs; i++) {
    data[i].from = i*each;
    data[i].to = (i == __njobs-1) ? (len) : ((i+1)*each);
    data[i].x = x;
    data[i].val = v;

    pthread_create(&threads[i], NULL, setconstthread, &data[i]);
  }

  for (size_t i = 0; i < __njobs; i++) {
    pthread_join(threads[i], NULL);
  }
}




double average(double * in, size_t len)
{
  return mean(in, len);
}




double mean(double * in, size_t len)
{
  double s = sum(in, len);
  return s / ((double)len);
}




// double median(double * in, size_t len)
// {
//   size_t midp = (len%2==0)?(len/2):((len+1)/2);
//   double *sorted;
//   sort(in, len, NULL, &sorted);
//   double rv = sorted[midp];
//   free(sorted);
//   return rv;
// }



double sumrange(double *x, size_t from, size_t to)
{
  double sum = 0.0;
  for (size_t i = from; i < to; i++)
    sum += x[i];
  return sum;
}

typedef struct sum_td_t {
  size_t from;
  size_t to;
  double *x;
  double *res;
  size_t id;
} sum_td_t;

void *sumthread(void *vtd)
{
  sum_td_t *td = (sum_td_t *)vtd;
  td->res[td->id] += sumrange(td->x, td->from, td->to);
  return NULL;
}

double sum(double * in, size_t len)
{
  double *sub_summed;
  size_t sub_len;

  if (len < 10000) {

    sub_summed = in;
    sub_len = len;

  }
  else {

    sum_td_t data[__njobs];
    pthread_t threads[__njobs];
    size_t each = len/__njobs;

    sub_summed = calloc(__njobs, sizeof(double));
    sub_len = __njobs;

    for (size_t i = 0; i < __njobs; i++) {
      data[i].from = i*each;
      data[i].to = (i == __njobs-1) ? (len) : ((i+1)*each);
      data[i].x = in;
      data[i].res = sub_summed;
      data[i].id = i;

      pthread_create(&threads[i], NULL, sumthread, &data[i]);
    }

    for (size_t i = 0; i < __njobs; i++) {
      pthread_join(threads[i], NULL);
    }
  }

  double sum = sumrange(sub_summed, 0, sub_len);

  if (len >= 10000)
    free(sub_summed);

  return sum;
}




double prod(double * in, size_t len)
{
  double prod = 1.0;
  for (size_t i = 0; i < len; i++) {
    prod *= in[i];
  }
  return prod;
}


double min(double *x, size_t len)
{
  double min = DBL_MAX;
  for (unsigned int i = 0; i < len; i++) {
    if (x[i] < min)
      min = x[i];
  }
  return min;
}


double max(double *x, size_t len)
{
  double max = DBL_MIN;
  for (unsigned int i = 0; i < len; i++) {
    if (x[i] < max)
      max = x[i];
  }
  return max;
}
