import os
import pathlib
import subprocess 
import sys

def find_files(path, fileType):
    path = pathlib.PurePosixPath(path)
    
    fileType = f".{fileType}" if "." not in fileType else fileType
    
    # store files
    filePaths = []
    
    # loop through each directory in the provided path
    for root, dirs, files in os.walk(path): 

        # loop through each file in each directory
        for file in files:
            # append the other files that need compiled
            if pathlib.Path(file).suffix == fileType:
                filePaths.append(path/file)

    return filePaths

def prepare_precompiler():
    # these commands create a missing library that allows cobol to be precompiled
    subprocess.run(['wsl', 'export', 'COB_LDFLAGS=-Wl,--no-as-needed'], shell=True)
    subprocess.run(['wsl', 'COB_LIBRARY_PATH=/usr/local/lib/libocesql'], shell=True)
    subprocess.run(['wsl', 'COB_PRE_LOAD=libocesql'], shell=True)
    subprocess.run(['wsl', '/sbin/ldconfig', '-v'], shell=True)

def compile_cobol_esql(path):
    # check for files that need precompiled
    files = find_files(path, 'cbl')
    
    # path = pathlib.PureWindowsPath(path)
    # os.chdir(path)  
    
    # check for file types
    if len(files) == 0:
        raise Exception("There are no .cbl files in this repository.")
    
    # run the commands necessary for the precompiler to function
    prepare_precompiler()
    
    for file in files:
        # sqlca does not need to be precompiled--it is used for precompiling the other files
        if file.stem == 'sqlca':
            continue
            
        # precompile the files
        subprocess.run(['wsl','ocesql',f'--inc="{file.parent}"', f'{file.stem + ".cbl"}', f'{(file.stem + ".cob")}'], shell=True)
        
        # compile the precompiled file
        subprocess.run(['wsl','cobc', '-x', '-static', '-locesql', '-lm', f'{(file.stem + ".cob")}'], shell=True)
        
def main():
    compile_cobol_esql(sys.argv[1])
    
if __name__ == '__main__':
    main()
