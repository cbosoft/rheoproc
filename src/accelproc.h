#pragma once
#define _POSIX_C_SOURCE 200809L
#include <Python.h>

// opt.c
void opt_reject(double *raw_events, unsigned int nevents, double **events, unsigned int *actual_nevents);
int opt_calc_speed(double *events, unsigned int nevents, double **speed, unsigned int *len);

// csv.c
void parse_csv(char **csv_contents, unsigned int len, double ***data, unsigned int *ncols, unsigned int *nrows);

// peakdet.c
void peakdet(double* signal, size_t len, double threshold, double **peaks, size_t **peak_indices, size_t *npeaks, int negative_peaks);

// corr.c
void get_timecorr(double *t, double *v, unsigned int len, double **tc_x, double **tc_y, unsigned int *tc_len, double *binw, double maxlag, double fac);

// vim: ft=c
