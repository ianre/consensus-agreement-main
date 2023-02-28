from asyncio import Task
import os, sys
import json
import pathlib
import math
import numpy as np
from PIL import Image, ImageDraw, ImageColor
import krippendorff
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pkg_resources import invalid_marker
import statistics
from numpy.linalg import matrix_power


#from crowdkit.aggregation import DawidSkene
#from crowdkit.datasets import load_dataset

#import pandas as pd

global unique_labels
unique_labels = {}

global invalid_States
invalid_States = {}

'''
This program combines labels in "kay", "ian", and "volunteer" folders into three types of consensus data:

"output" contains the consensus labels
"match" contains a comparison between all labels as well as kappa for all 4 sets (kay vs. ian vs. volunteer) and (kay vs. ian vs. volunteer vs. consensus)
"kappa" 
'''

mathematicaColors = {
    "blue":"#5E81B5",
    "orange":"#E09C24",
    "red":"#EA5536",
    "purple":"#A5609D",
    "green":"#8FB131",
}
# list of colors for the annotations
colors =["#5E81B5","#D47BC9","#FAB6F4","#C9602A","#E09C24","#EA5536","#A1C738","#5E81B5","#D47BC9","#7CEB8E","#E36D6D","#C9602A","#77B9E0","#A278F0","#D66F6D"]
# opacity of the annotation masks. Values range from (0 to 255) Type tuple
opacity = (180,)
# radius of keypoint
radius = 4

def main(): 
    
    dir=os.getcwd()
    '''
    try:
        task=sys.argv[1]
        #print(task)
    except:
        print("Error: no task provided \nUsage: python draw_labels.py <task>")
        available_tasks = next(os.walk(os.path.join(dir, "images")))[1]
        print("Available task images: ", available_tasks)
        available_labels = next(os.walk(os.path.join(dir, "labels")))[1]
        print("Available task labels: ", available_labels)
        sys.exit()
    '''

    #print(task)
    task = "Knot_Tying" #then suturing to b done w/ jigs
    I = Iterator(task)
    #I.fixStates()
    #I.poll()
    #I.verifyOutput()
    I.showAllPlots()
    I.metrics()
    quit(); 

