#! /usr/bin/python
#################################################
#			Python Template						#
#################################################
# Zachary Priddy - 2015 						#
# me@zpriddy.com 								#
#												#
# Features: 									#
#	- XXXXXX									#
#	- XXXXXX 									#
#################################################
#################################################


#########
#IMPORTS
#########
import argparse
from StringIO import StringIO
import pycurl
import pickle

#########
#VARS
#########
programName="ASU Class Finder"
programDescription="INSERT PROGRAM DESCRIPTION"

searchURL1="https://webapp4.asu.edu/catalog/classlist?"
searchURL2="&e=all&hon=F"

allClassDB = {}



##################################################
#FUNCTIONS
##################################################

###########
# GET ARGS
##########
def getArgs():
	parser = argparse.ArgumentParser(prog=programName, description=programDescription)
	parser.add_argument("-s","--subject",help="Enter Subject (for MAT270 - enter MAT",required=True)
	parser.add_argument("-d","--debug",help="debug",action="store_true")
	parser.add_argument("-n","--classNumber",help="Enter Class Number (for MAT270 - enter 270)",required=True)
	#parser.add_argument("-id","--classID",help="Enter Class ID",required=True)




	return parser.parse_args()

	###############################################
	# OTHER NOTES 
	# 
	# For groups of args [in this case one of the two is required]:
	# group = parser.add_mutually_exclusive_group(required=True)
	# group.add_argument("-a1", "--arg1", help="ARG HELP")
	# group.add_argument("-a2", "--arg2", help="ARG HELP")
	#
	# To make a bool thats true:
	# parser.add_argument("-a","--arg",help="ARG HELP", action="store_true")
	#
	###############################################

##############
# END OF ARGS
##############


#############
# MAIN
#############
def main(args):
	global allClassDB
	try:
		allClassDB = pickle.load(open('cache/allClassesDB','rb'))
	except:
		print "Not Loaded from cache"
	
	#myClasses = getClasses(args.subject)
	#myClasses =  searchForClassBySub(args.subject,args.classNumber)

	#pickle.dump(allClassDB,open('cache/allClassesDB','wb'))

	#for item in myClasses:
	#	if (item[2] != 0):
	#		print item
	buildCache()

def buildCache():
	global allClassDB

	subList = open('subjects.txt','r').read().split("\n")
	for subject in subList:
		print "Loading Subject: ", subject
		try:
			parseClasses(downloadAndParse(subject),subject)
			tempArray = allClassDB[subject]
			path = "cache/" + subject + ".db"
			pickle.dump(tempArray,open(path,'wb'))
		except:
			print "ERROR", subject
		pickle.dump(allClassDB,open('cache/allClassesDB','wb'))
	print "Done"





#############
# END OF MAIN
#############

def searchForClassBySub(classSub, classNum):
	global allClassDB
	returnArray = []
	getClasses(classSub)
	searchFor = classSub + str(classNum)
	print searchFor

	for item in allClassDB[classSub]:
		if (item[0] == searchFor):
			returnArray.append(item)

	return returnArray


def getClasses(classSub):
	global allClassDB
	if not classSub:
		raise NameError('noClassSub')
	else:
		allClasses = downloadAndParse(classSub)
		parseClasses(allClasses, classSub)
		return allClassDB[classSub]


def downloadAndParse(classSub, term=2157,debug=True):
	output = ""
	searchURL = searchURL1 + "s=" + str(classSub) + "&t=" + str(term) + searchURL2
	if(debug):
		print searchURL
	trash = StringIO()
	page1 = StringIO()
	page2 = StringIO()
	page3 = StringIO()
	web = pycurl.Curl()
	web.setopt(web.URL,searchURL)
	web.setopt(web.FOLLOWLOCATION,True)
	web.setopt(web.COOKIEFILE,'cookies.txt')
	web.setopt(web.COOKIEJAR,'cookies.txt')
	web.setopt(web.WRITEDATA, trash)
	web.perform()
	#page1 = str(buffer.getvalue())
	#p1 = str(web.contents)
	web.close()

	searchURL="""https://webapp4.asu.edu/catalog/app?component=tablePages.linkPage&page=ClassResults&service=direct&session=T&sp=AClassResults%2CCatalogList&sp=1"""
	web = pycurl.Curl()
	web.setopt(web.URL,searchURL)
	web.setopt(web.FOLLOWLOCATION,True)
	web.setopt(web.COOKIEFILE,'cookies.txt')
	web.setopt(web.COOKIEJAR,'cookies.txt')
	web.setopt(web.WRITEDATA, page1)
	web.perform()
	web.close()

	#
	if(str(page1.getvalue()).count(" " + classSub + " ") == 300):
		searchURL="""https://webapp4.asu.edu/catalog/app?component=tablePages.linkPage&page=ClassResults&service=direct&session=T&sp=AClassResults%2CCatalogList&sp=2"""
		web = pycurl.Curl()
		web.setopt(web.URL,searchURL)
		web.setopt(web.FOLLOWLOCATION,True)
		web.setopt(web.COOKIEFILE,'cookies.txt')
		web.setopt(web.COOKIEJAR,'cookies.txt')
		web.setopt(web.WRITEDATA, page2)
		web.perform()
		web.close()

	if(str(page2.getvalue()).count(" " + classSub + " ") == 300):
		searchURL="""https://webapp4.asu.edu/catalog/app?component=tablePages.linkPage&page=ClassResults&service=direct&session=T&sp=AClassResults%2CCatalogList&sp=3"""
		web = pycurl.Curl()
		web.setopt(web.URL,searchURL)
		web.setopt(web.FOLLOWLOCATION,True)
		web.setopt(web.COOKIEFILE,'cookies.txt')
		web.setopt(web.COOKIEJAR,'cookies.txt')
		web.setopt(web.WRITEDATA, page3)
		web.perform()
		web.close()


	#print str(page1.getvalue()).count(" " + classSub + " ")
	#print str(page2.getvalue()).count(" " + classSub + " ")
	#print str(page3.getvalue()).count(" " + classSub + " ")

	if(str(page1.getvalue()) == str(page2.getvalue()) and str(page2.getvalue()) == str(page3.getvalue())):
		#print "ALL SAME"
		output = str(page1.getvalue())
	elif(str(page3.getvalue()) == str(page2.getvalue())):
		#print "SECOND AND THIRD SAME"
		output = str(page1.getvalue()) + str(page2.getvalue())
	else:
		output = str(page1.getvalue()) + str(page2.getvalue()) + str(page3.getvalue())

	print "TOTAL " + classSub + " CLASSES: ", output.count(" " + classSub + " ")

	return output


