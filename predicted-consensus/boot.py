
import os, sys
import json
import pathlib
import math
from PIL import Image, ImageDraw, ImageColor
import krippendorff
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pkg_resources import invalid_marker
import statistics
from numpy.linalg import matrix_power
import scikits.bootstrap as boot

from nltk import agreement
from nltk.metrics.distance import masi_distance
from nltk.metrics.distance import jaccard_distance

from scipy.spatial import distance


import numpy as np
from scipy.stats import norm
from scipy.stats import bootstrap

from sklearn.metrics import jaccard_score as jacc_sklearn 
from scipy.spatial.distance import jaccard as jccScipy

def ciStuff():
    rng = np.random.default_rng()
    dist = norm(loc=2, scale=4)  # our "unknown" distribution
    data = dist.rvs(size=100, random_state=rng)

    std_true = dist.std()      # the true value of the statistic
    print("the true value of the statistic",std_true)

    std_sample = np.std(data)  # the sample statistic
    print("the sample statistic", std_sample)

    data = (data,)  # samples must be in a sequence
    print("other data:",data,np.shape(data))
    res = bootstrap(data, np.std, confidence_level=0.9,
                    random_state=rng)
    print(res.confidence_interval)
    n_trials = 1000
    '''
    ci_contains_true_std = 0
    for i in range(n_trials):
    data = (dist.rvs(size=100, random_state=rng),)
    ci = bootstrap(data, np.std, confidence_level=0.9, n_resamples=1000,
                    random_state=rng).confidence_interval
    if ci[0] < std_true < ci[1]:
        ci_contains_true_std += 1
    print(ci_contains_true_std)
    '''

    data = (dist.rvs(size=(n_trials, 100), random_state=rng),)
    res = bootstrap(data, np.std, axis=-1, confidence_level=0.9,
                    n_resamples=1000, random_state=rng)
    ci_l, ci_u = res.confidence_interval

    print("ci_l",ci_l[995:])
    print("ci_u",ci_u[995:])

def dataShape():
    n_trials = 3
    rng = np.random.default_rng()
    dist = norm(loc=2, scale=4)  # our "unknown" distribution
    data = (dist.rvs(size=(n_trials, 100), random_state=rng),)
    print(np.shape(data))
    print(data)
def trials():
    x = [[1,1,1],[1,0,1],[0,0,0]]
    print(x)
    #[[1, 1, 1], [1, 0, 1], [0, 0, 0]]
    sk = jacc_sklearn(x[0],x[1])
    #0.33
    scp = jccScipy(x[0],x[1])
    #0.66
    nltkJac = jaccard_distance(set(x[0]),set(x[1]))
    #jaccard2 = distance.jaccard(l1,l2)
    #print("\tJacc2",jaccard2)
    print("Sklearn:",sk," Scipy:",scp," NLTK:",nltkJac)

def main():     
    dir=os.getcwd()
    task = "Suturing" #then suturing to b done w/ jigs
    I = Iterator(task)
    #I.fixStates()
    I.poll()
    #I.verifyOutput()
    #I.showAllPlots()
    #I.metrics()
    #ciStuff()
    #trials()
    #dataShape()
    quit(); 

