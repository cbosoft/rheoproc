//#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <float.h>

#include "accelproc.h"

#define TRIPS_PER_REV 12.0
#define CLOSE_THRESH 0.001

#define APPROX_EQUAL(A, B, T) ((A < (B+T)) && (A > (B-T)))


static PyObject *accelproc_parse_csv(PyObject *self, PyObject *args)
{
  PyObject *pylist_lines;

  if (self == NULL) {}

  if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &pylist_lines))
    return NULL;

  unsigned int len = PyList_Size(pylist_lines);
  char **csv_contents = malloc(len * sizeof(char*));

  for (unsigned int i = 0; i < len; i++) {
    PyObject *item = PyList_GetItem(pylist_lines, i);
    const char *item_str = PyUnicode_AsUTF8(item);
    csv_contents[i] = malloc((strlen(item_str)+1) * sizeof(char));
    strcpy(csv_contents[i], item_str);
  }

  double **data;
  unsigned int ncols, nrows;

  parse_csv(csv_contents, len, &data, &ncols, &nrows);

  PyObject *pylist_data = PyList_New(ncols);

  for (unsigned int ci = 0; ci < ncols; ci++) {
    PyObject *pylist_column = PyList_New(nrows);
    for (unsigned int ri = 0; ri < nrows; ri++) {
      PyList_SetItem(pylist_column, ri, PyFloat_FromDouble(data[ci][ri]));
    }
    PyList_SetItem(pylist_data, ci, pylist_column);
  }

  return pylist_data;
}




static PyObject *accelproc_clean_optenc_events(PyObject *self, PyObject *args)
{
  PyObject *pylist_events;

  if (self == NULL) {}

  if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &pylist_events))
    return NULL;

  unsigned int nevents = PyList_Size(pylist_events);

  double *events = malloc(nevents*sizeof(double));
  for (unsigned int i = 0; i < nevents; i++) {
    PyObject *value = PyList_GetItem(pylist_events, i);
    // TODO: error checking
    events[i] = PyFloat_AsDouble(value);
  }

  double *clean_events;
  unsigned int nclean;

  opt_reject(events, nevents, &clean_events, &nclean);
  free(events);

  PyObject *pylist_clean = PyList_New(nclean);
  for (unsigned int i = 0; i < nclean; i++) {
    PyList_SetItem(pylist_clean, i, PyFloat_FromDouble(clean_events[i]));
  }

  free(clean_events);

  return pylist_clean;
}




static PyObject *accelproc_speed_from_optenc_events(PyObject *self, PyObject *args)
{
  PyObject *pylist_events;

  if (self == NULL){}

  if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &pylist_events))
    return NULL;

  unsigned int nevents = PyList_Size(pylist_events);

  double *events = malloc(nevents*sizeof(double));
  for (unsigned int i = 0; i < nevents; i++) {
    PyObject *value = PyList_GetItem(pylist_events, i);
    // TODO: error checking
    events[i] = PyFloat_AsDouble(value);
  }

  double *speed;
  unsigned int nspeed;

  opt_calc_speed(events, nevents, &speed, &nspeed);
  free(events);

  PyObject *pylist_speed = PyList_New(nspeed);
  for (unsigned int i = 0; i < nspeed; i++) {
    PyList_SetItem(pylist_speed, i, PyFloat_FromDouble(speed[i]));
  }

  free(speed);

  return pylist_speed;
}




static PyObject *accelproc_filter_loadcell(PyObject *self, PyObject *args)
{
  // given data: a list of loadcell values, strip any that are "outliers"

  PyObject *pylist_loadcell;
  unsigned int same_thresh = 100;

  if (self == NULL) {}

  if (!PyArg_ParseTuple(args, "O!I", &PyList_Type, &pylist_loadcell, &same_thresh))
    return NULL;

  unsigned int len = PyList_Size(pylist_loadcell);
  //const double gain_limit = 1e5;
  int prev_same_p = 0;
  unsigned int same_count = 0;

  double prev = PyFloat_AsDouble(PyList_GetItem(pylist_loadcell, 0));
  //double lastgood = prev;

  for (unsigned int cur_index = 1; cur_index < len; cur_index++) {
    double cur = PyFloat_AsDouble(PyList_GetItem(pylist_loadcell, cur_index));
    
    // if ( (cur > (lastgood + gain_limit)) || (cur < (lastgood - gain_limit)) ) {
    //   //PyList_SetItem(pylist_loadcell, cur_index, PyFloat_FromDouble(lastgood));
    //   Py_INCREF(Py_None);
    //   PyList_SetItem(pylist_loadcell, cur_index, Py_None);
    // }
    // else 
    if (cur == prev) {
      // this value is the same as before

      if (!prev_same_p) {
        prev_same_p = 1;
      }

      same_count ++;

    }
    else {
      // this value is different...

      if (prev_same_p) {

        // was there a chain of same-values longer than the thresh?
        if (same_count > same_thresh) {
          for (unsigned int j = cur_index - same_count - 1; j < cur_index; j++) {
            //Py_INCREF(Py_None);
            PyList_SetItem(pylist_loadcell, j, PyFloat_FromDouble(NAN));
            //PyList_SetItem(pylist_loadcell, j, PyFloat_FromDouble(lastgood));
          }
        }
        // else {
        //   lastgood = cur;
        // }

        prev_same_p = 0;
        same_count = 0;

      }
    }

    prev = cur;

  }

  
  Py_RETURN_NONE;
}




