#! env/bin/python
import numpy as np
import json
import os, sys, argparse


import photoMaker

# Store complex numbers in json
def encode_complex(z):
	if isinstance(z, complex):
		return (z.real,z.imag)
	else:
		type_name = z.__class_.__name__
		raise TypeError("Object of type '{type_name}' is not JSON serializable")

# Convert binary lwp to lwp
def zeroToMinusOne(x):
	if x == 0:
		return -1
	else:
		 return x

# Returns array of roots of lwp with given degree and ConnectionAbortedError
def rootsOf(coeffCode, degree):
	degreeCode = '0'+str(degree+1)+'b'
	coefficientsStringArray = list(format(coeffCode, degreeCode))
	coefficients = [zeroToMinusOne(int(coeff)) for coeff in coefficientsStringArray]
	return np.roots(coefficients)

def appendRootsOf(coeffCode, degree, rootsArray):
	roots = list(rootsOf(coeffCode, degree))
	rootsArray.append({
	'CoeffCode' : coeffCode,
	'Degree' : degree,
	'Roots' : roots
	})

def maxCoeffCodeForDegree(degree):
	return ( 2 ** (degree + 1) ) - 1

class App:
	def __init__(self):
		self.blockBuffer = []
		self.blocksProcessed = 0
		if (os.path.isdir('Roots') == False):
			os.mkdir('Roots')
		self.finishedDegree = False
		stateFileExists = os.path.isfile('state.json') # state.json stores the last worked polynomials code and degree.
		if (stateFileExists == False):
			state = {'Degree' : 1, 'CoeffCode' :  0}
			file = open('state.json', 'w')
			json.dump(state, file)
			file.close()
		stateFile = open('state.json')
		self.state = json.load(stateFile)
		stateFile.close()
		maxCoeffCode = maxCoeffCodeForDegree(self.state['Degree'])
		if (self.state['CoeffCode'] == maxCoeffCode):
			self.degree = self.state['Degree'] + 1
			self.coeffCode = 0
		else:
			self.degree = self.state['Degree']
			self.coeffCode = self.state['CoeffCode']
		self.maxCoeffCode = maxCoeffCodeForDegree(self.degree)
		self.blockNumber = self.coeffCode // 20
		self.directoryPath = 'Roots/Degree_' + str(self.degree)
		self.outputBufferName = 'block_' + str(self.blockNumber) + '.json'
		self.outputPath = self.directoryPath + '/' + self.outputBufferName
		if (os.path.isdir(self.directoryPath) == False):
			os.mkdir(self.directoryPath)

	def flushBuffer(self):
		file = open(self.outputPath, 'w')
		json.dump(self.blockBuffer, file, default=encode_complex)
		file.close()
		self.blockBuffer = []
		self.outputBufferName = 'block_' + str(self.blockNumber) + '.json'
		self.outputPath = self.directoryPath + '/' + self.outputBufferName

	def flushState(self):
		stateFile = open('state.json', 'w')
		self.state = {'Degree' : self.degree, 'CoeffCode' : self.coeffCode - 1}
		json.dump(self.state, stateFile)
		stateFile.close()

	def nextDegree(self):
		self.degree += 1
		self.coeffCode = 0
		self.maxCoeffCode = maxCoeffCodeForDegree(self.degree)
		self.blockNumber = 0
		self.finishedDegree = False
		self.state = {'Degree' : self.degree, 'CoeffCode' : 0}

	def fillBlockBuffer(self):
		for code in range(self.coeffCode, self.coeffCode + 20):
			if (code <= self.maxCoeffCode):
				appendRootsOf(code, self.degree, self.blockBuffer)
			else:
				self.finishedDegree = True
				break
		print('Filled block buffer with ' + str(len(self.blockBuffer)) + ' polys.')

	def updateState(self):
		self.directoryPath = 'Roots/Degree_' + str(self.degree)
		if (os.path.isdir(self.directoryPath) == False):
			os.mkdir(self.directoryPath)
		self.outputBufferName = 'block_' + str(self.blockNumber) + '.json'
		self.outputPath = self.directoryPath + '/' + self.outputBufferName
		self.coeffCode += len(self.blockBuffer)
		self.blockNumber += 1
		self.blocksProcessed += 1
		self.flushState()
		if (self.finishedDegree == True):
			self.nextDegree()

	def run(self, count):
		while(self.blocksProcessed < count):
			self.fillBlockBuffer()
			self.updateState()
			self.flushBuffer()
			print('Just finished block ' + str(self.blocksProcessed) + '\n')

	def parseArgs(self, args=None):
		parser = argparse.ArgumentParser()
		parser.add_argument('--progress', help = 'Display the last saved polynomials code and degree', action = 'store_true')
		parser.add_argument('--render', help = 'Create an image of the roots.', action = 'store_true')
		parser.add_argument('--split', help = 'Split a given number of blocks.', type = int, nargs = 1)
		return parser.parse_args(args)

	def processArgs(self, args):
		if args.progress:
			stateFile = open('state.json', 'r')
			state = json.load(stateFile)
			stateFile.close()
			outputString = 'Last polynomial to be split: Degree = ' + str(state['Degree']) + ' ,  Coeff. Code = ' + str(state['CoeffCode'])
			print(outputString)

		if args.render:
			image = photoMaker.createImage()
			stateFile = open('state.json', 'r')
			state = json.load(stateFile)
			stateFile.close()
			fileName = 'render_D'+str(state['Degree'])+'_C'+str(state['CoeffCode'])+'.png'
			image.save(fileName,'PNG')
			print('Render was succesful! Saved image as ' + fileName)

		if args.split:
			count = args.split[0]
			print('Preparing to split' + str(count) + ' blocks.\n')
			self.run(count)


	def main(self):
		args = self.parseArgs(sys.argv[1:])
		self.processArgs(args)

if __name__ == "__main__":
	app = App()
	app.main()
