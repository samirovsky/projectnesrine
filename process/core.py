# coding: utf-8
import os
import gzip
import json
import datetime
import time
#import timedelta  
"""
with open("davis_80_station_ids.csv") as f:
    station_ids = set(x.strip() for x in f)

"""
START_INDEX_DATE = 4
END_INDEX_DATE = -4
DEFAULT_CONFIG_FILE_PATH= "./config/config.json"


class Configuration:

        datadir    = ""
        startdate  = ""
        enddate    = ""
        incmode    = ""
        filefolder = ""
        outfile    = ""

        """Configuration handler.

        :param datadir: A string, 
        :param startdate: An int, 
        (...)
        """
        #def __init__(self, datadir, startdate, enddate, incmode, filefolder, outfile):
        #        self.datadir = datadir
        #        self.startdate = startdate
        #        self.enddate = enddate
        #        self.incmode = incmode
        #        self.filefolder = filefolder
        #        self.outfile = outfile
        
        def __init__(self):
                self.datadir    = ""
                self.startdate  = ""
                self.enddate    = ""
                self.incmode    = ""
                self.filesfolder = ""
                self.outfile    = ""
        
        def initConfigurationFromArgs(self, args):
                configurationFile = ""
                if (args.config is not None):
                        if(args.config == ""):
                                configurationFile = DEFAULT_CONFIG_FILE_PATH
                        else:
                                configurationFile = args.config
                
                
                if (configurationFile != ""):
                        with open(args.config) as config_file:
                                configurationdata = json.load(config_file)
                        self.datadir = configurationdata['datadir'] if (configurationdata['datadir']!="") else args.datadir
                        self.startdate = configurationdata['startdate'] if (configurationdata['startdate']!="") else args.startdate
                        self.enddate = configurationdata['enddate'] if (configurationdata['enddate']!="") else args.enddate
                        self.incmode = configurationdata['incmode'] if (configurationdata['incmode']!="") else args.incmode
                        self.filesfolder = configurationdata['filesfolder'] if (configurationdata['filesfolder']!="") else args.filesfolder
                        self.outfile = configurationdata['outfile'] if (configurationdata['outfile']!="") else args.outfile
                else:
                        self.datadir = args.datadir
                        self.startdate = args.startdate
                        self.enddate = args.enddate
                        self.incmode = args.incmode
                        self.filesfolder = args.filesfolder
                        self.outfile = args.outfile