def parseClasses(inputString, classSub):
	global allClassDB
	allClassDB[classSub] = []
	thisClass = []
	allClasses = inputString.split("<tr class=\"grp")


	
	
	#print len(allClasses)

	for item in allClasses:
		loc = item.find(" " + classSub + " ")
		if(item[loc:loc+8].find(" " + classSub + " ") != -1):

			dayList2 = None
			startTime = None
			startTime2 = None
			startHour = None
			startHour2 = None
			startMin = None
			startMin2 = None
			endTime = None
			endTime2 = None
			endHour = None
			endHour2 = None
			endMin = None
			endMin2 = None
			reserved_status = "Reserved"
			
			idloc = item.find(";r=")
			avb = item.find("""<td style="text-align:right;padding:0px;width:22px; border:none">""")
			tot= item.find("""<td style="text-align:left;padding:0px;width:22px;border:none">""")
			dayListloc = item.find("""<td class="dayListColumnValue""")
			startTimeloc = item.find("""<td class="startTimeDateColumnValue""")
			endTimeloc = item.find("""<td class="endTimeDateColumnValue""")

			dayList = item[dayListloc+49:dayListloc+90].replace("\n","").replace("\t","").replace(">","")
			dayListEndloc = dayList.find("&nbsp;")
			if('<br/' in dayList):
				dayList2 = dayList.split("<br/")[1].split("&nbsp")[0]
				dayList = dayList.split("<br/")[0]
			else:
				dayList = dayList[:dayListEndloc]

			if(dayList != ''):
				startTime = item[startTimeloc+56:startTimeloc+200].replace("\n","").replace("\t","").replace(">","")
				startTimeEndloc = startTime.find("&nbsp;")
				startTime = startTime.split("&nbsp;")[0]
				if('<br/' in startTime):
					startTime2 = startTime.split('<br/')[1].replace(" ", "")
					startTime = startTime.split('<br/')[0].replace(" ","")

				endTime = item[endTimeloc+54:endTimeloc+200].replace("\n","").replace("\t","").replace(">","")
				endTimeEndloc = endTime.find("&nbsp;")
				#endTime = endTime[:endTimeEndloc].replace(" ","")
				endTime = endTime.split("&nbsp;")[0]
				if('<br/' in endTime):
					endTime2 = endTime.split('<br/')[1].replace(" ", "")
					endTime = endTime.split('<br/')[0].replace(" ","")


				startHour = int(startTime.split(":")[0])
				if ('PM' in startTime and startHour != 12):
					startHour = int(startHour) + 12
				startMin = int(startTime.split(":")[1][0:2])
				#startMin = int(startMin)
				
				endHour = int(endTime.split(":")[0])
				if('PM' in endTime and endHour != 12):
					endHour = int(endHour) + 12 
				endMin = int(endTime.split(":")[1][0:2])

				if(dayList2):
					startHour2 = int(startTime2.split(":")[0])
					if ('PM' in startTime2 and startHour2 != 12):
						startHour2 = int(startHour2) + 12
					startMin2 = int(startTime2.split(":")[1][0:2])
					#startMin = int(startMin)
					
					endHour2 = int(endTime2.split(":")[0])
					if('PM' in endTime2 and endHour2 != 12):
						endHour2 = int(endHour2) + 12 
					endMin2 = int(endTime2.split(":")[1][0:2])


			else:
				dayList = "ONLINE"

			if('images/icon_circle.png' in item):
				reserved_status = "Not Reserved"


		
			

		#if(item[loc:loc+8].find(" " + classSub + " ") != -1):
			#print item[loc:loc+8], item[idloc+3:idloc+8], item[avb+65:avb+68].replace("<","").replace("/",""), "of", item[tot+63:tot+66].replace("<","").replace("/","") , "open"
			thisClass.append([item[loc:loc+8].replace(" ",""), int(item[idloc+3:idloc+8]),int(item[avb+65:avb+68].replace("<","").replace("/","")),int(item[tot+63:tot+66].replace("<","").replace("/","")), dayList, startTime, startHour, startMin, endHour, endMin, dayList2, startTime2, startHour2, startMin2, endTime2, endHour2, endMin2, reserved_status])

	allClassDB[classSub] = thisClass




###########################
# PROG DECLARE
###########################
if __name__ == '__main__':
	args = getArgs()
	main(args)
