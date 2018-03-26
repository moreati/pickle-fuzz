#include <stdio.h>
#include <Python.h>

int
main(int argc, char *argv[])
{
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);

    Py_NoSiteFlag = 1;
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }
    Py_SetProgramName(program);  /* optional but recommended */

    Py_InitializeEx(0);
#ifdef __AFL_HAVE_MANUAL_CONTROL
    __AFL_INIT();
#endif

    FILE *f = fopen(argv[1], "rb");
    int closeit = 1;

    if(PyRun_AnyFileEx(f, argv[1], closeit) == -1) {
        printf("fail");
    }

    if (Py_FinalizeEx() < 0) {
        exit(120);
    }
    PyMem_RawFree(program);
    return 0;
}
