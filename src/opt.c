#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "vector.h"

#define TRIPS_PER_REV 12.0
#define CLOSE_THRESH 0.001

#define APPROX_EQUAL(A, B, T) ((A < (B+T)) && (A > (B-T)))


/*
  opt_reject: reject optical encoder events that have been double registered.
*/
void opt_reject(double *raw_events, unsigned int nevents, double **events, unsigned int *actual_nevents)
{
  double this, prev;

  // allocate the full range of memory to hold the clean results, which will be
  // at most the same size, but probably smaller.
  double *doubles_rejected = calloc(nevents, sizeof(double));
  (*events) = calloc(nevents, sizeof(double));

  // Skip events == 0, as this will muck up calculations later
  int start = 0;
  while (raw_events[start] == 0.0) start++;
  
  (*actual_nevents) = 1;
  prev = raw_events[start];
  doubles_rejected[0] = prev;
  for (unsigned int event_index = start; event_index < nevents; event_index++) {
    this = raw_events[event_index];
    
    if (!APPROX_EQUAL(this, prev, CLOSE_THRESH))
      doubles_rejected[(*actual_nevents)++] = this;
    
    prev = this;
  }
  doubles_rejected = realloc( doubles_rejected, (*actual_nevents)*sizeof(double));
  (*events) = copy(doubles_rejected, (*actual_nevents));
  free(doubles_rejected);
}




/*
  opt_calc_speed - calculate speed (in ROT/S) from a list of optical encode events.
*/
int opt_calc_speed(double *events, unsigned int nevents, double **speed, unsigned int *len)
{

  double revs_per_trip = 1.0 / TRIPS_PER_REV;
  // MUST HAVE LAG OF AT LEAST 2
  unsigned int lag = 2; //TRIPS_PER_REV * 1;
  (*speed) = zeros(nevents);
  (*len) = nevents;
  double dr, dt;

  for (unsigned int event_number = 1; event_number < nevents; event_number++) {

    if (event_number >= lag) {
      dr = revs_per_trip * lag;
      dt = events[event_number] - events[event_number - lag];
    }
    else {
      dr = revs_per_trip * (event_number);
      dt = events[event_number] - events[0];
    }
    
    (*speed)[event_number] = dr / dt;

  }

  // plaster over the initial reading
  (*speed)[0] = (*speed)[1];

  return 0;
}
