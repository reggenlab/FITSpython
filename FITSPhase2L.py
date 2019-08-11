import sys, getopt, glob, os
import numpy as np
from scipy.stats import spearmanr
import traceback
def main(argv):
	dataX = ''
	topk = 3
	colwise = 0
	name2save = 'FITS_OUTPUT'
	try:
		opts, args = getopt.getopt(argv,"hi:o:t:c:")
	except getopt.GetoptError:
		print("main_FITS2.py -i <inputfile> -o <outputfile> -t <topk>")
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print("main_FITS2.py -i <inputfile> -o <outputfile> -t <topk>")
			sys.exit()
		elif opt in ("-i"):
			dataX = arg
		elif opt in ("-o"):
			name2save = arg
		elif opt in ("-t"):
			topk = int(arg)
	if dataX == '':
		print("Input file is required!!")
	else:
		dataX1 = np.loadtxt(dataX, delimiter=",")
		dataX1 = np.transpose(dataX1)
		average = dataX1.mean(axis=1)
		dataX1 = dataX1/average[:, np.newaxis]+0.000001
		dataX1 = np.log(dataX1+1.01)
		corrStruct = {}
		for i in range(dataX1.shape[0]):
			corrStruct[i] = {}
			corrStruct[i]['val'] = []
			corrStruct[i]['tree'] = []
			corrStruct[i]['isR'] = []
			corrStruct[i]['index'] = []
			corrStruct[i]['row'] = {}
			corrStruct[i]['found'] = 0
		index_files = 'indexes_'+name2save+'_*.txt'
		file_dict = {}
		start = 1
		for t in glob.glob(index_files):
			try:
				obj = np.loadtxt(t, delimiter=",")
				obj = obj.astype(int)
				file_dict[start] = {}
				file_dict[start]['val'] = obj
				c = os.path.splitext(os.path.basename(t))[0]
				c = c.split("_",1)[1]
				file_dict[start]['name'] = c
				file_dict[start]['rfile'] = 0
				file_dict[start]['file'] = 0
				try:
					mc = file_dict[start]['name'].split('_')
					formed_file_name = 'fitsL_'+file_dict[start]['name']+'.npy'
					obj1 = np.load(formed_file_name)
					if(np.isnan(obj1).sum()==0):
						file_dict[start]['file'] = 1
						file_dict[start]['filename'] = formed_file_name
						# print(formed_file_name)
						corrCalc(dataX1,obj1,file_dict[start]['val'],corrStruct,topk,start,0)
						file_dict[start]['val'] = 0
				except:
					print(formed_file_name)
					print("This is either corrupted or not exist")
				for r in range(3,7):
					try:
						mc1 = file_dict[start]['name'].rsplit("_",1)[0]
						formed_file_name = 'fitsL_'+mc1+'_r_'+str(r)+'.npy'
						obj1 = np.load(formed_file_name)
						if(np.isnan(obj1).sum()==0):
							file_dict[start]['rfile'] = r
							file_dict[start]['rfileName'] = formed_file_name
							corrCalc(dataX1,obj1,file_dict[start]['val'],corrStruct,topk,start,1)
							file_dict[start]['val'] = 0
					except:
						print(" ")
				start = start+1
			except:
				print(t)
				print("This is either corrupted or not exist")
		total = start-1
		matrixUsage = {}
		for i in range(1,total+1):
			matrixUsage[i] = {}
			matrixUsage[i]['normal'] = []
			matrixUsage[i]['r'] = []
			matrixUsage[i]['normali'] = []
			matrixUsage[i]['ri'] = []
		fillMatrixUsage(matrixUsage,corrStruct,dataX1.shape[0])
		matrixFormation(dataX1.shape[0],dataX1.shape[1],file_dict,matrixUsage,corrStruct,name2save,total)
		# maxCorrelated(dataX1,file_dict,total,topk,name2save)

def fillMatrixUsage(matrixUsage,corrStruct,count):
	for i in range(0,count):
		for j in range(len(corrStruct[i]['val'])):
			if(corrStruct[i]['isR'][j] == 0):
				matrixUsage[corrStruct[i]['tree'][j]]['normal'].append(i)
				matrixUsage[corrStruct[i]['tree'][j]]['normali'].append(corrStruct[i]['index'][j])
			else:
				matrixUsage[corrStruct[i]['tree'][j]]['r'].append(i)
				matrixUsage[corrStruct[i]['tree'][j]]['ri'].append(corrStruct[i]['index'][j])


