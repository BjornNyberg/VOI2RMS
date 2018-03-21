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

import os,arcpy,csv

def main(p,ta,tac,output):

    if len(ta) == 0 and len(tac) == 0:
	arcpy.AddError('A value is required in either the Thickness Along Axis Geometry or Thickness Across Axis Geometry parameters')
    else:

    	fname = os.path.join(os.path.dirname(os.path.realpath(__file__)),'RMS_UDO.py')
        python_executer = r'C:\Python27\ArcGIS10.4\python.exe'

   	expression = '%s "%s" "%s" "%s" "%s" "%s"' %(python_executer,fname,p,ta,tac,output)
   	arcpy.AddMessage('%s'%(expression))
   	os.system(expression)
    
if __name__ == "__main__":        

    #==================================
    #Definition of inputs and outputs
    #==================================
              
    planform=arcpy.GetParameterAsText(0)
    thicknessalong=arcpy.GetParameterAsText(1)
    thicknessacross=arcpy.GetParameterAsText(2)
    output=arcpy.GetParameterAsText(3)

    main(planform,thicknessalong,thicknessacross,output)

