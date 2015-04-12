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
	#getClasses(args.subject)
	myClasses =  searchForClassBySub(args.subject,args.classNumber)

	for item in myClasses:
		if (item[2] != 0):
			print item


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
	if not classSub:
		raise NameError('noClassSub')
	else:
		allClasses = downloadAndParse(classSub)
		parseClasses(allClasses, classSub)


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
		idloc = item.find(";r=")
		avb = item.find("""<td style="text-align:right;padding:0px;width:22px; border:none">""")
		tot= item.find("""<td style="text-align:left;padding:0px;width:22px;border:none">""")
		dayListloc = item.find("""<td class="dayListColumnValue""")
		startTimeloc = item.find("""<td class="startTimeDateColumnValue" id="informal_159">""")
		endTimeloc = item.find("""<td class="endTimeDateColumnValue" id="informal_160">""")

		dayList = item[dayListloc+49:dayListloc+90].replace("\n","").replace("\t","").replace(">","")
		dayListEndloc = dayList.find("&nbsp;")
		dayList = dayList[:dayListEndloc]

		#startTime = item[startTimeloc]

		if(item[loc:loc+8].find(" " + classSub + " ") != -1):
			#print item[loc:loc+8], item[idloc+3:idloc+8], item[avb+65:avb+68].replace("<","").replace("/",""), "of", item[tot+63:tot+66].replace("<","").replace("/","") , "open"
			thisClass.append([item[loc:loc+8].replace(" ",""), item[idloc+3:idloc+8],item[avb+65:avb+68].replace("<","").replace("/",""),item[tot+63:tot+66].replace("<","").replace("/",""), dayList])

	allClassDB[classSub] = thisClass




###########################
# PROG DECLARE
###########################
if __name__ == '__main__':
	args = getArgs()
	main(args)
