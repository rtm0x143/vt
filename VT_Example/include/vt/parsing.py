import re
from pathlib import Path
import os
import sys

method_decl_pat = (r"VT_DECLARE_METHOD\s*\(\s*(?P<class_name>[a-zA-Z_]\w*)\s*,\s*"
                   r"(?P<method_name>[a-zA-Z_]\w*)(?:.|\s)*?\)(?:.|\s)*?;")

method_override_pat = (r"VT_OVERRIDE_METHOD\s*\(\s*(?P<class_name>[a-zA-Z_]\w*)\s*,\s*"
                       r"(?P<method_name>[a-zA-Z_]\w*)\s*\)(?:.|\s)*?\s"
                       r"(?P<last_macro_like>[a-zA-Z_]\w*)\s"
                       r"(?P<func_name>[a-zA-Z_]\w*)\s*\((?:.|\s)*?"
                       r"(?P<self_class>[a-zA-Z_]\w*)\s+self(?:(?:.|\s)*?)\)(?:.|\s)*?;")

class_decl_pat = (r"(?P<mods>(?:[a-zA-Z_]\w*\s+)*)VT_DECLARE_CLASS\s*\(\s*"
                  r"(?P<class_name>[a-zA-Z_]\w*)(?:\s*,\s*"
                  r"(?P<base_classes>[a-zA-Z_]\w*(?:\s*,\s*[a-zA-Z_]\w*)*))?\s*\)\s*;")


class ClassDecl:
    def __init__(self, name):
        self.name = name
        self.bases_names: list[str] = []
        self.method_decls: list[str] = []
        self.method_impl: dict[dict[str: str]] = {}     # { decl_name : impl_name }
        self.is_abstract: bool = False

        self.result_decl_impls: list[str] = []
        self.result_interface: list[str] = []           # list of "(class_name)_(method_name)"
        self.result_decl_positions: list[int] = []      # an indices of ClassDecl in general VT


