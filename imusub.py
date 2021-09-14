#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
from sensor_msgs.msg import Imu
import datetime

class subclass():
    def __init__(self):
        self.logoCiz()
        rospy.init_node("subNodetoIMU")
        rospy.Subscriber("/mavros/imu/data",Imu,self.imuCallBack)
        rospy.spin()
    def logoCiz(self):
            print('''
            - + - + @ @ @ - + - + - + -  + -
            - + - + - + -@ - + - + - + - + + 
            - + - + - + - @ - + - + - + -  +
            - + - + - + @  @ - + - + - + - +
            - + - + -  @ -  @ - - @ @  - + -
            - + - + - @      @ - @ - + - + -
            - - -@ @ @       @ @ - + - + - +
            - + - + - + Memoli - + - + - + -
            ''')
    def imuCallBack(self,mesaj):
        txtFile = open("imuVerileri.txt","a+")
        txtFile.write(str(datetime.datetime.now()))
        txtFile.write("Angular Velocity Verileri : ")
        txtFile.write("X : "+str(mesaj.angular_velocity.x)+"\n")
        txtFile.write("Y : "+str(mesaj.angular_velocity.y)+"\n")
        txtFile.write("Z : "+str(mesaj.angular_velocity.z)+"\n")
        txtFile.write("Linear Acceleration Verileri : "+"\n")
        txtFile.write("X : "+str(mesaj.linear_acceleration.x)+"\n")
        txtFile.write("Y : "+str(mesaj.linear_acceleration.y)+"\n")
        txtFile.write("Z : "+str(mesaj.linear_acceleration.z)+"\n")
        txtFile.write("Oryantasyon Verileri  :"+"\n")
        txtFile.write("X : "+str(mesaj.orientation.x)+"\n")
        txtFile.write("Y : "+str(mesaj.orientation.y)+"\n")
        txtFile.write("Z : "+str(mesaj.orientation.z)+"\n")
        txtFile.write("W : "+str(mesaj.orientation.w)+"\n")
        txtFile.write("---------------------------------------"+"\n")
        rospy.loginfo("Angular X : "+str(mesaj.angular_velocity.x)+"\n")
        rospy.loginfo("Angular Y : "+str(mesaj.angular_velocity.y)+"\n")
        rospy.loginfo("Angular Z : "+str(mesaj.angular_velocity.z)+"\n")

        
subNesne = subclass()

