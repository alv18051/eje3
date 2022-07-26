#Programa principal

from gl import *

rende = Renderer(1024,512)

rende.glClearColor(1,0,0)
rende.glColor(1,1,0)

rende.glClear()

rende.glPixel(50,75)

for i in range(300):
    rende.glPixel(i,i)

rende.glFinish("salida.bmp")