from asyncio import Task
from genericpath import isfile
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
from sklearn import metrics
import textdistance

global unique_labels
unique_labels = {}

global MPid
MPid = 0

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
    LABEL_TYPE = "MP"
    SUBJECT = "Surgeon"
    try:
        #task=sys.argv[1]
        LABEL_TYPE=sys.argv[1]
        SUBJECT=sys.argv[2]
    except:
        print("Error: no task provided \nUsage: python consensus-metrics.py <LABEL_TYPE:Gestures | MP | Context> <SUBJECT:Surgeon| All | Trial [1,2,3] >")

      
    #I = Iterator(task)
    #I.fixStates()
    #I.poll()
    #I.verifyOutput()
    #I.showAllPlots()
    #I.metrics()
    
    #setup1()
    #setupGestures()
    #setupMP()

    #setupUniqueCompGestures()


    
    #setupUniqueCompMP()  
    #setupUniqueCompMPForCoder()
    #setupUniqueCompGestureForCoder()

    #setupContextCoderwise()

    if LABEL_TYPE == "Gestures":
        setupUniqueCompGestureForCoder()
    elif LABEL_TYPE == "MP":
        if SUBJECT == "All":
            setupUniqueCompMP()
        else:
            #trial
            setupUniqueCompMPForCoder(SUBJECT)    
    elif LABEL_TYPE == "Context":
        setupContextCoderwise()
    
    quit(); 

def getUniqueIndex(s):
    global MPid
    global unique_labels
    


    if s in unique_labels.keys():
        return unique_labels[s]
    else:
        unique_labels[s] = MPid
        MPid+=1
        return unique_labels[s]

def setup1():
    dataType = "Context Labels"
    coders = ["Trial 1","Trial 2","Trial 3"]
    tasks = ["Knot_Tying","Suturing","Needle_Passing"]     
    C = ConsensusEngine(dataType,coders, tasks)
    kappaDirs = C.generateConsensus()

    #kappaDirs = ['C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\kappa_output\\Knot_Tying', 'C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\kappa_output\\Suturing', 'C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\kappa_output\\Needle_Passing']
    print("kappaDirs:",kappaDirs)
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

def setupContextCoderwise():
    '''
    Test in which:
        We compare individual context labels to Surgeon context labels 
    '''
    dataTypeA = "Context Labels"
    coders=" --- "
    coder = "Trial 1"
    dataTypeB = "Context_Surgeon" # contains the static files (uncombined LR)
    tasks = ["Knot_Tying","Suturing","Needle_Passing"]     
    C = ConsensusEngine(dataTypeA,coders, tasks, dataTypeB)
    C.nominalAgreementCoderContext(coder)


def setupGestures():
    dataType = "Gesture Labels"
    coders = ["Trial 1","Trial 2","Trial 3"]
    tasks = ["Knot_Tying","Suturing","Needle_Passing"]     
    C = ConsensusEngine(dataType,coders, tasks)
    kappaDirs = C.generateConsensusGestures()


def setupUniqueCompGestures():
    '''
    Tets in which:
        We compare two transcripts with gestures, MPs or anything that we use an unique ID to identify (for K alpha)

    '''
    dataTypeA = "gesture_consensus_output"
    coders=" --- "
    dataTypeB = "GT Gestures"
    #tasks = ["Knot_Tying","Suturing","Needle_Passing"]   
    tasks = ["Suturing"]
    C = ConsensusEngine(dataTypeA,coders, tasks, dataTypeB)
    C.nominalAgreement()


def setupUniqueCompMP():
    '''
    Test in which
        we compare MP consensus to MP Context translation - All coders

    '''
    dataTypeA = "MP_consensus_output"
    coders=" --- "
    dataTypeB = "MP_Context_Consensus" # contains the static files (uncombined LR)
    tasks = ["Knot_Tying","Suturing","Needle_Passing"]     
    C = ConsensusEngine(dataTypeA,coders, tasks, dataTypeB)
    C.nominalAgreement()

def setupUniqueCompMPForCoder(SUBJECT=""):
    '''
    Test in which:
        We compare individual MP labels to translated MP labels

    '''
    dataTypeA = "MP Labels"
    coders=" --- "
    if SUBJECT != "":
        coder = SUBJECT #default
    else:
        coder = "Trial 1" #default
    dataTypeB = "MP_Context" # contains the static files (uncombined LR)
    tasks = ["Knot_Tying","Suturing","Needle_Passing"]     
    C = ConsensusEngine(dataTypeA,coders, tasks, dataTypeB)
    C.nominalAgreementCoder(coder)

