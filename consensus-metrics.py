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
import utils

global unique_labels
unique_labels = {}

global invalid_States
invalid_States = {}


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
    task = "Suturing"
    try:
        task=sys.argv[1]
    except:
        print("Error: no task provided \nUsage: python draw_labels.py <task>")
        
    #I = Iterator(task)
    #I.fixStates()
    #I.poll()
    #I.verifyOutput()
    #I.showAllPlots()
    #I.metrics()
    #setup1()
    setup2()
    
    quit(); 

def setup1():
    dataType = "Context"
    coders = ["Joyce","Sara","Shrisha"]
    tasks = ["Knot_Tying","Suturing","Needle_Passing"]     
    C = ConsensusEngine(dataType, coders, tasks )
    #kappaDirs = C.generateConsensus()

    kappaDirs = ['C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\kappa_output\\Knot_Tying', 'C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\kappa_output\\Suturing', 'C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\kappa_output\\Needle_Passing']
    print(kappaDirs)
    A = AgreementEngine()
    for kdir in kappaDirs:
        A.getAggrementMetricsFromKappa(kdir)
    
def setup2():
    consensusDirs = ['C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\consensus_output\\Knot_Tying', 'C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\consensus_output\\Suturing', 'C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\consensus_output\\Needle_Passing']
    #consensusDirs = ['C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\consensus_output\\Suturing' ]
    
    print(consensusDirs)
    A = AgreementEngine()
    for cdir in consensusDirs:
        A.getAggrementMetricsFromConsensus(cdir)
    

class FileGrabber:
    def __init__(self):
        pass
    
    def getTranscriptLines(self,CWD,dataType,coder,task,trial):
        fPath = os.path.join(CWD, dataType, coder,task,trial)
        self.getTranscriptLinesFile(fPath)

    def unrollContext(self, lines):
        n_lines = []
        start = lines[0].split(" ")[0] 
        start = int(start)
        MAX = lines[-1].split(" ")[0]
        #MAX = int(MAX)
        if(start > 0):
            for j in range(0, start):
                n_lines.append(str(j)+ " 0 0 0 0 0")
        for i in range(0,len(lines)-1):
            n_lines.append(lines[i])
            currentIndex = lines[i].split(" ")[0]
            currentIndex = int(currentIndex)
            nextIndex = lines[i+1].split(" ")[0]
            nextIndex = int(nextIndex)
            for k in range(currentIndex+1,nextIndex):
                n_lines.append(str(k) + " " + " ".join(lines[i].split(" ")[1:] ))        
        n_lines.append(lines[len(lines)-1])
        return n_lines

    def getTranscriptLinesFile(self,file):
        tLines = []
        with open(file) as transcriptData:
            for line in transcriptData:
                tLines.append(line.strip())
        tLinesU = self.unrollContext(tLines)        
        return tLines, tLinesU


    
        


# Agreement metric K Alpha among 2+ annotators
class AgreementEngine:
    def __init__(self):
        pass

    def getAggrementMetricsFromKappa(self,kappaDir):
        fileCount = 0
        pre = 0
        post = 0
        preAggregate = 0
        postAggregate = 0
        allSigma = 0;
        sigmas = []
        lineCount = 0;
        for root, dirs, files in os.walk(kappaDir):
            for file in files:
                if("99" in file):
                    continue 
                kappa_file = os.path.join(kappaDir, file)
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
        print(kappaDir)
        print( "Length:",str(lineCount))
        print( "Pre Unweight:",str( pre / (fileCount+0.0)))
        print( "Post Unweight:",str( post  / (fileCount+0.0)))
        print( "Sigma:",str( sigma2 ))
        print( "Pre Weight:",str( preAggregate / lineCount ))
        print( "Post Weight:",str(  postAggregate / lineCount ))
        return;

    def getAverage(self,file,fileName,x_col=0, y_col=5,y_c_col=9):
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
    
    def getAggrementMetricsFromConsensus(self,cdir):

        F = FileGrabber()        
        sdir = cdir.replace("consensus_output","context_surgeon")
        surgeon_file = ""
        for root, dirs, files in os.walk(sdir):
            for file in files:
                surgeon_file = os.path.join(sdir, file)
        con_file = surgeon_file.replace("context_surgeon","consensus_output")
        cLines,cLinesU = F.getTranscriptLinesFile(con_file)
        sLines,sLinesU = F.getTranscriptLinesFile(surgeon_file)
        y = []
        for i in range(0,min(len(cLinesU),len(sLinesU))):   
            nominalKAlpha = 0
            c_s = cLinesU[i].split(" ")
            s_s = sLinesU[i].split(" ")

            c_n = [int(state) for state in c_s[1:]]
            s_n = [int(state) for state in s_s[1:]]

            arr = [c_n,s_n]
            ZERO_ROW = self.testZeroRow(c_n) or self.testZeroRow(s_n)
            y.append(float(self.getK_Kappa(arr, "nominal",ZERO_ROW)))
            #print(cLinesU[i],sLinesU[i],str(float(self.getK_Kappa(arr, "nominal",ZERO_ROW))))
        preAvg = statistics.mean(y);
        sigma = statistics.stdev(y);
        print(cdir)
        print( "Length:",str(len(cLines)),str(len(cLinesU)))
        print( "Pre Unweight\Weight:",str( preAvg))
        print( "Sigma:",str( sigma ))




    def testZeroRow(self, o_s):
        for o in o_s:
            if( o != 0):
                return False
        return True

    def getK_Kappa(self, arr, type,ZERO_ROW):
        kappa = self.rawK_Kappa(arr, type)
        if(kappa ==0 & ZERO_ROW): # it returns 0 when all coders say '00000'
            return " 1.0"
        else:
            return " " + "{:.2f}".format(kappa).lstrip('0');
    def rawK_Kappa(self, arr, type):
        res = 0;
        try:
            res = krippendorff.alpha(reliability_data=arr,level_of_measurement=type)
        except:
            pass 
        return res


        

