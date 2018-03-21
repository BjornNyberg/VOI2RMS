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

import arcpy,os,math
import networkx as nx

arcpy.env.overwriteOutput= True

def Deviation(infc):

    curfields = [f.name for f in arcpy.ListFields(infc)]

    if 'Deviation' not in curfields:
        arcpy.AddField_management(infc,'Deviation',"DOUBLE")
    if 'SP_Length' not in curfields:
        arcpy.AddField_management(infc,'SP_Length',"DOUBLE")
        
    fields = ['Id','Distance','RDistance','RDCoordx','RDCoordy','DCoordx','DCoordy','SHAPE@','Deviation','SP_Length']
    SP = {}
    SP2 = {}

    for feature in arcpy.da.SearchCursor(infc, fields):
        try:
            geom = feature[7].length
            if round(geom,2) == round(feature[1],2): 
                SP[feature[0]]=[feature[3],feature[4]]
            if round(geom,2) == round(feature[2],2):
                SP2[feature[0]]=[feature[5],feature[6]]
                
        except Exception,e:
            arcpy.AddError('%s'%(e))
            continue

    with arcpy.da.UpdateCursor(infc,fields) as cursor:
        for feature in cursor:
            try:
                midx,midy = feature[5],feature[6]

                startx,starty=(SP[feature[0]][0],SP[feature[0]][1])
                endx,endy =(SP2[feature[0]][0],SP2[feature[0]][1])

                dx = startx-endx
                dy = starty-endy

                m = (dx**2)+(dy**2)

                u = ((midx - startx) * (endx - startx) + (midy - starty) * (endy - starty))/(m)
                x = startx + u * (endx - startx)
                y = starty + u * (endy - starty)
                d = ((endx-startx)*(midy-starty) - (endy - starty)*(midx - startx)) #Determine which side of the SP the symmetry occurs

                if u > 1:
                    u = 1
                elif u < 0:
                    u = 0

                dx = x - midx
                dy =  y - midy
                
                dist = math.sqrt((dx**2)+(dy**2))

                if d < 0:
                    DW = -(dist)
                else:
                    DW = dist
                feature[-2]=DW
                feature[-1]= math.sqrt(m)
                cursor.updateRow(feature)


            except Exception,e:
                arcpy.AddError('%s'%(e))
                continue
            
def Width(infc,mask):
    area = {}

    for feature in arcpy.da.SearchCursor(mask,['SHAPE@','Id']):
        try:
            if feature[1] not in area:
                area[feature[1]] = feature[0].area
                
        except Exception,e:
            arcpy.AddError('%s'%(e))

    arcpy.FeatureToLine_management([mask],'in_memory\\templines',"0.001 Meters", "ATTRIBUTES")
    dname = os.path.dirname(infc)
    arcpy.CreateFeatureclass_management('in_memory','temppoints',"POINT",'','','',infc)
    arcpy.AddField_management('in_memory\\temppoints','FID',"LONG")
    
    cursor = arcpy.da.InsertCursor('in_memory\\temppoints',['SHAPE@','FID'])
    fields = ['Id','DCoordx','DCoordy','OID@']
    for row in arcpy.da.SearchCursor(infc,fields):
        data = [[row[1],row[2]],row[-1]]
        cursor.insertRow(data)

    arcpy.Near_analysis('in_memory\\temppoints', 'in_memory\\templines')

   
    curfields = [f.name for f in arcpy.ListFields(infc)]
    if 'Width' not in curfields:
        arcpy.AddField_management(infc,'Width',"DOUBLE")

    if 'Area' not in curfields:
        arcpy.AddField_management(infc,'Area',"DOUBLE")
        
    fields.extend(['Width','Area'])
   
    data = {f[0]:f[1] for f in arcpy.da.SearchCursor('in_memory\\temppoints',['FID','NEAR_DIST'])}

    with arcpy.da.UpdateCursor(infc,fields) as cursor:
        for feature in cursor:
            try:
                feature[-2] = data[feature[-3]] * 2
                feature[-1] = area[feature[0]]
                cursor.updateRow(feature)
            except Exception,e: #No Connection?
                arcpy.AddError('%s'%(e))
                continue

