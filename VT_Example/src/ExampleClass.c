#include <malloc.h>
#include "ExampleClass.h"

VT_IMPLEMENT_CLASS_BEG(ExampleBaseClass)
struct {
	char* name;
	int baseField1;
};
VT_IMPLEMENT_CLASS_END(ExampleBaseClass)

VT_IMPLEMENT_CLASS_BEG_INHERIT(ExampleClass, ExampleBaseClass, )
struct {
	double newField;
};
VT_IMPLEMENT_CLASS_END(ExampleClass)

#include <stdio.h>
void ExampleBaseClass_print(ExampleBaseClass self, const char* message) {
	printf("Message from ExampleBaseClass's ICanPrint.print method : \n\t%s", message);
}

void ExampleClass_print(ExampleClass self, const char* message) {
	printf("Message from ExampleClass's ICanPrint.print method : \n\t%s", message);
}