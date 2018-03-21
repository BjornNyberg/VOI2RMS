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

import sys,time
import os,numpy,time
from pylab import *
import math
from itertools import izip

from pandas import DataFrame,Series,concat,ExcelWriter,read_csv
from scipy import stats


def main(inFC,Directional,Sample_Number,Output_Folder,Sinuous_Threshold,Symmetry_Threshold,Linear_Threshold,Crescentric_Threshold,Polynomial_Order,Averaged):
    try:
        values,output = {},{}
        
        df = read_csv(inFC,sep=':')
        
        df2 = None

        Groups = df.groupby("Id")
        Total = len(Groups)
        Counter = 0
        print('Calculating Fields')
        for name,g in Groups: #Normalize data to compare 
            try:
                Counter += 1

                x = [n/g.Distance.max() for n in g.Distance]
                y = [n/g.Width.max() for n in g.Width]
                
                m, intercept, r_value, p_value, std_err = stats.linregress(x,y)
                r2=r_value**2
                
                xMax = g.Deviation.abs().max()     
                x = [n/xMax for n in g.Deviation if n > 0]
                x2 = [-(n/-xMax) for n in g.Deviation if n < 0]
                
                mm = [float(len(x)),float(len(x2))] #min and max values
                mm = min(mm)/max(mm)  
                c=xMax/(g.Width.max()/2)

                if m > 0 or Directional:
                    Distance = (g.Distance - g.Distance.min()) / (g.Distance.max() - g.Distance.min())
                else:
                    Distance = (g.RDistance - g.RDistance.min()) / (g.RDistance.max() - g.RDistance.min()) 
                if len(x) > len(x2):
                    Org_Deviation = g.Deviation
                else:
                    Org_Deviation = -g.Deviation

                Width1=(g.Width/2) + Org_Deviation
                Width2=-(g.Width/2) + Org_Deviation

                Width = (g.Width/g.Width.max()) 
                DWidth = (Width1 - Width2.min()) / (Width1.max() - Width2.min()) - 0.5
                DWidth2 =(Width2 - Width2.min()) / (Width1.max() - Width2.min()) - 0.5
                Deviation =(Org_Deviation - Width2.min()) / (Width1.max() - Width2.min()) - 0.5

                if Averaged == 'true':
                    Class = 'Avg'
                    
                else:
                    if c > eval(Crescentric_Threshold):
                        if mm < eval(Sinuous_Threshold): 
                            if fabs(m) > eval(Symmetry_Threshold):
                                Class = "C AS"
                            elif r2 > eval(Linear_Threshold):
                                Class = "C L"    
                            else:
                                Class = "C E"
                        else:
                            if fabs(m) > eval(Symmetry_Threshold):
                                Class = "L-S AS"
                            elif r2 > eval(Linear_Threshold):
                                Class = "L-S L"    
                            else:
                                Class = "L-S E"
                    else:
                        if fabs(m) > eval(Symmetry_Threshold):
                            Class = "E AS"
                        elif r2 > eval(Linear_Threshold):
                            Class = "L S"               
                        else:
                            Class= "E S"

                if fabs(m) > eval(Symmetry_Threshold):
                        if Directional == 'true':
                            if m > 0:
                                Class = '%s 1'%(Class)
                            else:
                                Class = '%s 0'%(Class)

                if df2 is None:
                    df2 = DataFrame({"FID":name,"Width":Width,"DWidth":DWidth,"DWidth2":DWidth2,"Max Width":g.Width.max(),"Centerline Deviation Ratio":c,"Class":Class,"Distance":Distance,"Deviation":Deviation,"Area":g.Area.max(),"Sinuosity":g.Distance.max()/g.SP_Length.max(),"Length":g.Distance.max()})
                else:
                    df3 = DataFrame({"FID":name,"Width":Width,"DWidth":DWidth,"DWidth2":DWidth2,"Max Width":g.Width.max(),"Centerline Deviation Ratio":c,"Class":Class,"Distance":Distance,"Deviation":Deviation,"Area":g.Area.max(),"Sinuosity":g.Distance.max()/g.SP_Length.max(),"Length":g.Distance.max()})
                    df2 = concat([df2,df3])
                
            except Exception,e:
                print('%s'%(e))
                continue
            
        print('Plotting Profiles')

        del df

        Groups = df2.groupby("Class")
        Total = len(Groups)
        Counter = 0

        for n,g in Groups:

            Counter += 1
            x =g.Distance

            if len(x) == 0:
                continue
                
            y = g.Width
            y2 = g.Deviation
            y3 = g.DWidth
            y4 = g.DWidth2
            
            pw = np.poly1d(np.polyfit(x,y,Polynomial_Order))
            xx = np.linspace(min(x),max(x), 1000)

            fig = figure(Counter)
            ax = fig.add_subplot(221)
            ax.set_ylabel('Total Width')
            
            ax2 = fig.add_subplot(222)
            ax2.set_ylabel('Centerline Deviation')
            
            ax3 = fig.add_subplot(223)
            ax3.set_xlabel('Distance')
            ax3.set_ylabel('Width Deviation')
            
            ax4 = fig.add_subplot(224)
            ax4.set_xlabel('Distance')
            ax4.set_ylabel('Interpolated Width')
            
            ps = np.poly1d(np.polyfit(x,y2,Polynomial_Order))
            pdw = np.poly1d(np.polyfit(x,y3,Polynomial_Order))
            pdw2 = np.poly1d(np.polyfit(x,y4,Polynomial_Order))
            
            ax.plot(x,y,'bo',xx,pw(xx),'r-')
       
            ax2.plot(x,y2,'bo',xx,ps(xx),'r-')
   
            ax3.plot(x,y3,'bo',x,y4,'go')

            ax4.plot(xx,pdw(xx),xx,pdw2(xx),xx,ps(xx))
      
            subplots_adjust(left=0.1,bottom=0.1,right=0.95,top=0.9,wspace=0.3,hspace=0.2)

            values = numpy.linspace(0,1,Sample_Number)

            suptitle('Profile Geometry %s'%(n),fontsize=16)

            
            if Output_Folder != 'False':
                group = g.groupby("FID").max()

                group = group[["Length","Max Width","Centerline Deviation Ratio","Area","Sinuosity"]]

                TW = Series(pw(values)) #Normalize Total Width of polynomial fit to 1
                
                if min(TW) < 0: #0 to 1 if min below 0
                    TW = (TW - min(TW)) / (max(TW) - min(TW))
                else:
                    TW = TW / max(TW)                
                
                TWidth = DataFrame({'Centerline': Series([0]*len(values)),'Total Width': TW}) #Total Width

                DWidth = DataFrame({'Centerline':Series(ps(values)), 'Rel. Width': Series(pdw(values)) }) #Deviated Width
                DWidth["Rel. Width"]=(DWidth["Rel. Width"] - DWidth["Centerline"])*2 #Determine the Relative Width

                DWidth['Rel. Width'][DWidth['Rel. Width'] < 0 ] = 0
                Rel_Width,Centerline = [],[]
                for i,row in DWidth.iterrows():
                    value = float(row['Rel. Width'])
                    value2 = float(row['Centerline'])
                    if value2 > 0.5:
                        value2 = 0.5
                    elif value2 < -0.5:
                        value2 = -0.5
                    if (value/2.0) + abs(value2) > 0.5:
                        value = (0.5 - abs(value2))*2.0

                    Rel_Width.append(value)
                    Centerline.append(value2)

                DWidth['Rel. Width'] = Rel_Width
                DWidth['Centerline'] = Centerline  

                m_v = 1.0/max(DWidth['Rel. Width'])#Maximum difference
                group["M_Factor"] = m_v

                excel_output = os.path.join(Output_Folder,'%s_DataSummary.xlsx'%(n))
                DWidth_csv = os.path.join(Output_Folder,'%s_DWidth.dat'%(n))
                TWidth_csv = os.path.join(Output_Folder,'%s_TWidth.dat'%(n))
                writer = ExcelWriter(excel_output) 
    
                group.describe().to_excel(writer, 'Profile Geometry')
                
                with open(TWidth_csv,'w') as f:
                    f.write('2\n%s\n'%(Sample_Number))
                    TWidth.to_csv(f,header=False,index=False,sep=' ')
                with open(DWidth_csv,'w') as f:
                    f.write('2\n%s\n'%(Sample_Number))    
                    DWidth.to_csv(f,header=False,index=False,sep=' ')

                Output = os.path.join(Output_Folder,'%s.jpg'%(n))

                savefig(Output,dpi=200)

                clf()
                
                writer.save()

            else:
                show()

                
    except Exception,e:
        print e
        time.sleep(10)

if __name__ == "__main__":
    
    try:
        inFC =sys.argv[1]
        Directional=sys.argv[2]
        Sample_Number=sys.argv[3]
        Output_Folder=sys.argv[4]
        Sinuous_Threshold=sys.argv[5]
        Symmetry_Threshold=sys.argv[6]
        Linear_Threshold=sys.argv[7]
        Crescentric_Threshold=sys.argv[8]
        Polynomial_Order=sys.argv[9]
        Averaged=sys.argv[10]

        main(inFC,Directional,Sample_Number,Output_Folder,Sinuous_Threshold,Symmetry_Threshold,Linear_Threshold,Crescentric_Threshold,Polynomial_Order,Averaged)
        
    except Exception,e:
        print '%s e'%(e)
        time.sleep(10)
