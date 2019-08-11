import sys, getopt
from FITSPhase2 import FITSPhase2
def main(argv):
	dataX = ''
	topk = 3
	colwise = 0
	name2save = 'FITS_OUTPUT'
	try:
		opts, args = getopt.getopt(argv,"hi:o:t:c:")
	except getopt.GetoptError:
		print("main_FITS2.py -i <inputfile> -o <outputfile> -t <topk> -c <FeatureWise/SampleWise>")
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print("main_FITS2.py -i <inputfile> -o <outputfile> -t <topk> -c <colwise/SampleWise>")
			sys.exit()
		elif opt in ("-i"):
			dataX = arg
		elif opt in ("-o"):
			name2save = arg
		elif opt in ("-t"):
			topk = int(arg)
		elif opt in ("-c"):
			colwise = int(arg)
	if dataX == '':
		print("Input file is required!!")
	else:
		FITSPhase2(dataX, topk, colwise, name2save)
if __name__ == "__main__":
	main(sys.argv[1:])