# Combine transcripts from annotators into one consensus transcript
class ConsensusEngine:
    def __init__(self,  dataType, coders, tasks):  
        self.CWD = os.path.dirname(os.path.realpath(__file__))    
        self.dataType = dataType
        self.coders = coders
        self.tasks = tasks

    def generateConsensusFor2(self):
        F = FileGrabber()
        kappaDirs = []
        kappaDir = ""
        for task in self.tasks:
            print("task:",task)
            for trial in os.listdir(os.path.join(self.CWD,self.dataType,"Joyce",task)):
                print("\ttrial",trial)
                allTranscriptLines = []
                allTranscriptULines = []
                out_lines = []
                kappa_lines = []
                for coder in self.coders:
                    print("\t\tcoder:",coder)
                    tLines, tLinesU = F.getTranscriptLines(self.CWD, self.dataType, coder, task, trial) 
                    allTranscriptLines.append(tLines)
                    allTranscriptULines.append(tLinesU)

                for lineIndex in range(0,len(allTranscriptULines[0])):
                    tSingleFrame = []
                    for coderIndex in range(0,len(self.coders)):
                        line = allTranscriptULines[coderIndex][lineIndex].replace("\n","")
                        tSingleFrame.append(line)

                    kappaPollRow = self.pollLine_cohen_kappa(tSingleFrame[0], tSingleFrame[1], tSingleFrame[2],lineIndex,DEBUG_INFO="file"+" "+str(1))
                    outPollRow = self.majority_voting(tSingleFrame[0], tSingleFrame[1], tSingleFrame[2],lineIndex)
                    out_lines.append(outPollRow)
                    kappa_lines.append(kappaPollRow)
                print("\t\t\t\t#",len(allTranscriptULines[0]))
                kappaFname = os.path.join(self.CWD,"kappa_output",task,trial)
                outFname = os.path.join(self.CWD,"consensus_output",task,trial)

                kappaFnamedir = os.path.abspath(kappaFname + "/../")
                if(not os.path.isdir(kappaFnamedir)):
                    path = pathlib.Path(kappaFnamedir)
                    path.mkdir(parents=True, exist_ok=True)  

                outFnamedir = os.path.abspath(outFname + "/../")
                if(not os.path.isdir(outFnamedir)):
                    path = pathlib.Path(outFnamedir)
                    path.mkdir(parents=True, exist_ok=True)  
                kappaDir = kappaFnamedir

                utils.save(kappaFname,kappa_lines)  
                utils.save(outFname,out_lines)    
            kappaDirs.append(kappaDir)
        return kappaDirs

    def generateConsensus(self):
        F = FileGrabber()
        kappaDirs = []
        kappaDir = ""
        for task in self.tasks:
            print("task:",task)
            for trial in os.listdir(os.path.join(self.CWD,self.dataType,"Joyce",task)):
                print("\ttrial",trial)
                allTranscriptLines = []
                allTranscriptULines = []
                out_lines = []
                kappa_lines = []
                for coder in self.coders:
                    print("\t\tcoder:",coder)
                    tLines, tLinesU = F.getTranscriptLines(self.CWD, self.dataType, coder, task, trial) 
                    allTranscriptLines.append(tLines)
                    allTranscriptULines.append(tLinesU)

                for lineIndex in range(0,len(allTranscriptULines[0])):
                    tSingleFrame = []
                    for coderIndex in range(0,len(self.coders)):
                        line = allTranscriptULines[coderIndex][lineIndex].replace("\n","")
                        tSingleFrame.append(line)

                    kappaPollRow = self.pollLine_cohen_kappa(tSingleFrame[0], tSingleFrame[1], tSingleFrame[2],lineIndex,DEBUG_INFO="file"+" "+str(1))
                    outPollRow = self.majority_voting(tSingleFrame[0], tSingleFrame[1], tSingleFrame[2],lineIndex)
                    out_lines.append(outPollRow)
                    kappa_lines.append(kappaPollRow)
                print("\t\t\t\t#",len(allTranscriptULines[0]))
                kappaFname = os.path.join(self.CWD,"kappa_output",task,trial)
                outFname = os.path.join(self.CWD,"consensus_output",task,trial)

                kappaFnamedir = os.path.abspath(kappaFname + "/../")
                if(not os.path.isdir(kappaFnamedir)):
                    path = pathlib.Path(kappaFnamedir)
                    path.mkdir(parents=True, exist_ok=True)  

                outFnamedir = os.path.abspath(outFname + "/../")
                if(not os.path.isdir(outFnamedir)):
                    path = pathlib.Path(outFnamedir)
                    path.mkdir(parents=True, exist_ok=True)  
                kappaDir = kappaFnamedir

                utils.save(kappaFname,kappa_lines)  
                utils.save(outFname,out_lines)    
            kappaDirs.append(kappaDir)
        return kappaDirs

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

    def pollLine_cohen_kappa(self, k_line, i_line, v_line,lineNumber, DEBUG=True,DEBUG_INFO="none", ):
        # X_S means array of "S"trings from x's line
        k_s = k_line.split(" ")
        i_s = i_line.split(" ")
        v_s = v_line.split(" ")
        o_s = k_line.split(" ")
        probs = k_line.split(" ")
        line = ""
        # to do math
        for i in range (1,len(k_s)):
            self.checkUniqueness(k_s[i], i_s[i], v_s[i],lineNumber);
            
            candidate = self.majority(k_s[i], i_s[i], v_s[i]);
            o_s[i] = candidate

        if(DEBUG):
            line = k_s[0] + " " + "".join(k_s[1:])            
            line = line + " "+self.lineToStr(i_line)+" "+self.lineToStr(v_line)+" "+"".join(o_s[1:])      #+ str(res)
        else:
            line = " ".join(k_s)

        k_n = self.getListOfInts_no_plus_1_offset(k_s[1:])
        i_n = self.getListOfInts_no_plus_1_offset(i_s[1:])
        v_n = self.getListOfInts_no_plus_1_offset(v_s[1:])
        o_n = self.getListOfInts_no_plus_1_offset(o_s[1:])
        arr = [k_n,i_n,v_n]
        ZERO_ROW = self.testZeroRow(o_n)
        line = line + self.getK_Kappa(arr, "nominal",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "ordinal",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "interval",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "ratio",ZERO_ROW)
        arr = [k_n,i_n,v_n,o_n]
        line = line + self.getK_Kappa(arr, "nominal",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "ordinal",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "interval",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "ratio",ZERO_ROW)
       
        return line

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

    def getListOfInts_no_plus_1_offset(self, line):
        stateNums = []
        for state in line:
            stateNums.append(int(state))
        return stateNums

    def getK_Kappa(self, arr, type,ZERO_ROW):
        kappa = self.rawK_Kappa(arr, type)
        if(kappa ==0 & ZERO_ROW): # it returns 0 when all coders say '00000'
            return " 1.0"
        else:
            return " " + "{:.2f}".format(kappa).lstrip('0');  

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

    def rawK_Kappa(self, arr, type):
        res = 0;
        try:
            res = krippendorff.alpha(reliability_data=arr,level_of_measurement=type)
        except:
            pass 
        return res
        

    def testZeroRow(self, o_s):
        for o in o_s:
            if( o != 0):
                return False
        return True

    def lineToStr(self, line):
        l_s = line.replace("\n","").split(" ")
        return "".join(l_s[1:])


main();