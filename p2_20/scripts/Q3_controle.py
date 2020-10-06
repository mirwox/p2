#! /usr/bin/env python
# -*- coding:utf-8 -*-

# Sugerimos rodar com:
# roslaunch turtlebot3_gazebo  turtlebot3_empty_world.launch 


from __future__ import print_function, division
import rospy
import numpy as np
import cv2
from geometry_msgs.msg import Twist, Vector3
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, Vector3
import math
from math import pow, sqrt
import time
from tf import transformations


x = None
y = None

v = 0.4
w = 0.3

contador = 0
pula = 50
alpha = 0

zero = Twist(Vector3(0,0,0), Vector3(0,0,0))

def recebe_odometria(data):
    global x
    global y
    global contador
    global alpha

    x = data.pose.pose.position.x
    y = data.pose.pose.position.y

    quat = data.pose.pose.orientation
    lista = [quat.x, quat.y, quat.z, quat.w]
    angulos = np.degrees(transformations.euler_from_quaternion(lista))    
    alpha = math.radians(angulos[2])

    if contador % pula == 0:
        print("Posicao (x,y)  ({:.2f} , {:.2f}) + angulo {:.2f}".format(x, y,angulos[2]))
    contador = contador + 1

def go_to(x2, y2, pub):

    dist = sqrt(pow(x2 - x, 2) + pow(y2 - y, 2))

    while dist > 0.30:
        # calcular theta
        theta = math.atan2(y2-y, x2-x)

        # obter alpha da odometria e converter para rads
        angulo = theta - alpha

        print("angulo ", angulo)

        # girar theta - alpha para a esquerda
        tempo = angulo / w

        vel = Twist(Vector3(0,0,0), Vector3(0,0,w))

        pub.publish(vel)
        rospy.sleep(tempo)
        pub.publish(zero)
        rospy.sleep(0.5)

        # calcula d = pitagoras x2 y2 x y
        d = sqrt(pow(x2 - x, 2) + pow(y2 - y, 2))

        # andar d
        t = d/v

        vel = Twist(Vector3(v,0,0), Vector3(0,0,0))
        pub.publish(vel)
        rospy.sleep(t)
        pub.publish(zero)
        rospy.sleep(0.5)
        # verifico se estou a menos de 0.30m do alvo
        dist = sqrt(pow(x2 - x, 2) + pow(y2 - y, 2))
        print("Dist", dist)
    


if __name__=="__main__":

    rospy.init_node("q3")

    




    pub = rospy.Publisher("/cmd_vel", Twist, queue_size = 3 )

    ref_odometria = rospy.Subscriber("/odom", Odometry, recebe_odometria)


    rospy.sleep(1.0) # contorna bugs de timing    



    x2 = 3
    y2 = 2


    while not rospy.is_shutdown():
        go_to(x2,y2, pub)
        print("x y ", x, y)
        pub.publish(zero)
        rospy.sleep(0.5)
