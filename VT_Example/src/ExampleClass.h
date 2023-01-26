#pragma once
#include <sal.h>
#include "vt/vt.h"

VT_ABSTRACT VT_DECLARE_CLASS(ICanPrint);

VT_DECLARE_METHOD(ICanPrint, print, void, const char*);

VT_DECLARE_CLASS(ExampleBaseClass, ICanPrint);

VT_OVERRIDE_METHOD(ICanPrint, print)
void ExampleBaseClass_print(ExampleBaseClass self, const char* message);

VT_DECLARE_CLASS(ExampleClass, ExampleBaseClass);

VT_OVERRIDE_METHOD(ICanPrint, print)
void ExampleClass_print(ExampleClass self, const char* message);