import sys
import os
from pathlib import Path

from parsing import VTGenerator

extensions = ["h", "hpp"]
output_path = os.path.dirname(sys.argv[0])
src_dirs = []
file_paths = []


def eval_flag(flag: str, flag_args: list[str]):
    global extensions, output_path, src_dirs, file_paths
    if flag == "o":
        output_path = flag_args.pop(0)
    elif flag == "src":
        src_dirs.extend(flag_args)
        flag_args.clear()
    elif flag == "ex":
        extensions = list(map(lambda x: x.removeprefix("."), flag_args))
        flag_args.clear()
    elif flag == "-help":
        print("vtc [targets] [-src] [-o] [-ex]\n\n"
              "Generates \"vt_impl.c\" file that will implement virtual table for classes specified in given files\n\n"
              "targets - sequence of files to analyse\n"
              "-o <dir> - put output to <dir>\n"
              "-src <dir1> [<dir2>...] - search for files into <dir[n]>\n"
              "-ex <ex1> [<ex2>...] - specify file extensions <ex[n]> to search for\n")
        exit()
    if len(flag_args):
        file_paths.extend(flag_args)
        flag_args.clear()


def process_cmd_args():
    arg_buf = []
    flag = None
    for arg in sys.argv[1:]:
        if arg[0] == "-":
            eval_flag(flag, arg_buf)
            flag = arg[1:]
            continue

        arg_buf.append(arg)

    eval_flag(flag, arg_buf)


if __name__ == "__main__":
    print("picked args",  sys.argv)

    process_cmd_args()

    for dir_path in src_dirs:
        for subdir, dirs, files in os.walk(dir_path):
            for file in files:
                if os.path.splitext(file)[1].removeprefix(".") in extensions:
                    file_paths.append(os.path.join(subdir, file))

    targets = set(map(lambda p: Path(p).resolve(), file_paths))
    print("extensions : ", extensions)
    print("output_path : ", output_path)
    print("src_dirs : ", src_dirs)
    print("file_paths : ", file_paths)
    print("targets : ", targets)
    
    gen = VTGenerator(output_path)
    for file in targets:
        gen.add_file(file)

    open(Path(output_path).joinpath("./vt_impl.c"), "w").write(gen.generate())
