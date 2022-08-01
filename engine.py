#Programa principal
import random
from turtle import width
from gl import *
from obj import *
width = 1000  #alto de la pantalla
height = 1000 #ancho de la pantalla
rende = Renderer(height,width)


rende.glLoadModel('mod2.obj',translate=V3(width/2,height/2,0),scale=V3(10,10,10))


rende.glFinish("./salida.bmp")