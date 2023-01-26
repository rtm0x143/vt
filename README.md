# Virtual table
That repo is just a try to do small and funny trick to provide some explicit OOP concepts to developing in C.
There just a header file with macro definitions and python script to analyse them in user's code.
### Macros
All functionality provided threw macros from vt.h.
Usage of that macros could be found in their annotations.

### vtc.py
Macros can't standalone implement virtual table, so before building your project you should run CLI tool __vtc.py__, which wil analyse your code and generate __vc_impl.c__ file, whitch should be included in your build.

> **The implementation of code parser seem to be very buggy and unstable** 
>
>  _>  _the idea is just to show availability, not implement OOP framework for C programming_

### Example 
You can find example in VT_Example folder, it is very small Visual Studio solution showing how VT could be used. 
