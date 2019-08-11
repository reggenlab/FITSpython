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
		chunks = makechunks(dataX)
		for i in range(1,chunks['count']+1):
			dataX1 = np.loadtxt(dataX, delimiter=",")
			dataX1 = np.transpose(dataX1)
			average = dataX1.mean(axis=1)
			dataX1 = dataX1/average[:, np.newaxis]+0.000001
			data = dataX1[chunks['res'][i]['val'],:]
			del dataX1
			FITSPhase1(data,maxClusters,msc,aRFSR,maxAllowedLevel,'fitsL_'+name2save+'_'+str(i),num)
			indexes = chunks['res'][i]['val']
			np.savetxt('indexes_'+name2save+'_'+str(i)+'_'+num+'.txt',indexes)

def makechunks(dataX):
	dataX1 = np.loadtxt(dataX, delimiter=",")
	numberOfSamples = dataX1.shape[1]
	chunkSize = 1000
	v = range(0,numberOfSamples)
	rv = random.sample(v, len(v))
	nonOverlapChunks = math.ceil(numberOfSamples/chunkSize)
	res = {}
	start = 0
	count=0
	for i in range(1,nonOverlapChunks+1):
		res[i] = {}
		res[i]['val'] = {}
		if i!=nonOverlapChunks:
			res[i]['val'] = rv[start:start+chunkSize]
			start = start+chunkSize
		else:
			if i==1:
				res[i]['val'] = rv
				count=1
			else:
				if len(rv[start:numberOfSamples])>500:
					res[i]['val'] = rv[start:numberOfSamples]
					count = i
				else:
					count = i-1
					res[i-1]['val']=rv[start-chunkSize:numberOfSamples]
	overlapChunks = count
	if overlapChunks>15:
		overlapChunks=15
	for i in range(1,overlapChunks+1):
			res[i+count] = {}
			res[i+count]['val'] = random.sample(v,chunkSize)
	count = count+overlapChunks
	result = {}
	result['count'] = count
	result['res'] = res
	return result

if __name__ == "__main__":
	main(sys.argv[1:])
