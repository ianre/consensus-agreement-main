import os, sys
import json
import pathlib
import math
import numpy as np
from PIL import Image, ImageDraw, ImageColor
import krippendorff
from collections import Counter

#from crowdkit.aggregation import DawidSkene
#from crowdkit.datasets import load_dataset

#import pandas as pd

global unique_labels
unique_labels = {}

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
    # Get task from command line

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
    task = "Needle_Passing"
    I = Iterator(task)
    I.poll()
    quit();

class Iterator:
    def __init__(self, task):
        self.CWD = os.path.dirname(os.path.realpath(__file__))        
        self.task = task
        #self.imagesDir = os.path.join(self.CWD, "images", task)
        #self.labelsDir = os.path.join(self.CWD, "labels", task)
        self.outputDir = os.path.join(self.CWD, self.task,"output")
        self.ian = os.path.join(self.CWD,self.task, "ian")
        self.kay = os.path.join(self.CWD,self.task, "kay")
        self.v = os.path.join(self.CWD, self.task,"volunteer")
        self.kappa = os.path.join(self.CWD, self.task,"kappa")
        self.match = os.path.join(self.CWD, self.task,"match_lines")


    def poll(self):
        # get a filename from Kay's set:
        count = 0
        for root, dirs, files in os.walk(self.kay):
            for file in files:
                #if(not("99"  in file)):
                #    continue
                #print(file)
                count=count+1
                kay_file =  os.path.join(self.kay, file)
                ian_file =  os.path.join(self.ian, file)
                v_file = os.path.join(self.v, file)
                out_file = os.path.join(self.outputDir, file)
                kappa_file = os.path.join(self.kappa, file)
                match_file = os.path.join(self.match, file)
                
                #print("K:",kay_file,"  I:",ian_file,"   v:",v_file)
                #print("Key:",kay_file[-60:])
                print("File: ",file)

                kay_lines = []
                with open(kay_file) as kay_data:
                    for line in kay_data:
                        kay_lines.append(line)
                
                ian_lines = []
                with open(ian_file) as ian_data:
                    for line in ian_data:
                        ian_lines.append(line)
                v_lines = []
                with open(v_file) as v_data:
                    for line in v_data:
                        v_lines.append(line)
                
                out_lines = []
                kappa_lines = []
                match_lines = []

                out_lines.append("Frame Consensus")
                kappa_lines.append("Frame Kay Ian Volunteer Nominal Ordinal Interval Ratio")
                #               0 00000 00000 00000 00000 0 0 0 0
                match_lines.append("Frame Consensus")

                i = 0                
                for line in kay_lines:
                    line = line.replace("\n","")
                    ian_line = ian_lines[i].replace("\n","")
                    v_line = v_lines[i].replace("\n","")
                    kappaPollRow = self.pollLine_cohen_kappa(line, ian_line, v_line)
                    probsPollRow = self.pollLine_probs(line, ian_line, v_line)
                    outPollRow = self.majority_voting(line, ian_line, v_line)
                    out_lines.append(outPollRow)
                    kappa_lines.append(kappaPollRow)
                    match_lines.append(probsPollRow)
                    i=i+1
                self.save(out_file,out_lines)
                self.save(kappa_file, kappa_lines)
                self.save(match_file, match_lines)
                
                global unique_labels
                print("uniue",unique_labels);
                unique_labels = {}


        print(count,"files processed!")
    def save(self, x_file, x_lines):
        with open(x_file, 'w+') as f:
            for item in x_lines:
                f.write("%s\n" % item)
        '''
        with open(out_file, 'w+') as f:
            for item in out_lines:
                f.write("%s\n" % item)

        with open(kappa_file, 'w+') as f:
            for item in kappa_lines:
                f.write("%s\n" % item)
        with open(match_file, 'w+') as f:
            for item in match_lines:
                f.write("%s\n" % item)

        '''

    def getListOfInts(self, line):
        stateNums = []
        for state in line:
            stateNums.append(int(state) +1)
        return stateNums

    def getListOfInts_NOFSET(self, line):
        stateNums = []
        for state in line:
            stateNums.append(int(state))
        return stateNums

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

    def lineToStr(self, line):
        l_s = line.replace("\n","").split(" ")
        return "".join(l_s[1:])

    def pollLine_cohen_kappa(self, k_line, i_line, v_line,DEBUG=True):
        # X_S means array of "S"trings from x's line
        k_s = k_line.split(" ")
        i_s = i_line.split(" ")
        v_s = v_line.split(" ")
        o_s = k_line.split(" ")
        probs = k_line.split(" ")
        # to do math
        k_n = self.getListOfInts(k_s)
        i_n = self.getListOfInts(i_s)
        v_n = self.getListOfInts(v_s)
        o_n = self.getListOfInts(o_s)

        for i in range (1,len(k_s)):
            self.checkUniqueness(k_s[i], i_s[i], v_s[i]);
            candidate = self.majority(k_s[i], i_s[i], v_s[i]);
            o_s[i] = candidate

        '''
        arr = [[1, 1, 1, 1, 3, 0, 0, 1],
            [1, 1, 1, 1, 3, 0, 0, 1],
            [1, 1, 1, 1, 2, 0, 0, 1],
            [1, 1, 0, 2, 3, 1, 0, 1]]    
        '''
        #self.k_usage();
       
        if(DEBUG):
            line = k_s[0] + " " + "".join(k_s[1:])
            line = line + " "+self.lineToStr(k_line) +" "+self.lineToStr(i_line)+" "+self.lineToStr(v_line)  #+ str(res)
        else:
            line = " ".join(k_s)

        k_n = self.getListOfInts_NOFSET(k_s[1:])
        i_n = self.getListOfInts_NOFSET(i_s[1:])
        v_n = self.getListOfInts_NOFSET(v_s[1:])
        o_n = self.getListOfInts_NOFSET(o_s[1:])
        arr = [k_n,i_n,v_n]
        res = 0
        try:
            res = krippendorff.alpha(reliability_data=arr,level_of_measurement="nominal")
        except:
            pass

        #print("`-> RES!",res)
        line = line + " "+ str(res) 
        try:
            res = krippendorff.alpha(reliability_data=arr,level_of_measurement="ordinal")
        except:
            pass   
        line = line + " "+ str(res)
        try:
            res = krippendorff.alpha(reliability_data=arr,level_of_measurement="interval")
        except:
            pass   
        line = line + " "+ str(res)
        try:
            res = krippendorff.alpha(reliability_data=arr,level_of_measurement="ratio")
        except:
            pass   
        line = line + " "+ str(res)
        '''
        k_n = self.getListOfInts(k_s[1:])
        i_n = self.getListOfInts(i_s[1:])
        v_n = self.getListOfInts(v_s[1:])
        o_n = self.getListOfInts(o_s[1:])
        arr = [k_n,i_n,v_n]
        
        ''' 
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
       
    def checkUniqueness(self, k, i, v):
        global unique_labels
        if( k in unique_labels.keys()):
            pass
        else:
            unique_labels[k] = k;
        if( i in unique_labels.keys()):
            pass
        else:
            unique_labels[i] = i;
        if( v in unique_labels.keys()):
            pass
        else:
            unique_labels[v] = v;

        #print("uniue",unique_labels);
        
    def majority(self, k, i, v):
        k_n = int(k)
        i_n = int(i)
        v_n = int(v)
        arr = [k_n,i_n,v_n]
        return self.Most_Common(arr)
    
    def Most_Common(self, lst):
        data = Counter(lst)
        obj = data.most_common(1)
        return data.most_common(1)[0][0]
        
    def majority_voting(self, k_line, i_line, v_line):
       

        k_s = k_line.split(" ")
        i_s = i_line.split(" ")
        v_s = v_line.split(" ")
        o_s = k_line.split(" ") #output
        probs = k_line.split(" ") #output        
        accepted = 0;

        for i in range (1,len(k_s)):
            self.checkUniqueness(k_s[i], i_s[i], v_s[i]);
            candidate = self.majority(k_s[i], i_s[i], v_s[i]);
            o_s[i] = candidate
            '''
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
            '''
            
            #o_s[i] = (int(k_s[i]) + int(i_s[i]) + int(o_s[i])) /3.0;
        
        #print(o_s)
        line = " ".join(o_s)
        line = line +"\t"+ " ".join(probs)
        #return (line, accepted, rejected);
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
            #o_s[i] = (int(k_s[i]) + int(i_s[i]) + int(o_s[i])) /3.0;
        
        #print(o_s)
        line = " ".join(o_s)
        line = line +"\t"+ " ".join(probs)
        #return (line, accepted, rejected);
        return line
    
       
    def getDirectory(self, filename, newDir):
        return "".join([ filename[0:self.dirIndices[0]], newDir, filename[self.dirIndices[1]:]])

    def imageToJSON(self, file):
        fileArr = file.split(".")
        return "".join(fileArr[:-1]) + ".json"

    def getRBGA(self, hexColor):
        c = ImageColor.getcolor(hexColor, "RGB")        
        c = c + opacity
        return c

    def DrawLabel(self, imageSource, labelSource, target, debug=False):
        #print("DrawLabel", imageSource, labelSource,target)
        print("labelSource",labelSource)
        J = JSONInterface(labelSource)
        polygons = J.getPolygons();
        keyPoints = J.getKeyPoints();   
        polyLines = J.getPolyLines(); 
        #print(polyLines)
        #return    
        img = Image.open(imageSource)
        #draw = ImageDraw.Draw(img)
        draw = ImageDraw.Draw(img, "RGBA")        
        for i in range(len(polygons)): # draws each polygon 
            c = self.getRBGA(colors[i])
            draw.polygon(polygons[i], fill=c) #,outline='#EA5536')     
        for i in range(len(polyLines)): # draws each polygon 
            print("Drawing one polyLine")
            c = self.getRBGA(colors[-i])
            #draw.line((polyLines[i][0],polyLines[i][1],polyLines[i][-1],polyLines[i][-1]), fill=c, width=3)  
            #draw.polygon(polyLines[i], fill=c) #,outline='#EA5536')   
            #polyLines[i][0:2]
            #draw.line(polyLines[i], fill=c, width=3)
            k=0
            for j in range(0,len(polyLines[i])):
                #if(k+3>=len(polyLines[i])):
                #    
                draw.line(( polyLines[i][k],
                            polyLines[i][k+1],
                            polyLines[i][k+2],
                            polyLines[i][k+3]), fill=c, width=5) 
                k+=2
                if(k>=len(polyLines[i])-2): break
 
                
        for i in range(len(keyPoints)): # draws each KeyPoint
            x = keyPoints[i][0]
            y = keyPoints[i][1]            
            leftUpPoint = (x-radius, y-radius)
            rightDownPoint = (x+radius, y+radius)
            twoPointList = [leftUpPoint, rightDownPoint]
            c = self.getRBGA(colors[i+(len(polygons))])
            draw.ellipse(twoPointList, fill=c)
        #for i in range(len()
        img.save(target)

    def DrawLabels(self):
        count = 0
        for root, dirs, files in os.walk(self.imagesDir):
            for file in files:
                if "frame" not in file:
                    continue
                '''
                If we replace "images" by "labels" then the image source should be the same as the label source, 
                which is the same as the output destination
                '''
                imageRoot = root
                labelRoot = self.getDirectory(root,"labels")
                outputRoot =  self.getDirectory(root,"output")

                imageSource = os.path.join(imageRoot, file)
                labelSource = os.path.join(labelRoot, self.imageToJSON(file))
                outputDest = os.path.join(outputRoot, file)

                if(not os.path.isdir(outputRoot)):
                    path = pathlib.Path(outputRoot)
                    path.mkdir(parents=True, exist_ok=True)

                if os.path.exists(outputDest):
                    os.remove(outputDest)

                if not os.path.exists(labelSource):
                    print("label not found for ",imageSource)
                    continue
                else:
                    self.DrawLabel(imageSource,labelSource,outputDest)
                count += 1
                
        print(count,"images processed!")
       
