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

def main(inFC,prj,XYZ,outFC):


    fname = os.path.join(os.path.dirname(os.path.realpath(__file__)),'CSV_Join.py')
    python_executer = r'C:\Python27\ArcGIS10.4\python.exe'

    expression = '%s "%s" "%s" "%s" %s' %(python_executer,fname,inFC,outFC,XYZ)
    arcpy.AddMessage('%s'%(expression))
    os.system(expression)
        
    arcpy.CreateFeatureclass_management(os.path.dirname(outFC),os.path.basename(outFC),"POLYGON", "","","",prj)

    arcpy.AddField_management(outFC,"Id",'LONG')
    
    cursor = arcpy.da.InsertCursor(outFC, ["Id","SHAPE@"])

    fname = os.path.join(os.path.dirname(outFC),'temp_csv.csv')

    ID = None
    Geometries = {}
    
    with open(fname,'rb') as csvfile:
        reader = csvfile.readlines()[1:]
        for line in reader:
            line = line.split(',')
            curID = line[4]
            if curID == ID:
                x = float(line[5])
                y = float(line[3])
                Geometries[ID].add(arcpy.Point(x,y)) 
            else:
                if ID != None:
                    Geometries[ID].add(arcpy.Point(sx,sy))
                
                sx = float(line[5])
                sy = float(line[3])
                    
                ID = curID
                Geometries[ID] = arcpy.Array()
                Geometries[ID].add(arcpy.Point(sx,sy))             

    for id,features in Geometries.iteritems():
        poly_geom = arcpy.Polygon(features)
        cursor.insertRow([id,poly_geom])        
       
    os.remove(fname)
    
if __name__ == "__main__":        

    #==================================
    #Definition of inputs and outputs
    #==================================
              
    inFC=arcpy.GetParameterAsText(0)
    Projection=arcpy.GetParameterAsText(1)
    XYZ=arcpy.GetParameterAsText(2)
    outFC=arcpy.GetParameterAsText(3)

    main(inFC,Projection,XYZ,outFC)