PyObject *accelproc_tcorr(PyObject *self, PyObject *args)
{
  PyObject *pylist_t, *pylist_v;
  double binw = 0.0, max_lag = 0.0, width_factor = 0.0;

  if (self == NULL) {}

  if (!PyArg_ParseTuple(args, "O!O!ddd",
        &PyList_Type, &pylist_t, 
        &PyList_Type, &pylist_v, 
        &binw, &max_lag, &width_factor))
    return NULL;

  unsigned int len = PyList_Size(pylist_t), nbins;
  double 
    *t = malloc(len*sizeof(double)), 
    *v = malloc(len*sizeof(double)), 
    *dt = NULL, 
    *corr = NULL;

  for (unsigned int i = 0; i < len; i++) {
    t[i] = PyFloat_AsDouble(PyList_GetItem(pylist_t, i));
    v[i] = PyFloat_AsDouble(PyList_GetItem(pylist_v, i));
  }

  get_timecorr(t, v, len, &dt, &corr, &nbins, &binw, max_lag, width_factor);

  PyObject *pylist_dt, *pylist_corr, *pyint_nbins, *rv;

  pylist_dt = PyList_New(nbins);
  pylist_corr = PyList_New(nbins);
  pyint_nbins = PyLong_FromLong((long)nbins);
  PyObject *pyfloat_binw = PyFloat_FromDouble(binw);

  for (unsigned int i = 0; i < nbins; i++) {
    PyList_SetItem(pylist_dt, i, PyFloat_FromDouble(dt[i]));
    PyList_SetItem(pylist_corr, i, PyFloat_FromDouble(corr[i]));
  }

  rv = PyTuple_New(4);
  PyTuple_SetItem(rv, 0, pylist_dt);
  PyTuple_SetItem(rv, 1, pylist_corr);
  PyTuple_SetItem(rv, 2, pyint_nbins);
  PyTuple_SetItem(rv, 3, pyfloat_binw);

  return rv;
}




PyObject *accelproc_peak_detect(PyObject *self, PyObject *args)
{
  PyObject *pylist_signal, *pylist_time;
  int negative_peaks_p = 0;
  double threshold = 0.0;

  if (self == NULL) {}

  if (!PyArg_ParseTuple(args, "O!O!dp", 
        &PyList_Type, &pylist_time, 
        &PyList_Type, &pylist_signal, 
        &threshold, &negative_peaks_p))
    return NULL;

  double *sig = NULL, *time = NULL, *peaks = NULL;
  size_t len, npeaks, *peak_indices = NULL;

  len = PyList_Size(pylist_signal);

  sig = malloc(len*sizeof(double));
  time = malloc(len*sizeof(double));
  for (unsigned int i = 0; i < len; i++) {
    sig[i] = PyFloat_AsDouble(PyList_GetItem(pylist_signal, i));
    time[i] = PyFloat_AsDouble(PyList_GetItem(pylist_time, i));
  }

  peakdet(sig, len, threshold, &peaks, &peak_indices, &npeaks, negative_peaks_p);

  double *peaktimes = malloc(npeaks*sizeof(double));
  for (size_t i = 0; i < npeaks; i++) {
    size_t j = peak_indices[i];
    peaktimes[i] = time[j];
  }

  PyObject *rv = PyTuple_New(2);
  PyObject *pylist_peaks, *pylist_peaktimes;

  pylist_peaks = PyList_New(npeaks);
  pylist_peaktimes = PyList_New(npeaks);

  for (unsigned int i = 0; i < npeaks; i++) {
    PyList_SetItem(pylist_peaks, i, PyFloat_FromDouble(peaks[i]));
    PyList_SetItem(pylist_peaktimes, i, PyFloat_FromDouble(peaktimes[i]));
  }

  PyTuple_SetItem(rv, 0, pylist_peaktimes);
  PyTuple_SetItem(rv, 1, pylist_peaks);

  free(sig);
  free(time);
  free(peaks);
  free(peaktimes);

  return rv;
}









static PyMethodDef accelproc_methods[] = {
    {"speed_from_optenc_events",  accelproc_speed_from_optenc_events, METH_VARARGS, "Convert a list of N optical encoder events to a list of N speeds. Expects events to be clean, errors and misfires are NOT removed."},
    {"clean_optenc_events", accelproc_clean_optenc_events, METH_VARARGS, "Clean a list of optenc events of mis-fires."},
    {"parse_csv", accelproc_parse_csv, METH_VARARGS, "Parse CSV contents to list of columns of floats."},
    {"filter_loadcell", accelproc_filter_loadcell, METH_VARARGS, "filter out non-sensible values from loadcell"},
    {"peak_detect", accelproc_peak_detect, METH_VARARGS, "find peaks and associated times for a timeseries"},
    {"tcorr", accelproc_tcorr, METH_VARARGS, "get time correlation of data"},
    {NULL, NULL, 0, NULL}
};




static struct PyModuleDef accelproc_module = {
    PyModuleDef_HEAD_INIT,
    "accelproc",   /* name of module */
    "Accelerated data processing for /the device/.", /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    accelproc_methods,
    NULL,
    NULL,
    NULL,
    NULL
};




PyMODINIT_FUNC PyInit_accelproc(void)
{
  PyObject *m = PyModule_Create(&accelproc_module);
  return m;
}