'''
JSONInterface deals with the particular JSON format of the annotations
It's set up now to read labels as we received them from Cogito

If the JSON annotations are in a different format, you can edit the getPolygons and getKeyPoints methods
'''
class JSONInterface:    
    def __init__(self, jsonLoc):
        self.json_location = jsonLoc    
        with open(self.json_location) as f:
            data = json.load(f)
            self.data = data
            self.meta = data['metadata']
            self.instances = data['instances']      
    '''
    Returns a list of polygons
    each polygon is a list of points ordered as [x1, y1, x2, y2, ... , xn, yn]
    '''
    def getPolygons(self):
        polygonSeries = list()
        for instance in self.instances:            
            instance_ID = instance["classId"]
            instance_type = instance["type"]
            instance_probability = instance["probability"]
            instance_class = instance["className"]
            if(instance_type == "polygon"):                
                polygonSeries.append(instance["points"])   
        return polygonSeries
    '''
    Returns a list of PolyLines
    each polyline is a list of points ordered as [x1, y1, x2, y2, ... , xn, yn]
    '''
    def getKeyPoints(self):
        keyPoints = list()
        for instance in self.instances:            
            instance_ID = instance["classId"]
            instance_type = instance["type"]
            instance_probability = instance["probability"]
            instance_class = instance["className"]
            if(instance_type == "point"):                
                keyPoints.append([instance['x'], instance['y']])   
        return keyPoints

    '''
    Returns a list of PolyLines
    each PolyLine is a list [x, y]
    '''
    def getPolyLines(self):
        polylineSeries = list()
        for instance in self.instances:            
            instance_ID = instance["classId"]
            instance_type = instance["type"]
            instance_probability = instance["probability"]
            instance_class = instance["className"]
            if(instance_type == "polyline"):                
                polylineSeries.append(instance["points"])    
        return polylineSeries

'''
Usage: put the top folder name. This folder should exist both under imges and labels

The organization within both folders should be the same.

The labels will appear in the same file organization as the images dataset under the folder "output"
'''
main();

