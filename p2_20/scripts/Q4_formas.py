#! /usr/bin/env python
# -*- coding:utf-8 -*-
# Sugerimos rodar com:
# roslaunch my_simulation formas.launch

# Solução pode ser vista em     https://youtu.be/hxMqlZmcrXk

from __future__ import print_function, division
import rospy

import numpy as np

from numpy import array, uint8

import cv2

from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge, CvBridgeError

import math


ranges = None
minv = 0
maxv = 10

distancia = 100

bridge = CvBridge()



## 

goal = "blue"  # se este código vai centralizar e se aproximar do azul ou do verde

###

# Código extraído do notebook  que está na pasta Q4, em
#  https://github.com/mirwox/p2/blob/solution/q4/Q4.ipynb


# Limiares obtidos via color picker
# NOTE QUE ESTES VALORES FORAM EXPANDIDOS EM RELAÇÂO AO NOTEBOOK
g1, g2 = (array([45, 80, 20], dtype=uint8), array([ 65, 255, 255], dtype=uint8))
b1, b2 = (array([105,  80,  20], dtype=uint8), array([125, 255, 255], dtype=uint8))

def mask(hsv, a1, a2):
    return cv2.inRange(hsv, a1, a2)


def auto_canny(image, sigma=0.5):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    #image = cv2.blur(image, ksize=(5,5)) # blur se necessário
    #cv2.imshow("filter", image)
    #cv2.waitKey(0)
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged


def maior_circulo(mask, color):
    """ Retorna os dados do maior círculo existente na imagem. E uma imagem com este círculo desenhado"""
    tem_circulo = False
    maior_centro = (0,0)
    maior_raio = 0
    
    bordas = auto_canny(mask)
    
    # acumulador levemente ajustado
    circles=cv2.HoughCircles(image=bordas,method=cv2.HOUGH_GRADIENT,dp=2.2,minDist=250,param1=50,param2=100,minRadius=30,maxRadius=250)
    
    
    bordas_bgr = cv2.cvtColor(bordas, cv2.COLOR_GRAY2RGB)

    output =  bordas_bgr

    if circles is not None:        
        circles = np.uint16(np.around(circles))
        
        for i in circles[0,:]:
            tem_circulo = True
            # draw the outer circle
            cv2.circle(output,(i[0],i[1]),i[2],color,2)
            # draw the center of the circle
            cv2.circle(output,(i[0],i[1]),2,color,3)
            if i[2] > maior_raio:
                maior_centro = (int(i[0]), int(i[1]))
                                
    return tem_circulo, maior_centro, maior_raio, output


def processa_circulos_controle(img_bgr):
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    blue = mask(hsv, b1,b2)
    green = mask(hsv, g1, g2)
    cor_b = (255,0,0)
    cor_g = (0,255,0)
    tem_blue, centro_b, raio_n, img_b = maior_circulo(blue, cor_b)
    tem_green, centro_g, raio_g, img_g = maior_circulo(green, cor_g)
    
    delta_blue = centro_b[0] - 320 # quão afastado está do centro da tela de 640 x 480
    delta_green = centro_g[0] - 320 # quão afastado está do centro da tela de 640 x 480
    return tem_green, delta_green, img_g, tem_blue, delta_blue, img_b

# Variaveis de controle

circle_visible = False
circle_delta = 0


### Fim do trecho inserido no gabarito


def scaneou(dado):
    global ranges
    global minv
    global maxv
    global distancia
    print("Faixa valida: ", dado.range_min , " - ", dado.range_max )
    print("Leituras:")
    ranges = np.array(dado.ranges).round(decimals=2)
    minv = dado.range_min 
    maxv = dado.range_max
    for m in ranges[0: 5]:
        if minv < m < maxv:
            if m < distancia:
                distancia = m    
    for m in ranges[355: 360]:
        if minv < m < maxv:  
            if m < distancia:
                distancia = m                  
 
# A função a seguir é chamada sempre que chega um novo frame
def roda_todo_frame(imagem):
    global circle_visible
    global circle_delta
    print("frame")
    try:
        cv_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        cv2.imshow("Camera", cv_image)
        tem_green, delta_green, img_g, tem_blue, delta_blue, img_b = processa_circulos_controle(cv_image)

        if goal == "blue":
            circle_visible = tem_blue
            circle_delta = delta_blue
            cv2.imshow("Blue", img_b)        
            cv2.waitKey(1)                        
        if goal == "green":
            circle_visible = tem_green
            circle_delta = delta_green
            cv2.imshow("Green", img_g)
            cv2.waitKey(1)            





    except CvBridgeError as e:
        print('ex', e)

if __name__=="__main__":

    rospy.init_node("q4")

    topico_imagem = "/camera/rgb/image_raw/compressed"
    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 3 )
    recebe_scan = rospy.Subscriber("/scan", LaserScan, scaneou)
    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)

    delta_tolerance = 5
    dist_tolerance = 0.1
    metro = 1.0


    rot = Twist(Vector3(0,0,0), Vector3(0,0,0.1))
    frente = Twist(Vector3(0.2,0,0), Vector3(0,0,0))
    zero = Twist(Vector3(0,0,0), Vector3(0,0,0))
    
    PROCURANDO, CENTRALIZANDO, AVANCANDO, PARADO = 1,2,3,4

    state = PROCURANDO

    # Evitando bugs em algun setups
    velocidade_saida.publish(zero)
    rospy.sleep(1.0)

    def printstate(state):
        if state == PROCURANDO:
            print("PROCURANDO")
        if state == CENTRALIZANDO:
            print("CENTRALIZANDO")            
        if state == AVANCANDO:
            print("AVANCANDO")            
        if state == PARADO:
            print("PARADO")                        

    dt = 0.05

    while not rospy.is_shutdown():
        printstate(state)
        if state == PROCURANDO:
            velocidade_saida.publish(rot)
            if circle_visible == True:
                state = CENTRALIZANDO
                velocidade_saida.publish(zero)                
                rospy.sleep(dt)                
        if state == CENTRALIZANDO:          
            print("Delta", circle_delta)
            atuacao = -circle_delta/275.0*0.3
            rot = Twist(Vector3(0,0,0), Vector3(0,0,atuacao))
            velocidade_saida.publish(rot)            
            if abs(circle_delta) < delta_tolerance:
                state = AVANCANDO
                velocidade_saida.publish(zero)              
                rospy.sleep(dt)
        if state == AVANCANDO:
            velocidade_saida.publish(frente)
            if metro - dist_tolerance < distancia < metro + dist_tolerance:
                state = PARADO
                velocidade_saida.publish(zero)
                rospy.sleep(dt)
        if state == PARADO:
            velocidade_saida.publish(zero)

        rospy.sleep(dt)