#==================================
#Author Bjorn Burr Nyberg 
#University of Bergen
#Contact bjorn.nyberg@uib.no
#Copyright 2016
#==================================

'''This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

import os,sys,subprocess

dirname = os.path.split(os.path.dirname(sys.executable))
folder = dirname[1].replace('x64','')

python_exe = os.path.join(dirname[0],folder,'python.exe')

try:
    import pip
except Exception:
    dirname = os.path.dirname(os.path.realpath('__file__'))
    fname = os.path.join(dirname,'get-pip.py')
    os.system(fname)
    import pip

from shutil import copyfile
from distutils.dir_util import copy_tree
modules = ['pandas','networkx==1.8','matplotlib']

for module in modules:
    try:
        subprocess.check_call([python_exe,'-m', 'pip', 'install','--upgrade', module])
    except Exception,e:
        print e
        continue

def main(python_exe):
    files = ['User_Defined_Object.py','3D22D.py','Shape_Analysis.py']
    try:
        python_exe = sys.executable.replace('w','')
        for fname in files:
            dirname = os.path.split(os.path.dirname(os.path.realpath('__file__')))
            fname_in = os.path.join(dirname[0],'Scripts',fname)
            fname_out = os.path.join(dirname[0],'Scripts','temp_%s'%(fname))
            
            with open(fname_in, 'r') as input_file, open(fname_out, 'w') as output_file:
                for line in input_file:
                    if 'python_executer =' in line:
                        spaces = line.partition("p")[0]
                        new_line = spaces + 'python_executer = r"%s"\n'%(python_exe)
                        output_file.write(new_line)          
                    else:
                        output_file.write(line)
                        
            copyfile(fname_out,fname_in)
            os.remove(fname_out)
            
        for module in modules:
            try:
                subprocess.check_call([python_exe,'-m', 'pip', 'install','--upgrade', module])
            except Exception,e:
                print e
                continue
            
        print '\n Finished'
    except Exception,e:
        print e
        
if __name__ == "__main__":

    main(sys.executable)