def corrCalc(dataX1,Xrec,indexes,corrStruct,topk,num,isR):
	n = indexes.shape[0]
	for i in range(0,n):
		index = indexes[i]
		cor, pval = spearmanr(np.transpose(dataX1[index,:]),np.transpose(Xrec[i,:]))
		if(len(corrStruct[index]['val'])<topk):
			corrStruct[index]['val'].append(cor)
			corrStruct[index]['tree'].append(num)
			corrStruct[index]['isR'].append(isR)
			corrStruct[index]['index'].append(i)
		else:
			ind = np.argmin(corrStruct[index]['val'])
			corrStruct[index]['val'][ind] = cor
			corrStruct[index]['tree'][ind] = num
			corrStruct[index]['isR'][ind] = isR
			corrStruct[index]['index'][ind] = i

def matrixFormation(m,n,mtree,matrixUsage,corrStruct,name2save,total):
	newMatrix = np.zeros((m,n))
	for i in range(1,total+1):
		if(len(matrixUsage[i]['normal'])>0):
			obj = np.load(mtree[i]['filename'])
			for j in range(len(matrixUsage[i]['normal'])):
				sample = matrixUsage[i]['normal'][j]
				index = matrixUsage[i]['normali'][j]
				corrStruct[sample]['row'][1+corrStruct[sample]['found']] = {}
				corrStruct[sample]['row'][1+corrStruct[sample]['found']]['val'] = obj[index,:]
				corrStruct[sample]['found'] = corrStruct[sample]['found'] + 1
				if(corrStruct[sample]['found'] == len(corrStruct[sample]['val'])):
					nm = np.zeros((corrStruct[sample]['found'],n))
					for k in range(1,corrStruct[sample]['found']):
						nm[k,:] = corrStruct[sample]['row'][k]['val']
						corrStruct[sample]['row'][k]['val'] = 0
					newMatrix[sample,:] = np.max(nm,axis=0)
		if(len(matrixUsage[i]['r'])>0):
			obj = np.load(mtree[i]['rfileName'])
			for j in range(matrixUsage[i]['r'].shape[2]):
				sample = matrixUsage[i]['r'][j]
				index = matrixUsage[i]['ri'][j]
				corrStruct[sample]['row'][1+corrStruct[sample]['found']]['val'] = obj[index,:]
				corrStruct[sample]['found'] = corrStruct[sample]['found'] + 1
				if(corrStruct[sample]['found'] == corrStruct[sample]['val'].shape[1]):
					nm = np.zeros((corrStruct[sample]['found'],n))
					for k in range(1,corrStruct[sample]['found']):
						nm[k,:] = corrStruct[sample]['row'][k]['val']
						corrStruct[sample]['row'][k]['val'] = 0
					newMatrix[sample,:] = np.max(nm,axis=0)
	np.savetxt(name2save+'.txt', np.transpose(newMatrix), delimiter = ",")

def maxCorrelated(mOriginal,mtree,count,topk,name2save):
	final_imputed=maxCorrelatedRow(mOriginal,mtree,count,topk)
	final_imputed = np.transpose(final_imputed)
	np.savetxt(name2save+'.txt', final_imputed, delimiter = ",")

def maxCorrelatedRow(mOriginal,mtree,count,topk):
	res = np.zeros((mOriginal.shape[0], mOriginal.shape[1]))
	for i in range(mOriginal.shape[0]):
		print(i)
		corrAll = []
		start = 1
		ntree = {}
		findk = 0
		for j in range(1, count + 1):
			if(np.where(mtree[j]['val'] == i)[0]>0):
				findex = np.where(mtree[j]['val'] == i)[0]
				if(mtree[j]['rfile']>0):
					findk = findk+1
					obj=np.load(mtree[j]['rfileName'])
					ntree[start]={}
					ntree[start]['val']=obj[findex,:]
					ntree[start]['val'] = np.transpose(ntree[start]['val'])
					morig = mOriginal[i,:]
					morig = morig.reshape(morig.shape[0],-1)
					cor, pval = spearmanr(ntree[start]['val'],morig)
					# cor, pval = spearmanr(ntree[start]['val'], mOriginal[i, :])
					corrAll = np.append(corrAll,cor)
					start = start+1
				if(mtree[j]['file']>0):
					findk = findk+1
					obj = np.load(mtree[j]['filename'])
					ntree[start]={}
					ntree[start]['val']=obj[findex,:]
					ntree[start]['val'] = np.transpose(ntree[start]['val'])
					morig = mOriginal[i,:]
					morig = morig.reshape(morig.shape[0],-1)
					cor, pval = spearmanr(ntree[start]['val'],morig)
					# cor,pval = spearmanr(ntree[start]['val'], mOriginal[i, :])
					corrAll = np.append(corrAll,cor)
					start = start+1
		indices = np.argsort(corrAll)[::-1]
		if findk>topk:
			findk=topk
		newMatrix =  np.zeros((findk, mOriginal.shape[1]))
		for j in range(findk):
			newMatrix[j,:]=np.ravel(ntree[indices[j]+1]['val'])
		res[i,:] = np.max(newMatrix)
	return res

if __name__ == "__main__":
	main(sys.argv[1:])
