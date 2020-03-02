#include <stdlib.h>

// simplified from https://github.com/cbosoft/cvec

// creating new vectors
double *linspace(double from, double to, size_t len);
double *logspace(double from, double to, size_t len);
double *zeros(size_t len);
double *ones(size_t len);
double *copy(double *source, size_t len);

// simple vector manipulation

double add(double v1, double v2);
double subtract(double v1, double v2);
double multiply(double v1, double v2);
double divide(double v1, double v2);
double pow(double v1, double v2);
double *apply(double* in, size_t len, double (*f)(double));
double *apply2(double* in1, double *in2, size_t len, double (*f)(double, double));
double *slice(double *source, size_t len, size_t start, size_t stop, size_t skip);
double *cat(double *source, size_t len, double *add, size_t addlen);
double *diff(double *x, size_t len);
double *rearrange(double *x, size_t len, size_t *arrangement, size_t alen);
void set_constant(double *x, size_t len, double v);

// properties of vector

double get_fit_sumse(double *x, double *y, size_t len, double *coefs, size_t ncoefs);
double *polyfit(double *x, double *y, size_t len, size_t degree);
double *linearfit(double *x, double *y, size_t len);
double interpolate(double *x, double *y, size_t len, double ix);
double min(double *x, size_t len);
double max(double *x, size_t len);

// stats
double average(double * in, size_t len);
double mean(double * in, size_t len);
double median(double * in, size_t len);
double sum(double * in, size_t len);
double prod(double * in, size_t len);


// jobs
void set_n_jobs(size_t njobs);
