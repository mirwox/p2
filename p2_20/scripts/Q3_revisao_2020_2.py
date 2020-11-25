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
import time
from tf import transformations


x = None
y = None

contador = 0
pula = 50

angle_z = None

w = 0.15
v = 0.2

gira = Twist(Vector3(0,0,0), Vector3(0,0,w))
frente = Twist(Vector3(v,0,0), Vector3(0,0,0))
zero = Twist(Vector3(0,0,0), Vector3(0,0,0))

def recebe_odometria(data):
    global x
    global y
    global contador
    global angle_z


    x = data.pose.pose.position.x
    y = data.pose.pose.position.y

    quat = data.pose.pose.orientation
    lista = [quat.x, quat.y, quat.z, quat.w]

    radians = transformations.euler_from_quaternion(lista)
    angle_z = radians[2]
    angulos = np.degrees(radians)

    if contador % pula == 0:
        print("Posicao (x,y)  ({:.2f} , {:.2f}) + angulo {:.2f}".format(x, y,angulos[2]))
    contador = contador + 1


def go_to(x2, y2, pub):
    x1 = x
    y1 = y
    theta_1 = angle_z

    delta_x = x2 - x1
    delta_y = y2 - y1

    theta_2 = math.atan2(delta_y, delta_x)

    delta_theta = theta_2 - theta_1

    print("delta theta {}".format(delta_theta))

    t_rot = delta_theta/w

    # Gira em malha aberta
    pub.publish(gira)
    rospy.sleep(t_rot)

    dist = math.sqrt(delta_x**2 + delta_y**2)

    t_trans = dist/v
    pub.publish(frente)
    rospy.sleep(t_trans)
    pub.publish(zero)
    rospy.sleep(0.2)

    # Checar se a distancia e menor que 30 cm
    x_final = x
    y_final = y

    tolerancia = math.sqrt((x2 - x_final)**2 + (y2 - y_final)**2)
    
    if tolerancia > 0.3:
        print('tolerancia {}'.format(tolerancia))
        print("Rodando de novo")
        go_to(x2, y2, pub)
    else:
        print("Terminei")
        return





if __name__=="__main__":

    rospy.init_node("q3")

    lado = 1.5

    goal_x = [lado/2.0, 0, -lado/2.0]
    goal_y = [0, math.sqrt(3.0)*lado/2, 0] 


    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 3 )

    ref_odometria = rospy.Subscriber("/odom", Odometry, recebe_odometria)


    rospy.sleep(1.0) # contorna bugs de timing    

    while not rospy.is_shutdown():

        for i in range(len(goal_x)):
            print("{},{}".format(goal_x[i],goal_y[i]))            
            go_to(goal_x[i],goal_y[i], velocidade_saida)  
            rospy.sleep(0.1)
        break   
        rospy.sleep(0.5)    