def setupUniqueCompGestureForCoder():
    '''
    Test in which:
        We compare individual gesture labels to JIGSAWS GT gestures 
    '''
    dataTypeA = "Gesture Labels"
    coders=" --- "
    coder = "Trial 2"
    dataTypeB = "GT Gestures" # contains the static files (uncombined LR)
    tasks = ["Knot_Tying","Suturing","Needle_Passing"]     
    C = ConsensusEngine(dataTypeA,coders, tasks, dataTypeB)
    C.nominalAgreementCoder(coder)


def setupMP():
    dataType = "MP Labels"
    coders = ["Trial 1","Trial 2","Trial 3"]
    tasks = ["Knot_Tying","Suturing","Needle_Passing"]     
    C = ConsensusEngine(dataType,coders, tasks)
    kappaDirs = C.generateConsensusMP()
    
    #kappaDirs = ['C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\kappa_output\\Knot_Tying', 'C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\kappa_output\\Suturing', 'C:\\Users\\ianre\\Desktop\\coda\\consensus-agreement-main\\kappa_output\\Needle_Passing']
    #print("kappaDirs:",kappaDirs)
    #A = AgreementEngine()
    #for kdir in kappaDirs:
    #    A.getAggrementMetricsFromKappa(kdir)

class FileGrabber:
    def __init__(self):
        pass
    
    def getTranscriptLines(self,CWD,dataType,coder,task,trial):
        fPath = os.path.join(CWD,task, dataType, coder,trial)
        self.getTranscriptLinesFile(fPath)

    def getMPLines(self,CWD,dataType,coder,task,trial):
        fPath = os.path.join(CWD,task, dataType, coder,trial)
        return self.getMPLinesFile(fPath)

    def getGestureLines(self,CWD,dataType,coder,task,trial):
        fPath = os.path.join(CWD,task, dataType, coder,trial)
        return self.getGestureLinesFile(fPath)

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

    def unrollGestures(self, lines):
        # Input: ["Start End Gesture",...]
        # Outout: ["Start Gesture", "Start+1 Gesture", ... "End Gesture",]
        '''
        n_lines = []
        start = lines[0].split(" ")[0] 
        end = lines[0].split(" ")[1]
        defaultGesture = lines[0].split(" ")[2]
        start = int(start)
        end = int(end)
        MAX = lines[-1].split(" ")[1]
        MAX = int(MAX)

        if(start > 0):
            for j in range(0, start):
                n_lines.append(str(j)+ " " + defaultGesture) #! here
        
        for i in range(start,len(lines)-1):
            n_lines.append(lines[i])
            currentIndex = lines[i].split(" ")[0]
            currentIndex = int(currentIndex)
            nextIndex = lines[i+1].split(" ")[0]
            nextIndex = int(nextIndex)
            for k in range(currentIndex+1,nextIndex):
                n_lines.append(str(k) + " " + " ".join(lines[i].split(" ")[1:] ))        
        n_lines.append(lines[len(lines)-1])
        return n_lines
        '''
        currentIndex = 0
        newLines = []
        for line in lines:
            split = line.split(" ")
            if len(split) < 2: 
                continue
            start = int(split[0])
            end = int(split[1])
            gesture = split[2]
            while currentIndex <= end:
                newLines.append(str(currentIndex)+ " " + gesture)
                currentIndex+=1        
        return newLines

    def unrollMP(self, lines):
        currentIndex = 0
        newLines = []
        for line in lines:
            split = line.split(" ")
            if len(split) < 2: 
                continue
            start = int(split[0])
            end = int(split[1])
            gesture = " ".join(split[2:])
            while currentIndex <= end:
                newLines.append(str(currentIndex)+ " " + gesture)
                currentIndex+=1        
        return newLines

    def getGestureLinesFile(self,file): 
        tLines = []
        with open(file) as transcriptData:
            for line in transcriptData:
                tLines.append(line.strip())
        tLinesU = self.unrollGestures(tLines)        
        return tLines, tLinesU

    def getMPLinesFile(self,file): 
        tLines = []
        with open(file) as transcriptData:
            for line in transcriptData:
                tLines.append(line.strip())
        tLinesU = self.unrollMP(tLines)        
        return tLines, tLinesU

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
    def __init__(self,  dataType, coders, tasks,dataTypeB=""):  
        self.CWD = os.path.dirname(os.path.realpath(__file__))    
        self.dataType = dataType
        self.coders = coders
        self.tasks = tasks
        self.dataTypeB = dataTypeB
        self.dataTypeA = dataType

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


    def nominalAgreementCoderContext(self, coder, ):
        global unique_labels
        global MPid
        F = FileGrabber()
        kappaDirs = []
        kappaDir = ""
        print("################################## Starting: context nominalAgreement for Coder", coder, self.dataTypeA, " : ",self.dataTypeB )

        for task in self.tasks:
            print("\nTask:",task)
            trialResults = []
            trialLengths = []
            trialEDistance = 0
            trialEDitScore = 0
        
            for trial in os.listdir(os.path.join(self.CWD,task,self.dataTypeA, coder)):
                print("\ttrial",trial) 
                file_a = os.path.join(self.CWD, task, self.dataTypeA, coder , trial)
                file_b = os.path.join(self.CWD, task, self.dataTypeB, trial)
                if not os.path.isfile(file_b):
                    continue

                _ , lines_a  = F.getTranscriptLinesFile(file_a)
                _ , lines_b  = F.getTranscriptLinesFile(file_b) 


                y = []
                trialLength = min(len(lines_a),len(lines_b)) 
                maxLen = max(len(lines_a),len(lines_b)) 
                correctlabels = 0
                totalLabels = 0
                k_string=[]
                i_string=[]
                for i in range(0,trialLength):   
                    nominalKAlpha = 0
                    c_s = lines_a[i].split(" ")
                    s_s = lines_b[i].split(" ")

                    c_n = [state for state in c_s[1:]]
                    s_n = [state for state in s_s[1:]]


                    if "".join(c_n) == "".join(s_n):
                        correctlabels+=1
                    totalLabels+=1
                    k_string.append("".join(c_n))
                    i_string.append("".join(s_n))


                    c_n = [int(state) for state in c_s[1:]]
                    s_n = [int(state) for state in s_s[1:]]

                    arr = [c_n,s_n]


                    '''
                    for stateIndex in range(0,len(c_n)):
                        if c_n[stateIndex] == s_n[stateIndex]:
                            correctlabels+=1
                        totalLabels+=1
                        k_string.append(str(c_n[stateIndex]))
                        i_string.append(str(s_n[stateIndex]))
                    '''
                    
                 
                    ZERO_ROW = self.testZeroRow(c_n) or self.testZeroRow(s_n)
                    y.append(float(self.getK_Kappa(arr, "nominal",ZERO_ROW)))
                    #print(lines_a[i],lines_b[i],str(float(self.getK_Kappa(arr, "nominal",ZERO_ROW))))
                
                                
                trialEDistance = textdistance.levenshtein.distance(i_string, k_string)
                trialEDitScore = (1-(trialEDistance/totalLabels))*100  
                trialAccuracy = correctlabels/totalLabels

                preAvg = statistics.mean(y);
                sigma = statistics.stdev(y);
                #print(cdir)
                print( "Length:",trialLength,"/",maxLen)
                print( "Pre Unweight\Weight:",str(preAvg))
                print( "Sigma:",str( sigma ))
                print("\t\t\tAccuracy:",trialAccuracy)
                print("\t\t\tEdistance\score:",trialEDistance,"\\\\\\",trialEDitScore)

                trialLengths.append(trialLength)
                trialResults.append(preAvg)


            print("Summary for "+task)
            print("Average K alpha unweighted %f",statistics.mean(trialResults))
            taskLength = sum(trialLengths)
            print("sum of actualLengths in task:",taskLength)
            crazylistcomp = [ (trialLengths[i]/taskLength)* trialResults[i] for i in range(0,len(trialLengths))] 
            print("Average K alpha weighted   %f",sum( crazylistcomp ))


    def nominalAgreementCoder(self, coder, ):
        global unique_labels
        global MPid
        F = FileGrabber()
        kappaDirs = []
        kappaDir = ""
        print("################################## Starting: nominalAgreement for Coder ", coder, self.dataTypeA, " : ",self.dataTypeB )

        for task in self.tasks:
            print("\nTask:",task)
            trialResults = []
            trialAccuracies = []
            trialLengths = []
            trialEDistScoresK = []
            trialEDistScoresI = []
            trialEDistScores = []
            maxLengthTask = 0

            for trial in os.listdir(os.path.join(self.CWD,task,self.dataTypeA, coder)):

                print("\ttrial",trial)
                
                
                file_a = os.path.join(self.CWD, task, self.dataTypeA, coder , trial)
                file_b = os.path.join(self.CWD, task, self.dataTypeB, coder , trial)
                _ , lines_a  = F.getMPLinesFile(file_a) 
                _ , lines_b  = F.getMPLinesFile(file_b) 


                MP_act = []
                MP_sub = []
                MP_obj = []
                minLen = min(len(lines_a),len(lines_b))

                if(True): # MP comp
                    for i in range(0,minLen):
                        line_a = lines_a[i].replace("\n","").strip()     
                        line_a = line_a.replace("Left","L").replace("Right","R")
                        line_a_s = line_a.split(" ")

                        MP_act.append(line_a_s[1].split("(")[0])
                        MP_obj.append(line_a_s[2].split(")")[0])
                        
                        if "LR" in line_a:
                            lineNumber = line_a_s[0]
                            line_a = " ".join([lineNumber,line_a_s[1].replace("LR","L"),line_a_s[2],line_a_s[1].replace("LR","R"),line_a_s[2] ])
                        
                        lines_a[i] = line_a


                    for i in range(0,minLen):
                        line_b = lines_b[i].replace("\n","")
                        #line_b = line_b.replace("Left","L").replace("Right","R")
                        try:
                            if( MP_act[i] in  line_b and MP_obj[i] in line_b):
                                lines_b[i] = lines_a[i]
                        except Exception as e:
                            #print("well")
                            pass

                k_ints = []
                i_ints = []
                actualLength = 0
                maxLength = max([len(lines_a),len(lines_b)])
                
                for lineIndex in range(0,minLen):
                    tSingleFrame = []
                    line_a = lines_a[lineIndex].replace("\n","").strip()  
                    line_b = lines_b[lineIndex].replace("\n","").strip()   
                    
                    tSingleFrame.append(line_a)
                    tSingleFrame.append(line_b)

                    if len(tSingleFrame) < 2:
                        break
                    #kappaPollRow, candidate = self.pollLine_cohen_kappa_gesture(tSingleFrame[0], tSingleFrame[1], tSingleFrame[2],lineIndex,DEBUG_INFO="file"+" "+str(1))
                    k_id  =  getUniqueIndex( " ".join(tSingleFrame[0].split(" ")[1:]))
                    k_gest = int(k_id)
                    i_id  =  getUniqueIndex( " ".join(tSingleFrame[1].split(" ")[1:]))
                    i_gest = int(i_id)                    

                    k_ints.append(k_gest)
                    i_ints.append(i_gest)
                    
                    actualLength+=1


                arr = [k_ints,i_ints]
                correctlabels = 0
                totalLabels = 0

                k_string = []
                i_string = []
                for lineIndex in range(0,minLen):
                    if k_ints[lineIndex] == i_ints[lineIndex]:
                        correctlabels+=1
                    totalLabels+=1
                    k_string.append(str(k_ints[lineIndex]))
                    i_string.append(str(i_ints[lineIndex]))
                    trialEDistScoresK.append(str(k_ints[lineIndex]))
                    trialEDistScoresI.append(str(i_ints[lineIndex]))
                #trialEDistance=0
                trialEDistance = textdistance.levenshtein.distance(i_string, k_string)
                trialEDitScore = (1-(trialEDistance/maxLength))*100
                maxLengthTask+=maxLength

                trialAccuracy = correctlabels/totalLabels
                trialAccuracies.append(trialAccuracy)
                trialEDistScores.append(trialEDitScore)
                results = self.getK_Kappa(arr, "nominal",False)

                kappa = self.rawK_Kappa(arr, "nominal")

                print("\t\t\tKA:",results,",",kappa)
                print("\t\t\tAccuracy:",trialAccuracy)
                print("\t\t\tEdistance\score:",trialEDistance,"\\\\\\",trialEDitScore)
                trialResults.append(kappa)
                trialLengths.append(actualLength)

                print("\t\t\t\t#",str(actualLength)+"/"+str(maxLength))
                MPid = 0 
                unique_labels = {}

            print("Summary for "+task)
            print("Average K alpha unweighted %f",statistics.mean(trialResults))
            taskLength = sum(trialLengths)
            print("sum of actualLengths in task:",taskLength)
            crazylistcomp = [ (trialLengths[i]/taskLength)* trialResults[i] for i in range(0,len(trialLengths))] 
            print("Average K alpha weighted   %f",sum( crazylistcomp ))
            print("Average Accuracy   %f",statistics.mean(trialAccuracies))
            kappaDirs.append(kappaDir)
            
            taskEDistance=0
            #taskEDistance = textdistance.levenshtein.distance(trialEDistScoresI, trialEDistScoresK)
            taskEDitScore = (1-(taskEDistance/maxLengthTask))*100

            print("Average EditScore   %f",statistics.mean(trialEDistScores))
            print("Final EditScore   %f",taskEDitScore)

        
        return kappaDirs


    def nominalAgreement(self):
        global unique_labels
        global MPid
        F = FileGrabber()
        kappaDirs = []
        kappaDir = ""
        print("################################## Starting: nominalAgreement ", self.dataTypeA, " : ",self.dataTypeB )

        for task in self.tasks:
            print("\nTask:",task)
            trialResults = []
            trialLengths = []
            trialExtraResults = []
            trialAccuracies = []
            trialEDistScoresK = []
            trialEDistScoresI = []
            trialEDistScores = []
            maxLengthTask = 0
            for trial in os.listdir(os.path.join(self.CWD,task,self.dataTypeA)):
                #if "Knot_Tying_S09_T05" in trial or "Knot_Tying_S09_T05" in trial or "Knot_Tying_S09_T05" in trial:
                #    print("\ttrial",trial)
                #else:
                #    continue
                
                
                file_a = os.path.join(self.CWD, task, self.dataTypeA , trial)
                file_b = os.path.join(self.CWD, task, self.dataTypeB , trial)
                _ , lines_a  = F.getMPLinesFile(file_a) 
                _ , lines_b  = F.getMPLinesFile(file_b) 

                k_ints = []
                i_ints = []
                actualLength = 0
                maxLength = max([len(lines_a),len(lines_b)])
                minLen = min(len(lines_a),len(lines_b))
                
                MP_act = []
                MP_sub = []
                MP_obj = []
                
                for i in range(0,minLen):
                    line_a = lines_a[i].replace("\n","").strip()     
                    line_a = line_a.replace("Left","L").replace("Right","R")
                    line_a_s = line_a.split(" ")

                    MP_act.append(line_a_s[1].split("(")[0])
                    MP_obj.append(line_a_s[2].split(")")[0])
                    
                    if "LR" in line_a:
                        lineNumber = line_a_s[0]
                        line_a = " ".join([lineNumber,line_a_s[1].replace("LR","L"),line_a_s[2],line_a_s[1].replace("LR","R"),line_a_s[2] ])
                    
                    
                    
                    
                    lines_a[i] = line_a

                for i in range(0,minLen):
                    line_b = lines_b[i].replace("\n","")
                    #line_b = line_b.replace("Left","L").replace("Right","R")
                    try:
                        if( MP_act[i] in  line_b and MP_obj[i] in line_b):
                            lines_b[i] = lines_a[i]
                    except Exception as e:
                        #print("well")
                        pass
                
                
                for lineIndex in range(0,min(len(lines_a),len(lines_b))):
                    tSingleFrame = []
                    line_a = lines_a[lineIndex].replace("\n","").strip()      
                    line_b = lines_b[lineIndex].replace("\n","").strip()                     
                    tSingleFrame.append(line_a)
                    tSingleFrame.append(line_b)

                    if len(tSingleFrame) < 2:
                        break
                    #kappaPollRow, candidate = self.pollLine_cohen_kappa_gesture(tSingleFrame[0], tSingleFrame[1], tSingleFrame[2],lineIndex,DEBUG_INFO="file"+" "+str(1))
                    k_id  =  getUniqueIndex( " ".join(tSingleFrame[0].split(" ")[1:]))
                    k_gest = int(k_id)
                    i_id  =  getUniqueIndex( " ".join(tSingleFrame[1].split(" ")[1:]))
                    i_gest = int(i_id)                    

                    k_ints.append(k_gest)
                    i_ints.append(i_gest)
                    
                    actualLength+=1


                arr = [k_ints,i_ints]

                correctlabels = 0
                totalLabels = 0
                
                k_string = []
                i_string = []
                for lineIndex in range(0,minLen):
                    if k_ints[lineIndex] == i_ints[lineIndex]:
                        correctlabels+=1
                    totalLabels+=1
                    k_string.append(str(k_ints[lineIndex]))
                    i_string.append(str(i_ints[lineIndex]))
                    trialEDistScoresK.append(str(k_ints[lineIndex]))
                    trialEDistScoresI.append(str(i_ints[lineIndex]))
                trialEDistance = textdistance.levenshtein.distance(i_string, k_string)
                trialEDitScore = (1-(trialEDistance/maxLength))*100
                maxLengthTask+=maxLength
                trialAccuracy = correctlabels/totalLabels
                trialAccuracies.append(trialAccuracy)
                trialEDistScores.append(trialEDitScore)

                results = self.getK_Kappa(arr, "nominal",False)
                resultsMiroIOU = metrics.jaccard_score(k_ints, i_ints, labels=None, pos_label=1, average='micro', sample_weight=None, zero_division='warn') 

                kappa = self.rawK_Kappa(arr, "nominal")

                print("\t\t\tKA:",results,",",kappa, "IOU", resultsMiroIOU)
                print("\t\t\tAccuracy:",trialAccuracy)
                print("\t\t\tEdistance\score:",trialEDistance,"\\\\\\",trialEDitScore)
                trialResults.append(kappa)
                trialExtraResults.append(resultsMiroIOU)
                trialLengths.append(actualLength)

                print("\t\t\t\t#",str(actualLength)+"/"+str(maxLength))
                kappaFname = os.path.join(self.CWD,task,"MP_kappa_output",trial)
                outFname = os.path.join(self.CWD,task,"MP_consensus_output",trial)

                kappaFnamedir = os.path.abspath(kappaFname + "/../")
                if(not os.path.isdir(kappaFnamedir)):
                    path = pathlib.Path(kappaFnamedir)
                    path.mkdir(parents=True, exist_ok=True)  

                outFnamedir = os.path.abspath(outFname + "/../")
                if(not os.path.isdir(outFnamedir)):
                    path = pathlib.Path(outFnamedir)
                    path.mkdir(parents=True, exist_ok=True)  
                kappaDir = kappaFnamedir
                #out_lines = self.MPCompact(out_lines)
                #utils.save(kappaFname,kappa_lines)  
                #utils.save(outFname,out_lines)                
                MPid = 0 
                #global unique_labels 
                unique_labels = {}

            print("Summary for "+task)
            print("Average K alpha unweighted %f",statistics.mean(trialResults))
            taskLength = sum(trialLengths)
            print("sum of actualLengths in task:",taskLength)
            crazylistcomp = [ (trialLengths[i]/taskLength)* trialResults[i] for i in range(0,len(trialLengths))] 
            print("Average K alpha weighted   %f",sum( crazylistcomp ))
            kappaDirs.append(kappaDir)
            print("Average IOU %f",statistics.mean(trialExtraResults))
            print("Average Accuracy   %f",statistics.mean(trialAccuracies))

            taskEDistance = textdistance.levenshtein.distance(trialEDistScoresI, trialEDistScoresK)
            taskEDitScore = (1-(taskEDistance/maxLengthTask))*100

            print("Average EditScore   %f",statistics.mean(trialEDistScores))
            print("Final EditScore   %f",taskEDitScore)
            

        
        return kappaDirs


    def generateConsensusMP(self):
        global unique_labels
        global MPid
        F = FileGrabber()
        kappaDirs = []
        kappaDir = ""

        for task in self.tasks:
            print("\nTask:",task)
            trialResults = []
            trialLengths = []
            for trial in os.listdir(os.path.join(self.CWD,task,self.dataType,self.coders[0])):
                print("\ttrial",trial)
                allTranscriptULines = []
                out_lines = []
                kappa_lines = []
                for coder in self.coders:
                    print("\t\tcoder:",coder)
                    tLines, tLinesU = F.getMPLines(self.CWD, self.dataType, coder, task, trial) 
                    #allTranscriptLines.append(tLines)
                    allTranscriptULines.append(tLinesU)
                k_ints = []
                i_ints = []
                v_ints = []
                actualLength = 0
                maxLength = max([len(allTranscriptULines[0]),len(allTranscriptULines[1]),len(allTranscriptULines[2])])
                
                for lineIndex in range(0,len(allTranscriptULines[0])):
                    tSingleFrame = []
                    for coderIndex in range(0,len(self.coders)):
                        try:
                            line = allTranscriptULines[coderIndex][lineIndex].replace("\n","")                            
                            tSingleFrame.append(line)
                        except Exception as e:
                            break
                    if len(tSingleFrame) < 3:
                        break
                    #kappaPollRow, candidate = self.pollLine_cohen_kappa_gesture(tSingleFrame[0], tSingleFrame[1], tSingleFrame[2],lineIndex,DEBUG_INFO="file"+" "+str(1))
                    k_id  =  getUniqueIndex( " ".join(tSingleFrame[0].split(" ")[1:]))
                    k_gest = int(k_id)
                    i_id  =  getUniqueIndex( " ".join(tSingleFrame[1].split(" ")[1:]))
                    i_gest = int(i_id)
                    v_id  =  getUniqueIndex( " ".join(tSingleFrame[2].split(" ")[1:]))
                    v_gest = int(v_id)

                    k_ints.append(k_gest)
                    i_ints.append(i_gest)
                    v_ints.append(v_gest)
                    candidate = self.majority(k_gest, i_gest, v_gest)
                    MPcandidate = ""
                    for MPstring, id in unique_labels.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
                        if id == int(candidate):
                            MPcandidate = MPstring
                    #outPollRow = self.majority_voting_gesture(tSingleFrame[0], tSingleFrame[1], tSingleFrame[2],lineIndex)
                    outPollRow = str(lineIndex) + " " + MPcandidate
                    out_lines.append(outPollRow)
                    kappa_lines.append(str(lineIndex) + " "+" ".join(tSingleFrame[0].split(" ")[1:]) + ":"+str(k_gest)+"\t"+ " ".join(tSingleFrame[1].split(" ")[1:])+ ":"+str(i_gest)+"\t"+" ".join(tSingleFrame[2].split(" ")[1:])+ ":"+str(v_gest)+"\t"+ " ->"+MPcandidate)
                    actualLength+=1


                arr = [k_ints,i_ints,v_ints]
                results = self.getK_Kappa(arr, "nominal",False)

                kappa = self.rawK_Kappa(arr, "nominal")

                print("\t\t\tKA:",results,",",kappa)
                trialResults.append(kappa)
                trialLengths.append(actualLength)

                print("\t\t\t\t#",str(actualLength)+"/"+str(maxLength))
                kappaFname = os.path.join(self.CWD,task,"MP_kappa_output",trial)
                outFname = os.path.join(self.CWD,task,"MP_consensus_output",trial)

                kappaFnamedir = os.path.abspath(kappaFname + "/../")
                if(not os.path.isdir(kappaFnamedir)):
                    path = pathlib.Path(kappaFnamedir)
                    path.mkdir(parents=True, exist_ok=True)  

                outFnamedir = os.path.abspath(outFname + "/../")
                if(not os.path.isdir(outFnamedir)):
                    path = pathlib.Path(outFnamedir)
                    path.mkdir(parents=True, exist_ok=True)  
                kappaDir = kappaFnamedir


                out_lines = self.MPCompact(out_lines)

                utils.save(kappaFname,kappa_lines)  
                utils.save(outFname,out_lines)   

                
                MPid = 0 
                #global unique_labels 
                unique_labels = {}

            print("Summary for "+task)
            print("Average K alpha unweighted %f",statistics.mean(trialResults))
            taskLength = sum(trialLengths)
            print("sum of actualLengths in task:",taskLength)
            crazylistcomp = [ (trialLengths[i]/taskLength)* trialResults[i] for i in range(0,len(trialLengths))] 
            print("Average K alpha weighted   %f",sum( crazylistcomp ))
            kappaDirs.append(kappaDir)
        
        return kappaDirs

    def generateConsensusGestures(self):
        F = FileGrabber()
        kappaDirs = []
        kappaDir = ""

        for task in self.tasks:
            print("task:",task)
            trialResults = []
            trialLengths = []
            for trial in os.listdir(os.path.join(self.CWD,task,self.dataType,self.coders[0])):
                print("\ttrial",trial)
                #allTranscriptLines = []
                allTranscriptULines = []
                out_lines = []
                kappa_lines = []
                for coder in self.coders:
                    print("\t\tcoder:",coder)
                    tLines, tLinesU = F.getGestureLines(self.CWD, self.dataType, coder, task, trial) 
                    #allTranscriptLines.append(tLines)
                    allTranscriptULines.append(tLinesU)
                k_ints = []
                i_ints = []
                v_ints = []
                actualLength = 0
                maxLength = max([len(allTranscriptULines[0]),len(allTranscriptULines[1]),len(allTranscriptULines[2])])

                for lineIndex in range(0,len(allTranscriptULines[0])):
                    tSingleFrame = []
                    for coderIndex in range(0,len(self.coders)):
                        try:
                            line = allTranscriptULines[coderIndex][lineIndex].replace("\n","")                            
                            tSingleFrame.append(line)
                        except Exception as e:
                            break
                    if len(tSingleFrame) < 3:
                        break
                    #kappaPollRow, candidate = self.pollLine_cohen_kappa_gesture(tSingleFrame[0], tSingleFrame[1], tSingleFrame[2],lineIndex,DEBUG_INFO="file"+" "+str(1))
                    k_gest = int(tSingleFrame[0].split(" ")[1].replace("G",""))
                    i_gest = int(tSingleFrame[1].split(" ")[1].replace("G",""))
                    v_gest = int(tSingleFrame[2].split(" ")[1].replace("G",""))
                    k_ints.append(k_gest)
                    i_ints.append(i_gest)
                    v_ints.append(v_gest)
                    candidate = self.majority(k_gest, i_gest, v_gest)

                    #outPollRow = self.majority_voting_gesture(tSingleFrame[0], tSingleFrame[1], tSingleFrame[2],lineIndex)
                    outPollRow = str(lineIndex) + " " + "G"+str(candidate)
                    out_lines.append(outPollRow)
                    kappa_lines.append(str(lineIndex) + " G"+str(k_gest) + " G"+str(i_gest) + " G"+str(v_gest) + " ->G"+str(candidate))
                    actualLength+=1


                arr = [k_ints,i_ints,v_ints]
                results = self.getK_Kappa(arr, "nominal",False)

                kappa = self.rawK_Kappa(arr, "nominal")

                print("\t\t\tKA:",results,",",kappa)
                trialResults.append(kappa)
                trialLengths.append(actualLength)

                print("\t\t\t\t#",str(actualLength)+"/"+str(maxLength))
                kappaFname = os.path.join(self.CWD,task,"gesture_kappa_output",trial)
                outFname = os.path.join(self.CWD,task,"gesture_consensus_output",trial)

                kappaFnamedir = os.path.abspath(kappaFname + "/../")
                if(not os.path.isdir(kappaFnamedir)):
                    path = pathlib.Path(kappaFnamedir)
                    path.mkdir(parents=True, exist_ok=True)  

                outFnamedir = os.path.abspath(outFname + "/../")
                if(not os.path.isdir(outFnamedir)):
                    path = pathlib.Path(outFnamedir)
                    path.mkdir(parents=True, exist_ok=True)  
                kappaDir = kappaFnamedir


                out_lines = self.gestureCompact(out_lines)

                utils.save(kappaFname,kappa_lines)  
                utils.save(outFname,out_lines)    

            print("Summary for"+task)
            print("Average K alpha unweighted %f",statistics.mean(trialResults))
            taskLength = sum(trialLengths)
            print("sum of actualLengths in task:",taskLength)
            crazylistcomp = [ (trialLengths[i]/taskLength)* trialResults[i] for i in range(0,len(trialLengths))] 
            print("Average K alpha weighted   %f",sum( crazylistcomp ))
            kappaDirs.append(kappaDir)
        
        

        
        return kappaDirs
    
    def MPCompact(self,out_lines):
        newLines = []
        start = 0
        end = 0
        lastGest = " ".join(out_lines[0].split(" ")[1:])
        for i in range(0,len(out_lines)):
            split = out_lines[i].split(" ")
            

            

            if (lastGest != " ".join(split[1:])):
                newLines.append(str(start) + " " + str(end-1) + " " + lastGest)
                lastGest = " ".join(split[1:])
                start = end
            else:
                end+=1
        return newLines

    def gestureCompact(self,out_lines):
        newLines = []
        start = 0
        end = 0
        lastGest = out_lines[0].split(" ")[1]
        for i in range(0,len(out_lines)):
            split = out_lines[i].split(" ")
            
            if (lastGest != split[1]):
                newLines.append(str(start) + " " + str(end-1) + " " + lastGest)
                lastGest = split[1]
                start = end
            else:
                end+=1
        return newLines
    
    def generateConsensus(self):
        F = FileGrabber()
        kappaDirs = []
        kappaDir = ""
        for task in self.tasks:
            print("task:",task)
            # -> Trial
            for trial in os.listdir(os.path.join(self.CWD,self.dataType,"Joyce",task)):
                print("\ttrial",trial)
                allTranscriptLines = []
                allTranscriptULines = []
                out_lines = []
                kappa_lines = []
                # -> Coders
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


    
    def pollLine_cohen_kappa_gesture(self, k_line, i_line, v_line,lineNumber, DEBUG=True,DEBUG_INFO="none", ):

        # X_S means array of Strings from x's line
        k_s = k_line.split(" ")
        i_s = i_line.split(" ")
        v_s = v_line.split(" ")
        o_s = k_line.split(" ")
        
        k_gest = int(k_s[1].replace("G",""))
        i_gest = int(i_s[1].replace("G",""))
        v_gest = int(v_s[1].replace("G",""))

        line = ""
            
        candidate = self.majority(k_gest, i_gest, v_gest)
        o_s[1] = "G"+str(candidate)

        if(DEBUG):
            line = k_s[0] + " " + "".join(k_s[1:])
            line = line + " "+self.lineToStr(i_line)+" "+self.lineToStr(v_line)+" "+"".join(o_s[1:])      #+ str(res)
        else:
            #line = " ".join(k_s)
            pass
        arr = [k_gest,i_gest,v_gest]
        ZERO_ROW = candidate == 0
        line = line + self.getK_Kappa(arr, "nominal",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "ordinal",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "interval",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "ratio",ZERO_ROW)
        arr = [k_gest,i_gest,v_gest,candidate]
        line = line + self.getK_Kappa(arr, "nominal",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "ordinal",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "interval",ZERO_ROW)
        line = line + self.getK_Kappa(arr, "ratio",ZERO_ROW)
       
        return line, candidate 

    
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