class Iterator:
    def __init__(self, task):
        self.CWD = os.path.dirname(os.path.realpath(__file__))        
        self.task = task
        self.outputDir = os.path.join(self.CWD, self.task,"output")
        self.ian = os.path.join(self.CWD,self.task, "ian")
        self.kay = os.path.join(self.CWD,self.task, "kay")

        self.pre_ian = os.path.join(self.CWD,self.task, "ian_pre")
        self.pre_kay = os.path.join(self.CWD,self.task, "kay_pre")

        self.v = os.path.join(self.CWD, self.task,"volunteer")
        #self.v2 = os.path.join(self.CWD, self.task,"vol2")
        self.kappa = os.path.join(self.CWD, self.task,"kappa")
        #self.match = os.path.join(self.CWD, self.task,"match_lines")

    def fixLine(self, line):
        # index 5 is where the pea state is:
        l_s = line.split(" ")
        #print(l_s[5], end='')
        #print(l_s[5])
        return line;
    # transcript as a list of lists.
    def transcriptToList(self, transcript):
        list = []
        #print(transcript)
        # For each label, fill in the list with that label from start to end sample number
        for t in transcript:
            fill = [t[2]]*(int(t[1])-int(t[0]))
            list[int(t[0]):int(t[1])] = fill

        return list

    def tToList(self, t):
        newList = []
        for line in t:
            start = line[0];
            end = line[1];
            gesture = line[2];
            for i in range(start, end+1):
                newList.append( str(i) + " " + gesture)
        return newList;

    def fixLine_Ian(self, line):
        l_s = line.split(" ")
        #print(l_s[5], end='')
        #print(l_s[5])
        return line;

    def fixLines(self, lines ):
        RH = 3
        RC = 4
        LH = 1
        LC = 2
        PEA = 5                
        four = False
        i = 0
        for line in lines:
            l_s = line.split(" ")
            if(l_s[PEA] == "4" ):
                four = True
            if( four ):
                if( (l_s[LH] == "1" or l_s[LC] == "1" or l_s[RH] == "1" or l_s[RC] == "1") ): #  and l_s[PEA] == "4"
                    if(l_s[PEA] == "4"):
                        # it was already 4
                        pass
                    elif(l_s[PEA] == "3"):
                        four = False
                    else:
                        l_s[PEA] = "4"
                        print(str(i) , " change to 4")
                if( l_s[LH] == "0" and l_s[LC] == "0" and l_s[RH] == "0" and l_s[RC] == "0" ):
                    four = False
            lines[i] = " ".join(l_s)
            i=i+1
            #print(line)
        return lines;

    def fixLines_Ian(self, lines):
        for line in lines:
            line = self.fixLine_Ian(line);
            #print(line)
        return lines;

    def fixStates(self):
        count = 0
        for root, dirs, files in os.walk(self.kay):
            for file in files: 
                #if("99" not in file):
                #    continue
                count=count+1
                kay_file =  os.path.join(self.kay, file)
                ian_file =  os.path.join(self.ian, file)
                v_file = os.path.join(self.v, file)  
                
                kay_lines = []
                with open(kay_file) as kay_data:
                    for line in kay_data:
                        kay_lines.append(line.strip())
                
                ian_lines = []
                with open(ian_file) as ian_data:
                    for line in ian_data:
                        ian_lines.append(line.strip())
                #print("Here")
                #ian_lines = self.takeAwayAngles(ian_lines)
                v_lines = []
                with open(v_file) as v_data:
                    for line in v_data:
                        v_lines.append(line.strip())
                print("File: ",file)
                print("\tkay:")
                kay_lines = self.fixLines(kay_lines)
                print("\t V:")
                v_lines = self.fixLines(v_lines)
                print("\tian:")
                ian_lines  = self.fixLines(ian_lines)

                #self.save(kay_file,kay_lines)
                #self.save(v_file, v_lines)
                #self.save(ian_file, ian_lines)              

        return;

    def showAllPlots(self):

        plots = []
        saved_Files = []
        fileCount = 0;
        count = 0
        pdfCount = 0
        try:
            os.remove(self.task+"_"+str(pdfCount)+".pdf")
        except OSError:
            pass
        pp = PdfPages(self.task+"_"+str(pdfCount)+".pdf")
        for root, dirs, files in os.walk(self.kappa):
            for file in files:
                if("99" in file):
                    continue
                if(fileCount %15 == 0):
                    pp.close();
                    pdfCount = pdfCount +1
                    try:
                        os.remove(self.task+"_"+str(pdfCount)+".pdf")
                    except OSError:
                        pass
                    pp = PdfPages(self.task+"_"+str(pdfCount)+".pdf")

                kappa_file = os.path.join(self.kappa, file)
                #files.append(kappa_file)
                plot = self.getPlot(kappa_file,file)
                saved_Files.append(file)
                plots.append(plot)   
                #print(fileCount, "created plot for file:",saved_Files[fileCount])
                #fileCount=fileCount+1 
                pp.savefig(plot) 
                fileCount = fileCount + 1;           
            
        '''
        for p in plots:
            print("count",count)
            pp.savefig(p)
            try:
                pp.savefig(p)
                print("saved file:",saved_Files[count])
            except:
                print("something went wrong with graph", saved_Files[count])
            
            count=count+1;
        '''
        pp.close();
        return;

    def metrics(self):

        fileCount = 0
        pre = 0
        post = 0
        preAggregate = 0
        postAggregate = 0
        allSigma = 0;
        sigmas = []
        lineCount = 0;
        for root, dirs, files in os.walk(self.kappa):
            for file in files:
                if("99" in file):
                    continue 
                kappa_file = os.path.join(self.kappa, file)
                #print(len(ka))
                #plot = self.getPlot(kappa_file,file)
                l_c, sigma, preAvg, postAvg, preAgr, postAgr = self.getAverage(kappa_file,file)
                pre = pre+preAvg
                post= post+postAvg
                preAggregate=preAggregate+preAgr
                postAggregate=postAggregate+postAgr
                #allSigma = sigma+allSigma
                sigmas.append(sigma)
                print(file, str(preAvg), str(postAvg), str(sigma)) 
                fileCount = fileCount + 1; 
                lineCount=lineCount+l_c;

        sigma2 = sum(i*i for i in sigmas)
        sigma2 = sigma2 / (fileCount+1)
        sigma2 = math.sqrt(sigma2)
        print(self.task)
        print( "Length:",str(lineCount))
        print( "Pre Unweight:",str( pre / (fileCount+1.0)))
        print( "Post Unweight:",str( post  / (fileCount+1.0)))
        print( "Sigma:",str( sigma2 ))
        print( "Pre Weight:",str( preAggregate / lineCount ))
        print( "Post Weight:",str(  postAggregate / lineCount ))

        return;
    def getAverage(self,file,fileName,x_col=0, y_col=3,y_c_col=3):
        preAvg = 0
        postAvg = 0
        preAgr = 0
        postAgr = 0

        f = open(file)
        lines=f.readlines()        
        x, y, y_c= [], [], []
        lineCount = 0;
        for line in lines:
            try:
                x.append(float(line.split(" ")[x_col]))
                y.append(float(line.split(" ")[y_col]))
                y_c.append(float(line.split(" ")[y_c_col]))
            except:
                pass;
            lineCount=lineCount+1
        f.close()
        
        for yy in y:
            preAgr = preAgr + yy
        for y_c_y_c in y_c:
            postAgr = postAgr + y_c_y_c
        
        #postAgr = postAgr / lineCount;
        #preAgr = preAgr / lineCount;        

        preAvg = statistics.mean(y);
        postAvg = statistics.mean(y_c)
        sigma = statistics.stdev(y);
        
        return lineCount, sigma, preAvg, postAvg, preAgr, postAgr

    def getPlot(self,file,fileName,x_col=0, y_col=3,y_c_col=3):
        f = open(file)
        lines=f.readlines()        
        x, y, y_c= [], [], []
        for line in lines:
            try:
                x.append(float(line.split(" ")[x_col]))
                y.append(float(line.split(" ")[y_col]))
                y_c.append(float(line.split(" ")[y_c_col]))
            except:
                pass;
        f.close()
        #print(x, y)
        fig = plt.figure()
        #fig = plt.plot(x,y)
        #fName = fileName.split["."][0]
        plt.title(fileName)
        plt.plot(x,y)
        plt.plot(x,y_c)
        plt.xlabel("Frames")
        plt.ylabel("Krippendorff Kappa")
        #plt.show();
        return fig

    def showPlot(self, file, x_col=0, y_col=5):
        f = open(file)
        lines=f.readlines()        
        x, y = [], []
        for line in lines:
            try:
                x.append(float(line.split(" ")[x_col]))
                y.append(float(line.split(" ")[y_col]))
            except:
                pass;
        f.close()
        print(x, y)
        plt.plot(x,y)
        #plt.show()        
    def graphs(self):
        count = 0
        for root, dirs, files in os.walk(self.kay):
            for file in files:
                kappa_file = os.path.join(self.kappa, file)
                self.showPlot(kappa_file)
    
    def verifyOutput(self):
        # get a filename from Kay's set:
        count = 0
        for root, dirs, files in os.walk(self.kay):
            for file in files:
                if("99"  in file):
                    continue
                count=count+1
                out_file = os.path.join(self.outputDir, file)                
                out_lines = []
                with open(out_file) as out_data:
                    for line in out_data:
                        out_lines.append(line.strip()) 
                pass
                global invalid_States
                invalid_States = self.getInvalidStates(out_lines[1:],file) # not the headers
                print("Invalid States",invalid_States);
                invalid_States = {}
    
    def takeAwayAngles(self, lines):
        i =0
        for line in lines:
            x = line.split(" ")
            y = " ".join(x[0:-2])
            lines[i] = y
            i = i + 1
        return lines;
    def poll(self):
        # get a filename from Kay's set:
        count = 0
        for root, dirs, files in os.walk(self.kay):
            for file in files:
                if("99"  in file):
                    continue
                #print(file)
                count=count+1
                kay_file =  os.path.join(self.kay, file)
                ian_file =  os.path.join(self.ian, file)
                #v_file = os.path.join(self.v, file)
                out_file = os.path.join(self.outputDir, file)
                kappa_file = os.path.join(self.kappa, file)
                #match_file = os.path.join(self.match, file)
                
                #print("K:",kay_file,"  I:",ian_file,"   v:",v_file)
                #print("Key:",kay_file[-60:])
                print("\t\t\tFile: ",file)

                kay_lines = []
                with open(kay_file) as kay_data:
                    for line in kay_data:
                        kay_lines.append(line.strip())
                
                ian_lines = []
                with open(ian_file) as ian_data:
                    for line in ian_data:
                        ian_lines.append(line.strip())
                #print("Here")
                #ian_lines = self.takeAwayAngles(ian_lines)
                
                out_lines = []
                kappa_lines = []
                #match_lines = []

                #out_lines.append("Annotation Consensus")
                #kappa_lines.append("Frame Kay Ian Volunteer Nominal Ordinal Interval Ratio Nominal Ordinal Interval Ratio")
                #               0 00000 00000 00000 00000 0 0 0 0
                #match_lines.append("Frame Consensus")

                i = 0                
                for line in kay_lines:

                    line = line.replace("\n","")
                    try:
                        ian_line = ian_lines[i].replace("\n","")
                    except:
                        print("One file is shorter")
                        break
                    
                    #v_line = v_lines[i].replace("\n","")
                    kappaPollRow = self.pollLine_cohen_kappa(line, ian_line,i,DEBUG_INFO=file+" "+str(1))
                    #probsPollRow = self.pollLine_probs(line, ian_line, v_line)
                    #outPollRow = self.majority_voting(line, ian_line, v_line,i)
                    #out_lines.append(outPollRow)
                    kappa_lines.append(kappaPollRow)
                    #match_lines.append(probsPollRow)
                    i=i+1
                #self.save(out_file,out_lines)
                self.save(kappa_file, kappa_lines)
                #self.save(match_file, match_lines)
                
                #global unique_labels
                ##print("\t\t\tuniue",unique_labels);
                unique_labels = {}

                #global invalid_States
                #invalid_States = self.getInvalidStates(out_lines[1:],file) # not the headers
                #print("Invalid States",invalid_States);
                #invalid_States = {}



        print(count,"files processed!")

    def unroll(self):
        # get a filename from Kay's set:
        count = 0
        for root, dirs, files in os.walk(self.pre_kay):
            for file in files:
                if("99"  in file):
                    continue
                #print(file)
                count=count+1
                kay_pre_file =  os.path.join(self.pre_kay, file)
                ian_pre_file =  os.path.join(self.pre_ian, file)

                kay_file =  os.path.join(self.kay, file)
                ian_file =  os.path.join(self.ian, file)

                #v_file = os.path.join(self.v, file)
                out_file = os.path.join(self.outputDir, file)
                kappa_file = os.path.join(self.kappa, file)
                #match_file = os.path.join(self.match, file)
                
                #print("K:",kay_file,"  I:",ian_file,"   v:",v_file)
                #print("Key:",kay_file[-60:])
                print("\t\t\tFile: ",file)

                kay_pre_lines = []
                with open(kay_pre_file) as kay_data:
                    for line in kay_data:
                        splits = line.strip().split(" ")
                        currLine = []
                        currLine.append(int(splits[0]))
                        currLine.append(int(splits[1]))
                        currLine.append(splits[2])
                        kay_pre_lines.append(currLine)
                        #kay_lines.append(line.strip())
                
                ian_pre_lines = []
                with open(ian_pre_file) as ian_data:
                    for line in ian_data:
                        splits = line.strip().split(" ")
                        currLine = []
                        currLine.append(int(splits[0]))
                        currLine.append(int(splits[1]))
                        currLine.append(splits[2])
                        ian_pre_lines.append(currLine)
                        #ian_lines.append(line.strip())
                #print("Here")
                #ian_lines = self.takeAwayAngles(ian_lines)
                #kay_lines = self.tToList(kay_pre_lines)
                #ian_lines = self.tToList(ian_pre_lines)
                
                #self.save(kay_file,kay_lines)
                #self.save(ian_file,ian_lines)



                #print("Lists: ",)



                continue
                v_lines = []
                with open(v_file) as v_data:
                    for line in v_data:
                        v_lines.append(line.strip())
                
                out_lines = []
                kappa_lines = []
                #match_lines = []

                out_lines.append("Annotation Consensus")
                kappa_lines.append("Frame Kay Ian Volunteer Nominal Ordinal Interval Ratio Nominal Ordinal Interval Ratio")
                #               0 00000 00000 00000 00000 0 0 0 0
                #match_lines.append("Frame Consensus")

                i = 0                
                for line in kay_lines:
                    line = line.replace("\n","")
                    ian_line = ian_lines[i].replace("\n","")
                    v_line = v_lines[i].replace("\n","")
                    kappaPollRow = self.pollLine_cohen_kappa(line, ian_line, v_line,i,DEBUG_INFO=file+" "+str(1))
                    #probsPollRow = self.pollLine_probs(line, ian_line, v_line)
                    outPollRow = self.majority_voting(line, ian_line, v_line,i)
                    out_lines.append(outPollRow)
                    kappa_lines.append(kappaPollRow)
                    #match_lines.append(probsPollRow)
                    i=i+1
                self.save(out_file,out_lines)
                self.save(kappa_file, kappa_lines)
                #self.save(match_file, match_lines)
                
                global unique_labels
                print("\t\t\tuniue",unique_labels);
                unique_labels = {}

                global invalid_States
                invalid_States = self.getInvalidStates(out_lines[1:],file) # not the headers
                print("Invalid States",invalid_States);
                invalid_States = {}



        print(count,"files processed!")

    def getInvalidStates(self,out_lines,filename):
        i = 1
        found = False
        for line in out_lines:
            row = line.split(" ")
            if(row[1] == row[2] and row[1]!= "0"):
                print("Right Grasper Same State line:",i," in ",filename)
                found = True
            if(row[3] == row[4] and row[3] != "0"):
                print("Left Grasper Same State line:",i," in ",filename)
                found = True
            i = i + 1
        if(found):
            pass
        else:
            print("OK: ",filename)

    def getListOfInts(self, line):
        stateNums = []
        for state in line:
            stateNums.append(int(state) +1)
        return stateNums
    
    def getListOfInts_no_plus_1_offset(self, line):
        stateNums = []
        for state in line:
            if("G" in state):
                stateNums.append(int(state.replace("G","")))
            else:
                stateNums.append(int(state))
        return stateNums
    
    def lineToStr(self, line):
        l_s = line.replace("\n","").split(" ")
        return "".join(l_s[1:])

    def getK_Kappa(self, arr, type,ZERO_ROW):
        kappa = self.rawK_Kappa(arr, type)
        #if(kappa ==0 & ZERO_ROW):
        #    return " 1.0"
        #else:
        #return " " + "{:.2f}".format(kappa).lstrip('0');  
        return " " + "{:.2f}".format(kappa)
        
    def rawK_Kappa(self, arr, type):
        '''
        res = 0;
        try:
            res = krippendorff.alpha(reliability_data=arr,level_of_measurement=type)
        except:
            pass 
        return res
        '''
        if (arr[0][0] != arr[1][0]):
            return 0.0;
        else:
            return 1.0;
    
    def testZeroRow(self, o_s):
        for o in o_s:
            if( o != 0):
                return False
        return True

    def pollLine_cohen_kappa(self, k_line, i_line, lineNumber, DEBUG=True,DEBUG_INFO="none", ):
        # X_S means array of "S"trings from x's line
        k_s = k_line.split(" ")
        i_s = i_line.split(" ")
        #o_s = k_line.split(" ")
        probs = k_line.split(" ")
        line = ""
        # to do math
        #for i in range (1,len(k_s)):
        #    self.checkUniqueness(k_s[i], i_s[i] ,lineNumber);
            
        #    candidate = self.majority(k_s[i], i_s[i], v_s[i]);
        #    o_s[i] = candidate

        if(DEBUG):
            line = k_s[0] + " " + k_s[1] + " "+ i_s[1]     
            #line = line + " "+self.lineToStr(i_line)+" "
        else:
            line = " ".join(k_s)

        k_n = self.getListOfInts_no_plus_1_offset(k_s[1:])
        i_n = self.getListOfInts_no_plus_1_offset(i_s[1:])
        #o_n = self.getListOfInts_no_plus_1_offset(o_s[1:])
        #arr = [k_n,i_n,v_n]
        arr = k_n, i_n
        #ZERO_ROW = self.testZeroRow(o_n)
        ZERO_ROW = False
        line = line + self.getK_Kappa(arr, "nominal",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "ordinal",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "interval",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "ratio",ZERO_ROW)
        #arr = [k_n,i_n,v_n,o_n]
        #line = line + self.getK_Kappa(arr, "nominal",ZERO_ROW)
        #line = line + self.getK_Kappa(arr, "ordinal",ZERO_ROW)
        #line = line + self.getK_Kappa(arr, "interval",ZERO_ROW)
        #line = line + self.getK_Kappa(arr, "ratio",ZERO_ROW)
       
        return line

    def pollLine_output(self, k_line, i_line, v_line,DEBUG=True):
        k_s = k_line.split(" ")
        i_s = i_line.split(" ")
        v_s = v_line.split(" ")
        o_s = k_line.split(" ")
        probs = k_line.split(" ")
        accepted = 0;
        for i in range (1,len(k_s)):
            try: 
                prob = (int(k_s[i]) + int(i_s[i]) + int(v_s[i])) /3.0;
            except:
                print("Error parsing bit ",i, " in line ", " in file ")
                continue
            prob = (int(k_s[i]) + int(i_s[i]) + int(v_s[i])) /3.0;
            if( prob.is_integer() ):
                probs[i] = str(int(prob))
            else:
                probs[i] = "{:.1f}".format(prob).lstrip('0')
            if( prob >=0.5 ):

                o_s[i] = "1";
            else:
                o_s[i] ="0";  
        line = " ".join(o_s)
        return line
        #line = line +"\t"+ " ".join(probs)       
    def checkUniqueness(self, k, i, v, line):
        global unique_labels
        if( k in unique_labels.keys()):
            pass
        else:
            unique_labels[k] = line;
        if( i in unique_labels.keys()):
            pass
        else:
            unique_labels[i] = line;
        if( v in unique_labels.keys()):
            pass
        else:
            unique_labels[v] = line;

        #print("uniue",unique_labels);        
    def majority(self, k, i, v):
        
        k_n = int(k)
        i_n = int(i)
        v_n = int(v)
        arr = [k_n,i_n,v_n]
        candidate = self.Most_Common(arr);

        return str(int(candidate))
    
    def Most_Common(self, lst):
        data = Counter(lst)
        obj = data.most_common(1)
        return data.most_common(1)[0][0]
        
    def majority_voting(self, k_line, i_line, v_line,lineNumber):     
        k_s = k_line.split(" ")
        i_s = i_line.split(" ")
        v_s = v_line.split(" ")
        o_s = k_line.split(" ") #output
        for i in range (1,len(k_s)):
            self.checkUniqueness(k_s[i], i_s[i], v_s[i],lineNumber);
            candidate = self.majority(k_s[i], i_s[i], v_s[i]);
            o_s[i] = candidate            
        line = " ".join(o_s)
        return line
    
    def pollLine_probs(self, k_line, i_line, v_line):
        k_s = k_line.split(" ")
        i_s = i_line.split(" ")
        v_s = v_line.split(" ")
        o_s = k_line.split(" ")
        probs = k_line.split(" ")
        accepted = 0;

        for i in range (1,len(k_s)):
            try: 
                prob = (int(k_s[i]) + int(i_s[i]) + int(v_s[i])) /3.0;
            except:
                print("Error parsing bit ",i, " in line ", " in file ")
                continue
            prob = (int(k_s[i]) + int(i_s[i]) + int(v_s[i])) /3.0;
            if( prob.is_integer() ):
                probs[i] = str(int(prob))
            else:
                probs[i] = "{:.1f}".format(prob).lstrip('0')
            if( prob >=0.5 ):

                o_s[i] = "1";
            else:
                o_s[i] ="0";  
        line = " ".join(o_s)
        line = line +"\t"+ " ".join(probs)
        return line
    
    def save(self, x_file, x_lines):
        with open(x_file, 'w+') as f:
            for item in x_lines:
                f.write("%s\n" % item)
      
    def k_usage(self, etc=False):
        reliability_data_str = (
        "*    *    *    *    *    3    4    1    2    1    1    3    3    *    3",  # coder A
        "1    *    2    1    3    3    4    3    *    *    *    *    *    *    *",  # coder B
        "*    *    2    1    3    4    4    *    2    1    1    3    3    *    4",  # coder C
        )
        print("\n".join(reliability_data_str))
        print()

        reliability_data = [[np.nan if v == "*" else int(v) for v in coder.split()] for coder in reliability_data_str]

        print("Krippendorff's alpha for nominal metric: ", krippendorff.alpha(reliability_data=reliability_data,
                                                                            level_of_measurement="nominal"))
        print("Krippendorff's alpha for interval metric: ", krippendorff.alpha(reliability_data=reliability_data))
        print()
        print()
        print("From value counts:")
        print()
        value_counts = np.array([[1, 0, 0, 0],
                                [0, 0, 0, 0],
                                [0, 2, 0, 0],
                                [2, 0, 0, 0],
                                [0, 0, 2, 0],
                                [0, 0, 2, 1],
                                [0, 0, 0, 3],
                                [1, 0, 1, 0],
                                [0, 2, 0, 0],
                                [2, 0, 0, 0],
                                [2, 0, 0, 0],
                                [0, 0, 2, 0],
                                [0, 0, 2, 0],
                                [0, 0, 0, 0],
                                [0, 0, 1, 1]])
        print(value_counts)
        print("Krippendorff's alpha for nominal metric: ", krippendorff.alpha(value_counts=value_counts,
                                                                            level_of_measurement="nominal"))
        print("Krippendorff's alpha for interval metric: ", krippendorff.alpha(value_counts=value_counts))

   
main();

