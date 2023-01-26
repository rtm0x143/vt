#pragma once
#include <assert.h>
#include <malloc.h>

/*
*
* TODO: Documentation
*
*/

// amount of classes, implementing methods, ect limited by 2^16
typedef unsigned short vtsize_t;

typedef struct { vtsize_t decl_id, mth_offset; } vtid_t;

typedef void* method_ptr;

typedef const struct vtrow_t* vtrow_ptr;
struct vtrow_t {
	const vtrow_ptr* decls;
	const method_ptr* impls;
	const vtsize_t decl_width, decls_count, decl_id;
};

// Declares class with 'class_name'; in variable arguments you can specify base classes as list of implementing interfaces
#define VT_DECLARE_CLASS(class_name, ...)		\
	extern const size_t vt_##class_name##_size;	\
	extern const vtrow_ptr vtrow_##class_name;	\
	typedef struct _##class_name* class_name

// Used before 'VT_DECLARE_CLASS' to allow not implemented methods
#define VT_ABSTRACT //

// Begins implementation of your base class
#define VT_IMPLEMENT_CLASS_BEG(class_name) struct _##class_name { const vtrow_ptr __vtrow; 

// Begins implementation of your class that direcly inherits 'base_class'
// 'base_class' should be already implemented 
// 'alias' used to "put" fields of 'base_class' in a field
#define VT_IMPLEMENT_CLASS_BEG_INHERIT(class_name, base_class, /*optional*/alias) \
	struct _##class_name { struct _##base_class alias;

// Ends implementations of your class
#define VT_IMPLEMENT_CLASS_END(class_name) }; const size_t vt_##class_name##_size = sizeof(struct _##class_name);

#define VT_DECLARE_METHOD_NOARGS(class_name, method_name, ret_t)		\
	extern const vtid_t vtid_##class_name##_##method_name;				\
	typedef ret_t(*class_name##_##method_name##_t)(class_name self)

#define VT_DECLARE_METHOD(class_name, method_name, ret_t, /*arguments declaration*/...)	\
	extern const vtid_t vtid_##class_name##_##method_name;								\
	typedef ret_t(*class_name##_##method_name##_t)(class_name self, __VA_ARGS__)				

// Should be used as function annotation 
// 'class_name' is an "interface" name, 'method_name' is name of method to override
// The target function will be used as implementation for concrete class
// The very first argument of function signature should be named as 'self' and typed using concrete class type name
// 
// Example : 
//		VT_OVERRIDE_METHOD(ExampleBaseClass, qwerty)
//		void foo(ExampleClass /* No macros here! */ self, int whatever);
#define VT_OVERRIDE_METHOD(class_name, method_name)

typedef struct vt_instance_t {
	vtrow_ptr vtrow;
}*vt_instance_ptr;

_declspec(thread) static vt_instance_ptr vt_tmpinst;

// Allocates new instance of class 'class_name'
// So that instance should be finalised using 'free' function
// Return could be NULL, if allocation failed 
#define VT_CREATE_INST(class_name)  ( vt_tmpinst = (vt_instance_ptr)malloc(vt_##class_name##_size), vt_tmpinst ? vt_tmpinst->vtrow = vtrow_##class_name : NULL, (class_name)vt_tmpinst )

__forceinline method_ptr vtrow_getmth(vtrow_ptr vtrow, vtid_t mthid) {
	const method_ptr* ptr = vtrow->impls + mthid.mth_offset;
	for (unsigned char i = 0; i < vtrow->decls_count; ++i)
	{
		if (vtrow->decls[i]->decl_id == mthid.decl_id) {
			assert(*ptr && "Requested method implementation was null, seems like this class is abstract or didn't implement entire interface.");
			return *ptr;
		}
		ptr += vtrow->decls[i]->decl_width;
	}
	assert(NULL && "Requested method implementation were not fount, seems like that doesn't implement requested interface");
	return NULL;
}

#define vt_getmth(inst, class_name, method_name) ((class_name##_##method_name##_t)vtrow_getmth(((vt_instance_ptr)inst)->vtrow, vtid_##class_name##_##method_name))