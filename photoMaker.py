import os, json
from PIL import Image, ImageDraw

def getDirectory():
    stateFile = open('state.json', 'r')
    state = json.load(stateFile)
    stateFile.close()
    degree = state['Degree']
    path = 'Roots/Degree_' + str(degree)
    return path

def trans(point):
    x = 200*point[0] + 500
    y = 200*point[1] + 500
    return (x,y)

def createImage():
    im = Image.new('RGBA', (1000, 1000), (0,0,0,0))
    ctx = ImageDraw.Draw(im)
    points = []
    path = getDirectory()
    for fileName in os.listdir(path):
        filePath = path + '/' + fileName
        file = open(filePath, 'r')
        jsonDataFile = json.load(file)
        file.close()
        for polynomial in jsonDataFile:
            rawPoints = map(tuple,polynomial['Roots'])
            transPoints = map(trans, rawPoints)
            points += transPoints
        ctx.point(points, fill = (255, 0, 0, 150))
        points = []
    return im
