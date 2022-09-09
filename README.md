
### Author:
- [Maria Rossano](https://github.com/rossanot)

A module, `coordgaus`, to extract the optimized
coordinates from a (gaus) .log output file. The
`XFile `, `GaInpFile`, and `SupInfFile` print out these coordinates into
.xyz, .com, and .txt files, respectively. 


Examples:

i) .xyz file.

    file_xyz = XFile(file, WORKDIR_PATH=WORKDIR)
    file_xyz.get_xyz()

ii) .com input file.

    new_file_2 = GaInpFile(file, WORKDIR_PATH=WORKDIR)
    new_file_2.get_gainp()

iii) .txt file.

    file_si = SupInfFile(file, WORKDIR_PATH=WORKDIR)
    file_si.get_si()


An already-to-use script, `ext_coord_example_script.py` is provided. 
From `ext_coord_example_script.py -h`:

    usage: ext_coord_example_script.py [-h] [-f file_type] working_directory
    
    Get coordinates from Gaussian .log and return them in .xyz, .com, 
    and/or LaTeX-type format using the `coordgaus` library.
    
    positional arguments:
      working_directory  The path where the files are.
    
    optional arguments:
      -h, --help         show this help message and exit
      -f file_type       The type of file to be parsed, e.g., .log