import sys, getopt, uuid, math, random
from FITSPhase1 import FITSPhase1
import numpy as np

def main(argv):
	maxClusters = 8
	msc = 8
	aRFSR = [60,100]
	num = str(uuid.uuid1())
	dataX = ''
	name2save = 'FITS_OUTPUT'
	maxAllowedLevel = 4
	try:
		opts, args = getopt.getopt(argv,"hi:o:l:")
	except getopt.GetoptError:
		print("main_FITS1.py -i <inputfile> -o <outputfile> -l <maxAllowedLevel>")
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print("main_FITS1.py -i <inputfile> -o <outputfile> -l <maxAllowedLevel>")
			sys.exit()
		elif opt in ("-i"):
			dataX = arg
		elif opt in ("-o"):
			name2save = arg
		elif opt in ("-l"):
			maxAllowedLevel = int(arg)
	if dataX == '':
		print("Input File is required!!")
		sys.exit()
	else:
		dataX1 = np.loadtxt(dataX, delimiter=",")
		dataX1 = np.transpose(dataX1)
		average = dataX1.mean(axis=1)
		dataX1 = dataX1/average[:, np.newaxis]+0.000001
		FITSPhase1(dataX1,maxClusters,msc,aRFSR,maxAllowedLevel,name2save,num)

if __name__ == "__main__":
	main(sys.argv[1:])
