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

#Algorithm body
#==================================
import pandas as pd
import networkx as nx
import math,sys,os,time


def main(folder,outFC,xyz):
    try:
        
        files = os.listdir(folder)
        for num,fn in enumerate(files):
            if fn.endswith('.asc'):
                break
        
        fname = os.path.join(folder,fn)
        df = pd.read_csv(fname,sep='\t',names=['X','Y','Z'],decimal=',')
        df['ID']=0

        for enum,fname in enumerate(files[num+1:]):
            if fname.endswith('.asc'):
                 fname = os.path.join(folder,fname)
                 df2 = pd.read_csv(fname,sep='\t',names=['X','Y','Z'],decimal=',')
                 df2['ID']=enum+1
                 df = df.append(df2)
         
        startPnts,edges,lengths,dist = {},{},{},{}
        df["X_New"] = 1.0
        df = df.reset_index()
        
        X,Y,Z =xyz.split(',')

        for n,g in df.groupby("ID"): #Calculate Edges
            Graph = nx.Graph()
            edges[n] = Graph
            maxV = 0
             
            m, mi = max(g.index),min(g.index)
            
            dist[n] = None

            for i in g.index:
                if dist[n] == None:
                    dist[n] = math.sqrt((eval(g.X[i]) - eval(X))**2 + (eval(g.Y[i]) - eval(Y))**2 + (eval(g.Z[i]) - eval(Z))**2)
                    startPnts[n] = i

                else:
                    curDist = math.sqrt((eval(g.X[i]) - eval(X))**2 + (eval(g.Y[i]) - eval(Y))**2 + (eval(g.Z[i]) - eval(Z))**2)

                    if curDist < dist[n]:
                        startPnts[n] = i
                        dist[n] = curDist
  

                if i + 1 <= m:
                    w = math.sqrt((eval(g.X[i]) - eval(g.X[i+1]))**2 + (eval(g.Y[i]) - eval(g.Y[i+1]))**2 + (eval(g.Z[i]) - eval(g.Z[i+1]))**2)
                    edges[n].add_edge(i,i+1,weight=w)

                else: 
                    w = math.sqrt((eval(g.X[i]) - eval(g.X[mi]))**2 + (eval(g.Y[i]) - eval(g.Y[mi]))**2 + (eval(g.Z[i]) - eval(g.Z[mi]))**2)
                    edges[n].add_edge(i,mi,weight=w)

        for FID in edges: #Calculate Distances
            G = edges[FID]
            Source = startPnts[FID]
            length,path = nx.single_source_dijkstra(G,Source,weight='weight')
            lengths[FID] = length

        for i,row in df.iterrows(): #Update Original Table
            dist_v = lengths[row.ID][i] + eval(X) + dist[row.ID]
            df.set_value(i,'X_New',dist_v)

        Output = os.path.join(os.path.dirname(outFC),'temp_csv.csv')
        df.to_csv(Output,index=False)
        
    except Exception,e:
        print e
        time.sleep(10)
        

if __name__ == "__main__":        

    #==================================

    #Definition of inputs and outputs
    #==================================

    folder = sys.argv[1]
    outFC = sys.argv[2]
    xyz = sys.argv[3]

    main(folder,outFC,xyz)

    
