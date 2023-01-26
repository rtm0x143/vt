#include "vt/vt.h"
#include "ExampleClass.h"

void calls_print(ICanPrint obj) {
	vt_getmth(obj, ICanPrint, print)(obj, "Hello, world!\n");
}

int main() {
	ExampleClass cl = VT_CREATE_INST(ExampleClass);
	calls_print((ICanPrint)cl);

	ExampleBaseClass base_cl = VT_CREATE_INST(ExampleBaseClass);
	calls_print((ICanPrint)base_cl);

	return 0;
}