def Centerline(infc):

    edges = {}

    temp3 = 'in_memory\\tempdata3'
    temp4 = 'in_memory\\tempdata4'

    arcpy.MinimumBoundingGeometry_management(infc, temp3,"RECTANGLE_BY_WIDTH", "ALL")
    arcpy.Intersect_analysis([temp3, inFC], temp4, "","","POINT")
    arcpy.MultipartToSinglepart_management(temp4,temp3)

    
    values = [f[0] for f in arcpy.da.SearchCursor(temp3,['SHAPE@'])]
    distance = 0

    for feature in values:

        startx,starty = feature.firstPoint.X,feature.firstPoint.Y
        for feature2 in values:
            endx,endy = feature2.firstPoint.X,feature2.firstPoint.Y
            dx = startx-endx
            dy = starty-endy
            dist = math.sqrt((dx**2)+(dy**2))
            if dist > distance:
                distance = dist
                pnt = (startx,starty)

    for feature in arcpy.da.SearchCursor(infc,['SHAPE@','Id']):
        try:
            start = feature[0].firstPoint
            end = feature[0].lastPoint
            pnts1,pnts2 = [(start.X,start.Y),(end.X,end.Y)]
            Length = feature[0].length
            ID = feature[1]
            if ID in edges:
                edges[ID].add_edge(pnts1,pnts2,weight=Length)
            else:
                Graph = nx.Graph()
                Graph.add_edge(pnts1,pnts2,weight=Length)
                edges[ID] = Graph
        except Exception,e:
            arcpy.AddError('%s'%(e))
            
    data = set([])
    Lengths = {}

    del values
    for FID in edges:
        try:
            G = edges[FID]
            G = max(nx.connected_component_subgraphs(G),key=len) #Largest Connected Graph

            source = G.nodes()[0]
            for n in range(2):
                length,path = nx.single_source_dijkstra(G,source,weight='weight')          
                Index = max(length,key=length.get)
                source = path[Index][-1]
            
            data.update(path[Index])
            
            dx = source[0]-pnt[0]
            dy = source[1]-pnt[1]
            dist = math.sqrt((dx**2)+(dy**2))
            
            source2 = path[Index][0]
            dx = source2[0]-pnt[0]
            dy = source2[1]-pnt[1]
            dist2 = math.sqrt((dx**2)+(dy**2))

            if dist2 > dist:
                length2 = length
                length,path = nx.single_source_dijkstra(G,source,weight='weight')  
            else:
                length2,path = nx.single_source_dijkstra(G,source,weight='weight')
                
            Lengths[FID] = [length,length2]
                
        except Exception,e:
            arcpy.AddError('%s'%(e))  
 
    curfields = curfields = [f.name for f in arcpy.ListFields(infc)]
    fields = ["Distance","RDistance","DCoordx","DCoordy","RDCoordx","RDCoordy"]
    for field in fields:
        if field not in curfields:
            arcpy.AddField_management(infc,field,"DOUBLE")
            
    with arcpy.da.UpdateCursor(infc,['SHAPE@','Id',"Distance","RDistance","DCoordx","DCoordy","RDCoordx","RDCoordy"]) as cursor:

        for feature in cursor:
            try:
                start = feature[0].firstPoint
                end = feature[0].lastPoint
                pnts = [(start.X,start.Y),(end.X,end.Y)]
                pnts1,pnts2 = pnts

                startx,starty = pnts1
                endx,endy = pnts2
            
                if pnts1 not in data or pnts2 not in data:
                    cursor.deleteRow()
                else:
                    ID = feature[1]
                    L = [Lengths[ID][0][(endx,endy)],Lengths[ID][0][(startx,starty)]]
                    if L[0] > L[1]:
                        sx = startx
                        sy = starty
                        ex = endx
                        ey = endy
                    else:
                        sx = endx
                        sy = endy
                        ex = startx
                        ey = starty
                        
                    L2 = [Lengths[ID][1][(endx,endy)],Lengths[ID][1][(startx,starty)]]

                    feature[2]=max(L)
                    feature[3]=max(L2)
                    feature[4]=ex 
                    feature[5]=ey
                    feature[6]=sx
                    feature[7]=sy
                    
                    cursor.updateRow(feature)
            except Exception,e:
                arcpy.AddError('%s'%(e))
                continue 
def Voronoi_Lines(inFC,Output):

    try:
    
        #Variables
        temp = 'in_memory\\tempdata'
        temp2 = 'in_memory\\tempdata2'

        arcpy.FeatureVerticesToPoints_management(inFC,temp, "ALL")
        arcpy.CreateThiessenPolygons_analysis(temp, temp2, "ONLY_FID")
        arcpy.PolygonToLine_management(temp2, temp)
        arcpy.Intersect_analysis([temp, inFC], temp2, "ALL")
        arcpy.MultipartToSinglepart_management(temp2, Output)

        fieldNames = []
        for field in arcpy.ListFields(Output):
            if not field.required and field.name != 'Id':
                fieldNames.append(field.name)
        arcpy.DeleteField_management(Output,fieldNames)

        Centerline(Output)
        Width(Output,inFC)
        Deviation(Output)
        
    except Exception,e:
        arcpy.AddError('%s'%(e))

def main(inFC,Vertices,Output):
    try:
        arcpy.AddMessage('\n')

        fields = [f.name for f in arcpy.ListFields(inFC)]

        Count = int(arcpy.GetCount_management(inFC).getOutput(0))
        TempFolder = os.path.dirname(inFC)
        temp = os.path.join(TempFolder,'temp.lyr')
        
        merge = []
        
        for n in xrange(Count):
            arcpy.AddMessage('Processing feature %s of %s'%(n+1,Count))
            arcpy.MakeFeatureLayer_management(inFC, temp)          
            arcpy.SelectLayerByAttribute_management(temp, "NEW_SELECTION", '"Id" = %s'%(n))  

	    if '.gdb' in TempFolder: #Geodatabase file	
	        TempInput = os.path.join(TempFolder,'temp_input')
           	TempOutput = os.path.join(TempFolder,'temp_%s'%(n))   
            else: #Shapefile 
                TempInput = os.path.join(TempFolder,'temp_input.shp')
                TempOutput = os.path.join(TempFolder,'temp_%s.shp'%(n))   

            arcpy.CopyFeatures_management(temp,TempInput)
	    for f in arcpy.da.SearchCursor(TempInput,['SHAPE@']):
		perim = f[0].length

	    Densify = perim/Vertices
		
            arcpy.Densify_edit(TempInput, "DISTANCE",Densify, "", "")
            merge.append(TempOutput)
            Voronoi_Lines(TempInput,TempOutput)
                                     
        arcpy.Merge_management(merge,Output)

        for fname in merge:
            arcpy.Delete_management(fname)
            
        arcpy.Delete_management(TempInput)

        arcpy.AddMessage('\n')

    except Exception,e:
        arcpy.AddError('%s'%(e))


if __name__ == "__main__":        
    ###Inputs###
    inFC = arcpy.GetParameterAsText(0)
    inFC = arcpy.Describe(inFC).catalogPath
    Output = arcpy.GetParameterAsText(1)

    #==================================
    #Advanced parameters
    #==================================
    Vertices = 2500.0 # Number of vertices to represent a polygon - higher number = more detail
    #==================================

    main(inFC,Vertices,Output)