class VTGenerator:
    def __init__(self, dest_path: Path):
        self.classes: list[ClassDecl] = []
        self.file_paths: list[Path] = []
        self.dest_path = dest_path

    @staticmethod
    def raise_name_error(name, src):
        place = src.find(name)
        place = str(src.count("\n", 0, place) + 1) + ":" + str(place - src.rfind("\n", 0, place))
        er = NameError(f"name '{name}' is not defined. Appeared in {place}")
        er.name = name
        raise er

    def find_class_or_none(self, name):
        for cl in self.classes:
            if cl.name == name:
                return cl
        return None

    def find_class_index(self, name):
        for i in range(len(self.classes)):
            if self.classes[i].name == name:
                return i
        raise ValueError(f"{name} - class with that name wasn't found")

    def add_file(self, file_path: Path):
        self.file_paths.append(file_path)
        with open(file_path.__str__(), "r") as file:
            code = file.read()

        for cl in re.finditer(class_decl_pat, code):
            class_decl = ClassDecl(cl.group("class_name"))
            grp = cl.group("base_classes")
            class_decl.bases_names = grp.replace(" ", "").split(",") if grp else []
            class_decl.is_abstract = cl.group("mods").find("VT_ABSTRACT") >= 0
            self.classes.append(class_decl)

        for mth in re.finditer(method_decl_pat, code):
            grp = mth.group('class_name')
            _class: ClassDecl = self.find_class_or_none(grp)
            if not _class:
                VTGenerator.raise_name_error(grp, code)
            _class.method_decls.append(mth.group("method_name"))

        for mth in re.finditer(method_override_pat, code):
            grp = mth.group('class_name')
            base_class: ClassDecl = self.find_class_or_none(grp)
            if not base_class:
                VTGenerator.raise_name_error(grp, code)

            method_name = mth.group("method_name")
            try:
                base_class.method_decls.index(method_name)
            except ValueError:
                VTGenerator.raise_name_error(method_name, code)

            grp = mth.group("self_class")
            self_class: ClassDecl = self.find_class_or_none(grp)
            if not self_class:
                VTGenerator.raise_name_error(grp, code)

            node = self_class.method_impl.get(base_class)
            if node:
                node[method_name] = mth.group("func_name")
            else:
                self_class.method_impl[base_class.name] = {method_name: mth.group("func_name")}

    def _expand_decls(self):
        for cl in self.classes:
            stack = [self.find_class_index(base) for base in cl.bases_names]

            while len(stack) != 0:
                cur = stack.pop(0)
                cl.result_decl_positions.append(cur)

                for base in reversed(self.classes[cur].bases_names):
                    stack.insert(0, self.find_class_index(base))

    def _get_base_classes(self, cl: ClassDecl):
        for base in cl.bases_names: yield self.find_class_or_none(base)

    def _apply_decl(self):
        for cl in self.classes:
            try:
                self_impl = cl.method_impl.pop(cl.name)
            except KeyError:
                self_impl = {}

            for decl in cl.method_decls:
                impl = self_impl.get(decl)
                if not impl and not cl.is_abstract:
                    raise NotImplementedError(f"Non abstract class {cl.name} didn't implement its method {decl}")
                cl.result_decl_impls.append(impl)
                cl.result_interface.append(cl.name + "_" + decl)

    def _apply_base(self):
        for cl in self.classes:
            for base in self._get_base_classes(cl):
                cl.result_decl_impls.extend(base.result_decl_impls[:len(base.result_decl_impls)])
                for i in range(len(base.result_interface)):
                    cl.result_interface.append(base.result_interface[i])

    def _override(self):
        for cl in self.classes:
            for [base_class_name, impl_map] in cl.method_impl.items():
                for [method_name, method_impl] in impl_map.items():
                    cl.result_decl_impls[cl.result_interface.index(base_class_name + "_" + method_name)] = method_impl

    def generate(self):
        self._expand_decls()
        self._apply_decl()
        self._apply_base()
        self._override()

        result = f"#include \"{os.path.relpath(os.path.join(sys.path[0], 'vt.h'), self.dest_path)}\"\n"
        for path in self.file_paths:
            result += f"#include \"{os.path.relpath(path, self.dest_path)}\"\n"
        result += "\n"

        impl_buf_value = ""
        decls_buf_value = ""
        vt_value = ""

        impl_buf_size = 0
        decls_buf_size = 0
        vt_size = 0
        
        for cl in self.classes:
            for mth in cl.result_decl_impls:
                impl_buf_value += f"{mth if mth else 0},"

            for decl_ind in cl.result_decl_positions:
                decls_buf_value += f"&vt[{decl_ind}],"

            vt_value += (f"{{&db[{decls_buf_size}],&ib[{impl_buf_size}],"
                         f"{len(cl.method_decls)},{len(cl.result_decl_positions)},{vt_size}}},")

            impl_buf_size += len(cl.result_decl_impls)
            decls_buf_size += len(cl.result_decl_positions)
            vt_size += 1

        result += f"static const method_ptr ib[{impl_buf_size}];\n" \
                  f"static const vtrow_ptr db[{decls_buf_size}];\n" \
                  f"static const struct vtrow_t vt[{vt_size}];\n" \
                  "\n" \
                  f"const method_ptr ib[{impl_buf_size}] = {{{impl_buf_value}}};\n" \
                  f"const vtrow_ptr db[{decls_buf_size}] = {{{decls_buf_value}}};\n" \
                  f"const struct vtrow_t vt[{vt_size}] = {{{vt_value}}};\n\n"

        for i in range(len(self.classes)):
            result += f"const vtrow_ptr vtrow_{self.classes[i].name} = &vt[{i}];\n"
            for j in range(len(self.classes[i].method_decls)):
                result += f"const vtid_t vtid_{self.classes[i].name}_{self.classes[i].method_decls[j]} = {{{i},{j}}};\n"
            result += "\n"

        return result