class Iterator:
    def __init__(self, task):
        self.CWD = os.path.dirname(os.path.realpath(__file__))        
        self.task = task
        self.outputDir = os.path.join(self.CWD, self.task,"output")
        self.ian = os.path.join(self.CWD,self.task, "ian")
        self.kay = os.path.join(self.CWD,self.task, "kay")
        self.v = os.path.join(self.CWD, self.task,"volunteer")
        self.v2 = os.path.join(self.CWD, self.task,"vol2")
        self.kappa = os.path.join(self.CWD, self.task,"kappa")
        self.match = os.path.join(self.CWD, self.task,"match_lines")




    def metrics(self):

        fileCount = 0
        pre = 0
        post = 0
        preAggregate = 0
        postAggregate = 0
        sigmas = []
        jacs=[]
        lineCount = 0;
        all_k_series = []
        for root, dirs, files in os.walk(self.kappa):
            for file in files:
                if("99" in file):
                    continue 
                #if("Knot_Tying_S02_T02" not in file):
                #    continue
                kappa_file = os.path.join(self.kappa, file)
                print(file)
                #print(len(ka))
                #plot = self.getPlot(kappa_file,file)
                l_c, sigma, preAvg, postAvg, preAgr, postAgr = self.getAverage(kappa_file,file)
                jaccard = self.bootstrap(kappa_file, file)
                #all_k_series.append(np.asanyarray(k_series))
                jacs.append(jaccard)
                pre = pre+preAvg
                post= post+postAvg
                preAggregate=preAggregate+preAgr
                postAggregate=postAggregate+postAgr
                #allSigma = sigma+allSigma
                sigmas.append(sigma)
                #print(file, str(preAvg), str(postAvg), str(sigma)) 
                fileCount = fileCount + 1; 
                lineCount=lineCount+l_c;
        #k_arr = np.asanyarray(all_k_series)
        #print(np.shape(all_k_series),np.shape(k_arr))
        jac = np.average(jacs)
        sigma2 = sum(i*i for i in sigmas)
        sigma2 = sigma2 / (fileCount+1)
        sigma2 = math.sqrt(sigma2)
        #print(self.task)
        #print( "Length:",str(lineCount))
        #print( "Pre Unweight:",str( pre / (fileCount+1.0)))
        #print( "Post Unweight:",str( post  / (fileCount+1.0)))
        #print( "Sigma:",str( sigma2 ))
        #print( "Pre Weight:",str( preAggregate / lineCount ))
        #print( "Post Weight:",str(  postAggregate / lineCount ))
        print("Avg jaccard:",jac)

        return;

    def bootstrap(self,file,fileName,x_col=0, y_col=5,y_c_col=9,DEBUG=True):
        preAvg = 0
        postAvg = 0
        preAgr = 0
        postAgr = 0

        col1 = 1;
        col2 = 2;
        col3 = 3;

        l1 = []
        l2 = []
        l3 = []

        f = open(file)
        lines=f.readlines()        
        x, y, y_c= [], [], []
        lineCount = 0;
        for line in lines:
            try:
                #print("x:",line.split(" ")[x_col],"y:",line.split(" ")[y_col],"y_c:",line.split(" ")[y_c_col])
                l_s = line.split(" ")
                x.append(float(l_s[x_col]))
                y.append(float(l_s[y_col]))
                y_c.append(float(l_s[y_c_col]))
                l1.append(l_s[col1])
                l2.append(l_s[col2])
                l3.append(l_s[col3])
            except:
                pass;
            lineCount=lineCount+1
        f.close()

        data = (y,)  # samples must be in a sequence
        
        #print("data",data,np.shape(data))
        rng = np.random.default_rng()
        res = bootstrap(data, np.std, confidence_level=0.9,
                random_state=rng)
        #print("res",res)
        if(DEBUG):print("\tscipy",res.confidence_interval)
        n_trials = 1000    
        #data = (dist.rvs(size=(n_trials, 100), random_state=rng),)
        #res = bootstrap(data, np.std,  confidence_level=0.8,n_resamples=2, random_state=rng) #axis=-1,
        #ci_l, ci_u = res.confidence_interval
        #print("ci_l",ci_l[995:])
        #print("ci_l len: ",len(ci_l))
        #print("ci_u len:",len(ci_u))
        #print("ci_l:",ci_l," ci_u:",ci_u)
        #print("ci_u",ci_u[995:])
        #conf_interval = np.percentile(y,[5,95])#%90
        conf_interval = np.percentile(y,[2.5,97.5])

        # Print the interval
        if(DEBUG):print("\tnp percentile: ",conf_interval)
        ''' 
        alpha: float or iterable, optional
        The percentiles to use for the confidence interval (default=0.05). If this
        is a float, the returned values are (alpha/2, 1-alpha/2) percentile confidence
        intervals. If it is an iterable, alpha is assumed to be an iterable of
        each desired percentile.
        '''
        b = boot.ci(y, alpha=0.05,statfunction=np.average)
        if(DEBUG):print("\tscikits bootstrap:",b)
        l1_s = set(l1)
        l2_s = set(l2)
        l3_s = set(l3)
        '''
        jaccard = jaccard_distance(l1_s,l2_s)
        print("\tjaccard",jaccard)
        jaccard2 = distance.jaccard(l1,l2)
        print("\tJacc2",jaccard2)

        macroJac = jacc_sklearn(l1,l2,average="macro")
        print("Macro Jaccard",macroJac )

        weightedJac =  jacc_sklearn(l1,l2,average="weighted")
        print("Weighted jaccard",weightedJac)
        '''
        microJac = jacc_sklearn(l1,l2,average="micro")
        if(DEBUG):print("\tMicro Jaccard",microJac )
        return microJac
        

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
                v_file = os.path.join(self.v, file)
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
                ian_lines = self.takeAwayAngles(ian_lines)
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




main();