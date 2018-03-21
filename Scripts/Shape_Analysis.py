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

#==================================

import os,arcpy

def main(inFC,Sample_Number,Directional,Averaged,Output_Folder):


    fname = os.path.join(os.path.dirname(os.path.realpath(__file__)),'Class_Profile.py')
    python_executer = r'C:\Python27\ArcGIS10.4\python.exe'

    curfields = [field.name for field in arcpy.ListFields(inFC)]
    
    try:
        curfields.remove('Shape')
    except Exception:
        pass

    temp_csv = os.path.join(os.path.dirname(os.path.realpath(__file__)),'temp_csv.csv')

    with open(temp_csv,'w') as f:
	for field in curfields[:-1]:
	    f.write('%s:'%(field))
	f.write('%s'%(curfields[-1]))
	f.write('\n')
    	for row in arcpy.da.SearchCursor(inFC,curfields):
   	    for enum,field in enumerate(curfields[:-1]):
		f.write('%s:'%(row[enum]))
	    f.write('%s'%(row[enum+1]))
            f.write('\n')

    if len(Output_Folder) < 1:
        Output_Folder = False
    if len(Directional) < 1:
        Directional = False
    if len(Averaged) < 1:
        Averaged = False

    #==================================
    #Advanced parameters
    #==================================
    Sinuous_Threshold=0.2
    Symmetry_Threshold=0.2
    Linear_Threshold=0.5
    Crescentric_Threshold=1
    Polynomial_Order=25
    #==================================
    
    expression = '%s "%s" "%s" %s %s "%s" %s %s %s %s %s %s'%(python_executer,fname,temp_csv,Directional,Sample_Number,Output_Folder,Sinuous_Threshold,Symmetry_Threshold,Linear_Threshold,Crescentric_Threshold,Polynomial_Order,Averaged)
    arcpy.AddMessage('%s'%(expression))
    os.system(expression)
    os.remove(temp_csv)


if __name__ == "__main__":        

    #==================================
    #Definition of inputs and outputs
    #==================================
              
    inFC=arcpy.GetParameterAsText(0)
    Sample_Number=arcpy.GetParameterAsText(1)
    Directional=arcpy.GetParameterAsText(2)
    Averaged =arcpy.GetParameterAsText(3)
    Output_Folder=arcpy.GetParameterAsText(4)

    main(inFC,Sample_Number,Directional,Averaged,Output_Folder)

