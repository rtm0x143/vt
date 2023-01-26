# Virtual table
That repo is just a try to do small and funny trick to provive some explicit OOP consepts to developing in C.
There just a header file with macro defenitions and python script to analyse them in user's code.
### Macros
All functionality providede threw macros from vt.h.
Usage of that macros could be found in their annotations.

### vtc.py
Macros can't standalone implement virtual table, so berofe building your project you should run CLI tool __vtc.py__, whitch wil analyse your code and generate __vc_impl.c__ file, whitch should be included in your build.

> **The implementation of code parser seem to be very buggy and unstable** 
>
>  _the idea is just to show avaliability, not implement OOP framework for C programming_
