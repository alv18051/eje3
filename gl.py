#Libreria de graficos
 

import struct #esta libreria si se puede usar
from collections import namedtuple
import numpy as np

from obj import Obj

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])
V4 = namedtuple('Point4', ['x', 'y', 'z', 'w'])

def char(c):
    #1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    #2 bytes
    return struct.pack('=h', w)

def dword(d):
    #4 bytes
    return struct.pack('=l', d)

def color(r, g, b):
    return bytes([int(b * 255),
                  int(g * 255),
                  int(r * 255)] )

class Renderer(object):
    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.clearColor = color(0,0,0)
        self.currColor = color(1,1,1)

        self.glViewport(0,0,self.width, self.height)
        
        self.glClear()

    def glViewport(self, posX, posY, width, height):
        self.vpX = posX
        self.vpY = posY
        self.vpWidth = width
        self.vpHeight = height

    def glClearColor(self, r, g, b):
        self.clearColor = color(r,g,b)

    def glColor(self, r, g, b):
        self.currColor = color(r,g,b)

    def glClear(self):
        self.pixels = [[ self.clearColor for y in range(self.height)]
                       for x in range(self.width)]

    def glClearViewport(self, clr = None):
        for x in range(self.vpX, self.vpX + self.vpWidth):
            for y in range(self.vpY, self.vpY + self.vpHeight):
                self.glPoint(x,y,clr)


    def glPoint(self, x, y, clr = None): # Window Coordinates
        if (0 <= x < self.width) and (0 <= y < self.height):
            self.pixels[x][y] = clr or self.currColor

    def glPoint_vp(self, ndcX, ndcY, clr = None): # NDC
        if ndcX < -1 or ndcX > 1 or ndcY < -1 or ndcY > 1:
            return

        x = (ndcX + 1) * (self.vpWidth / 2) + self.vpX
        y = (ndcY + 1) * (self.vpHeight / 2) + self.vpY

        x = int(x)
        y = int(y)

        self.glPoint(x,y,clr)

    def glCreateObjectMatrix(self, translate = V3(0,0,0), rotate = V3(0,0,0), scale = V3(1,1,1)):

        translation = np.matrix([[1, 0, 0, translate.x],
                                 [0, 1, 0, translate.y],
                                 [0, 0, 1, translate.z],
                                 [0, 0, 0, 1]])

        rotation = np.identity(4)

        scaleMat = np.matrix([[scale.x, 0, 0, 0],
                              [0, scale.y, 0, 0],
                              [0, 0, scale.z, 0],
                              [0, 0, 0, 1]])

        return translation * rotation * scaleMat

    def glTransform(self, vertex, matrix):

        v = V4(vertex[0], vertex[1], vertex[2], 1)
        vt = matrix @ v
        vt = vt.tolist()[0]
        vf = V3(vt[0] / vt[3],
                vt[1] / vt[3],
                vt[2] / vt[3])

        return vf



    def glLoadModel(self, filename, translate = V3(0,0,0), rotate = V3(0,0,0), scale = V3(1,1,1)):
        model = Obj(filename)
        modelMatrix = self.glCreateObjectMatrix(translate, rotate, scale)

        for face in model.faces:
            vertCount = len(face)
            for vert in range(vertCount):
                v0 = model.vertices[ face[vert][0] - 1]
                v1 = model.vertices[ face[(vert + 1) % vertCount][0] - 1]

                v0 = self.glTransform(v0, modelMatrix)
                v1 = self.glTransform(v1, modelMatrix)

                self.glLine(V2(v0.x, v0.y), V2(v1.x, v1.y))

    def glLine(self, v0, v1, clr = None):
        # Bresenham line algorithm
        # y = m * x + b
        x0 = int(v0.x)
        x1 = int(v1.x)
        y0 = int(v0.y)
        y1 = int(v1.y)

        # Si el punto0 es igual al punto 1, dibujar solamente un punto
        if x0 == x1 and y0 == y1:
            self.glPoint(x0,y0,clr)
            return

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        # Si la linea tiene pendiente mayor a 1 o menor a -1
        # intercambio las x por las y, y se dibuja la linea
        # de manera vertical
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        # Si el punto inicial X es mayor que el punto final X,
        # intercambio los puntos para siempre dibujar de 
        # izquierda a derecha       
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        limit = 0.5
        m = dy / dx
        y = y0

        for x in range(x0, x1 + 1):
            if steep:
                # Dibujar de manera vertical
                self.glPoint(y, x, clr)
            else:
                # Dibujar de manera horizontal
                self.glPoint(x, y, clr)

            offset += m

            if offset >= limit:
                if y0 < y1:
                    y += 1
                else:
                    y -= 1
                
                limit += 1

    def glTriangle_std(self, v0, v1, v2, clr = None):
        #scanline algorithm
        pass


    def glFinish(self, filename):
        with open(filename, "wb") as file:
            # Header
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write(dword(14 + 40))

            #InfoHeader
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            #Color table
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.pixels[x][y])

    
        
    
