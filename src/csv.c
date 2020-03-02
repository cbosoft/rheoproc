#include <Python.h>

#include "accelproc.h"

void parse_csv(char **csv_contents, unsigned int len, double ***data, unsigned int *ncols, unsigned int *nrows)
{
  unsigned int _ncols = 1;
  for (unsigned int line_index = 0; line_index < strlen(csv_contents[0]); line_index++)
    if (csv_contents[0][line_index] == ',')
      _ncols ++;
  (*ncols) = _ncols;

  (*data) = malloc(_ncols * sizeof(double*));
  for (unsigned int column_index = 0; column_index < _ncols; column_index++) {
    (*data)[column_index] = malloc(len * sizeof(double));
  }
  (*nrows) = len;


  char *str;
  for (unsigned int row_index = 0; row_index < len; row_index++) {
    str = strtok(csv_contents[row_index], ",");
    (*data)[0][row_index] = atof(str);
    for (unsigned int column_index = 1; column_index < _ncols; column_index++) {
      (*data)[column_index][row_index] = atof(strtok(NULL, ","));
    }
  }
}
