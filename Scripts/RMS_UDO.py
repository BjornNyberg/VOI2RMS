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
import os, time,sys

def main(p,ta,tac,outfname):
    try:
        
        df = pd.read_csv(p,skiprows=2,header=None,sep=' ')
        outfname = os.path.splitext(outfname)[0] + '.dat'
        s = 2
        
        if ta:
            df2 = pd.read_csv(ta,skiprows=2,header=None,sep=' ')
            
            if len(df) != len(df2):
                print 'Error Planform Geometry dimensions must equal Thickness Along Axis Geometry dimensions'
                print 'Quitting process'
                time.sleep(15)
                sys.exit()

            df[2] = df2[1] * 0.5   
            df[3] = df2[1] * 0.5 
            s = 4

        if tac:
            df2 = pd.read_csv(tac,skiprows=2,header=None,sep=' ')
            df2[0] = [0.0] * len(df2) 
            df2[1] = df2[1] * 0.5
            
            outfname_tac = os.path.splitext(outfname)[0] + '.dat_thicknessY'

            with open(outfname_tac,'w') as f:
                f.write('%s\n'%(len(df2)))   
                df2.to_csv(f,header=False,index=False,sep=' ')

        with open(outfname,'w') as f:
            f.write('%s\n%s\n'%(s,len(df)))    
            df.to_csv(f,header=False,index=False,sep=' ')

    except Exception,e:
        print e
        time.sleep(10)
         

if __name__ == "__main__":        

    #==================================

    #Definition of inputs and outputs
    #==================================

    p = sys.argv[1] #planform
    ta = sys.argv[2] #thickness along axis
    tac = sys.argv[3] #thickness across axis
    outfname = sys.argv[4] #Output file

    main(p,ta,tac,outfname)

    