class FileCrawler:
        """
        A Class that knows how to crawl files and directories ! d__ <->_<-> __b
        """
        configuration = Configuration()

        def __init__(self, configuration):
                self.configuration = configuration
        
        def matchlines(gzfile):#, pattern_set=station_ids):
                """
                Generate the lines matching the pattern_set
                """
                with gzip.open(gzfile, mode="rt") as f:
                        for line in f:
                                # Data format is
                                # timestamp, station ID, ...
                                station = line.split(",")[1]
                                #if station in pattern_set:
                                #    yield line

        def interpretDateFormat(self, dateFormat):

                """
                Check Date Format 

                """
                formatInterprted = dateFormat.replace('%m','Mois').replace('%d','Jour_du_mois').replace('%Y', 'Annee_en_4_chiffres').replace('%b','Les 3 premiers caractères du mois')
                print ("The correct format is : " + formatInterprted)
        

        def browseDirectoryRecursive(self, rootPath = '.', startingDate = datetime.date.today().strftime('%m%d%Y'), endingDate = None,
                incrementDateMode = 'd', dateFormat = '%m%d%Y', datedFilesFolder=''):

                """
                Browse all directories and select files by dates

                """
                #self.interpretDateFormat(dateFormat)
                currentDateStr = self.validateDateTime(startingDate, dateFormat)
                currentDate = datetime.datetime.strptime(currentDateStr, dateFormat)
                datesList = []
                datesListStr = []
                dateFilesExist = False
                


                allFilesPathList = []
                fileNamesList = []
                selectedFilesPathList = []
                nfiles = 0
                # Browse all files in all directories inside the root directory and store paths, and files names
                for root, directories, filenames in os.walk(rootPath):
                        #print "Directories in " + rootPath + "\n" 
                        #for directory in directories:
                                #print ("Dir "+os.path.join(root, directory))

                        #print "Files in " + rootPath + "\n" 
                        for filename in filenames: 
                                print ("File "+os.path.join(root,filename))
                                allFilesPathList.append(os.path.join(root,filename))
                                fileNamesList.append(filename)
                                nfiles +=1
                                #if (filename[START_INDEX_DATE:END_INDEX_DATE]):
                                        #dateFilesExist = True
                                        #print filename[START_INDEX_DATE:END_INDEX_DATE]
                
                
                # TODO: Utiliser dateutil library pour plus de precision
                nDays = 0
                if (incrementDateMode == 'd'):
                        nDays = 1
                if (incrementDateMode == 'w'):
                        nDays = 7
                if (incrementDateMode == 'm'):
                        nDays = 30
                if (incrementDateMode == 'y'):
                        nDays = 365
                
                #define dates dependin on the incrementation method and number of files (possible dates files if no ending date defined)
                ndates = 0
                if (ndates == nfiles) :
                        #if no files where found in directory so no need to compute anything (can be improved by checking dates early)
                        print("No files to be selected !")
                        return []
                elif endingDate is None :
                        while (ndates < nfiles):
                                
                                datesList.append(currentDate)
                                datesListStr.append(currentDate.strftime(dateFormat))
                                print("defined date : "+currentDate.strftime(dateFormat))
                                currentDate = currentDate+datetime.timedelta(days=nDays)
                                ndates+=1
                else :
                        while (currentDate < endingDate):
                                datesList.append(currentDate)
                                datesListStr.append(currentDate.strftime(dateFormat))
                                currentDate = currentDate+datetime.timedelta(days=nDays)
                                print(currentDate.strftime(dateFormat))
                
                
                
                #Select files usng the list of dates defined
                #User is alerted when files are missing for some dates (example week 0 : file, week 1: no file (error), week 2: file, week 3: file)
                founddates = []
                for filename in fileNamesList:
                        # checking dates in file names is very important !
                        print ("Test file :"+filename)
                        datestr = self.getValidatedDateTimeFromFileName(filename, START_INDEX_DATE, END_INDEX_DATE)
                        if datestr in datesListStr and datestr not in founddates:
                                print ("Found str :"+datestr)
                                selectedFilesPathList.append(allFilesPathList[fileNamesList.index(filename)])
                                founddates.append(datestr)
                                print ("Found Path :"+allFilesPathList[fileNamesList.index(filename)])
                                #TODO compute datediff with last element of found dates to check subsequent dates
                
                return list(set(selectedFilesPathList))
                 
        def validateDateTime(self, datetimestr, format):
                datestr = ""
                try:
                        date_time = datetime.datetime.strptime(datetimestr, format)
                        datestr = date_time.strftime(format)
                except:
                        print("Error parsing filename to get datetime.")
                        print(datetimestr+" doesn't represent a valid datetime.") 
                        self.interpretDateFormat(format) 
                
                
                return datestr
        
        def getValidatedDateTimeFromFileName(self, filename, startindex, endindex, format='%m%d%Y'):
                datepart = filename[startindex:] if (endindex==0) else filename[startindex:endindex]
                #print ("Date extracted "+datepart)
                return self.validateDateTime(datepart, format)
        


        def readFile(self, gzfile):
                """
                Generate the lines matching the pattern_set
                """
                with gzip.open(gzfile, 'rb') as f:
                        file_content = f.read()
                
                return file_content

        #with gzip.open(gzfile, mode="rb") as f:
                #for line in f:
                # Data format is
                # timestamp, station ID, ...
                #station = line.split(",")[1]data
                #if station in pattern_set:
                #    yield line






def main(args):

    #Init configuration parameters
    conf = Configuration()
    conf.initConfigurationFromArgs(args)
    
    #Get files list using configuration
    fileCrawler = FileCrawler(conf)
    fileCrawler.browseDirectoryRecursive(args.datadir,args.startdate, None, args.incmode)

    #for x in os.listdir(args.datadir):
        #print x
        #if (x.endswith(".txt.gz")):
            #print x
            #strValue = readFile(args.datadir+"/"+x)


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--datadir", default=".",
            help="Location of the raw station txt.gz files")

    parser.add_argument("--startdate", default="",
            help="Starting date for files reading")

    parser.add_argument("--enddate", default="",
            help="Ending date for files reading")

    parser.add_argument("--incmode", default="d",
            help="Dates Incrementing Mode")

    parser.add_argument("--filesfolder", default="d",
            help="Files Folder")

    parser.add_argument("--outfile", default="OutFile.txt",
            help="File to append all matching rows to")

    parser.add_argument("--config",
            help="Configuration file to be used instead of many params")

    args = parser.parse_args()

    main(args)