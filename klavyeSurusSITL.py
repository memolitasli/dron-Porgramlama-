#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
from os import system
from queue import Empty
import struct
from sys import byteorder
import time
from tkinter.constants import CENTER, LEFT
from dronekit import VehicleMode, connect,LocationGlobalRelative,Vehicle,Command, mavlink
import argparse
from pymavlink import mavutil
import inputs
import tkinter as tk
import os
import datetime


#ucus hizi metre /saniye
gnd_speed = 5
modee      = 'GROUND'
parser = argparse.ArgumentParser(description='commands')
parser.add_argument('--connect')
parser.add_argument('--altitude')
args = parser.parse_args()
altitude= float(args.altitude)
connectionString = args.connect

drone = connect(connectionString,wait_ready=True)
print("Drona baglanildi...")

def armAndTakeOff(tgt_altitute):
    print("Cihazda herhangi bir sikinti yok, Arm haline getiriliyor...")
    while not drone.is_armable:
        time.sleep(1)
    drone.mode = VehicleMode('GUIDED')
    drone.armed = True
    print("Kalkis Basliyor...")
    drone.simple_takeoff(tgt_altitute)

    while True:
        altit= drone.location.global_relative_frame.alt
        print("Yukseklik (metre) : " + str(altit))
        if altit >= tgt_altitute:
            print("Istenilen yukseklige ulasildi...")
            break
        time.sleep(1)


def clear_mission(vehicle):

    cmds = vehicle.commands
    vehicle.commands.clear()
    vehicle.flush()

    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()

def download_mission(vehicle):

    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    

def get_current_mission(vehicle):

    print ("Gorev indiriliyor...")
    download_mission(vehicle)
    missionList = []
    n_WP        = 0
    for wp in vehicle.commands:
        missionList.append(wp)
        n_WP += 1 
        
    return n_WP, missionList
    
#görevin yuklendiği konumu en son geri gidilecek konum olarak ekliyor.
def add_last_waypoint_to_mission(                                
        vehicle,           
        wp_Last_Latitude,  
        wp_Last_Longitude,  
        wp_Last_Altitude):  

    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()

    missionlist=[]
    for cmd in cmds:
        missionlist.append(cmd)
    wpLastObject = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 
                           wp_Last_Latitude, wp_Last_Longitude, wp_Last_Altitude)
    missionlist.append(wpLastObject)

    cmds.clear()


    for cmd in missionlist:
        cmds.add(cmd)
    cmds.upload()
    
    return (cmds.count)    

def ChangeMode(vehicle, mode):
    while vehicle.mode != VehicleMode(mode):
            vehicle.mode = VehicleMode(mode)
            time.sleep(0.5)
    return True


def gorevBelirle(vehicle):

    ucusKayitlari = open("ucuskayit.txt","a+")
    ucusKayitlari.write(str(datetime.datetime.now()) + "\n")
    ucusKayitlari.close()
    mode='GROUND'
    while True:
        ucusKayitlari = open("ucuskayit.txt","a+")
        if mode == 'GROUND':
            
            n_WP, missionList = get_current_mission(vehicle)
            time.sleep(2)
            if n_WP > 0:
                ucusKayitlari.write(str(n_WP) + " Adet Nokta İşaretlendi... \n")
                for nokta in missionList:
                    ucusKayitlari.write(str(nokta) + "\n")
                print ("Gorev yuklendi, kalkisa geciliyor...")
                mode = 'TAKEOFF'
        
        elif mode == 'TAKEOFF':
            
            add_last_waypoint_to_mission(vehicle, vehicle.location.global_relative_frame.lat, 
                                       vehicle.location.global_relative_frame.lon, 
                                       vehicle.location.global_relative_frame.alt)
            for nokta in missionList:
                ucusKayitlari.write(str(nokta) + "\n")
            
            print("Hedef listesine ev konumu eklendi..")
            time.sleep(1)
            armAndTakeOff(10)
        
            print("AUTO moda gecildi...")
            ChangeMode(vehicle,"AUTO")
        
            vehicle.groundspeed = gnd_speed
            mode = 'MISSION'
            print ("Gorev moduna gecildi..")
        
        elif mode == 'MISSION':

            print ("Current WP: %d of %d "%(vehicle.commands.next, vehicle.commands.count))
            if vehicle.commands.next == vehicle.commands.count:
                print ("Son hedefe ulasildi, eve donuluyor...")               
                
                clear_mission(vehicle)
                print ("Mission deleted")
                ChangeMode(vehicle,"RTL")
                mode = "BACK"
            
        elif mode == "BACK":
            if vehicle.location.global_relative_frame.alt < 1:
                print ("Yer moduna gecildi...")
                mode = 'GROUND'
                ucusKayitlari.write("Gorev Tamamlama Tarihi : "+ str(datetime.datetime.now()))
                ucusKayitlari.close()
                secim = int(input("Su an yeni gorev ekleyebilirsiniz, gorev ekledikten sonra 1 e basiniz, 2->Cikis Yap"))
                if secim == 1:
                    time.sleep(2)
                    continue
                elif secim == 2:
                    return
        time.sleep(0.5)


def set_velocity_body(vehicle,vx,vy,vz):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
            0,
            0, 0,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            0b0000111111000111, 
            0, 0, 0,        
            vx, vy, vz,     
            0, 0, 0,        
            0, 0)
    vehicle.send_mavlink(msg)
    vehicle.flush()
def key(event):
    if event.char ==event.keysym:
        if event.keysym =='r':
            print("R tusuna basildi. Drone RTL Moduna Aliniyor...")
            drone.mode = VehicleMode('RTL')
        if event.keysym =='g':
            print("G tusuna basildi dron GUIDED moda aliniyor")
            drone.mode = VehicleMode("GUIDED")
        if event.keysym == 'l':
            print("Inis moduna geciliyor...")
            drone.mode = VehicleMode("LAND")
            while drone.location.global_relative_frame.alt> 0.2:
                
                time.sleep(1)
            secim = int(input("Dron yere inis yapti. \n 1->Tekrar Havalan , 2-> Gorev Belirle \n Secim : "))
            if secim == 1:
                irt = float(input("Irtifa Degeri : "))
                armAndTakeOff(irt)
            if secim == 2:
                gorevBelirle(drone)

        if event.keysym =='w':
            set_velocity_body(drone,0,0,-0.5)
        if event.keysym == 's':
            set_velocity_body(drone,0,0,0.5)
        if event.keysym =='b':
            print("Enlem : " + str(drone.location.global_relative_frame.lat))
            print("Boylam : " + str(drone.location.global_relative_frame.lon))
            print("Irtifa : " + str(drone.location.global_relative_frame.alt))

    else:
        secenekleriYazdir()
        if event.keysym == 'Up':
            set_velocity_body(drone,gnd_speed,0,0)
        elif event.keysym =='Down':
            set_velocity_body(drone,-gnd_speed,0,0)
        elif event.keysym =='Left':
            set_velocity_body(drone,0,-gnd_speed,0)
        elif event.keysym =='Right':
            set_velocity_body(drone,0,gnd_speed,0)
        os.system('cls||clear')

def printLambda():
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

def secenekleriYazdir():
    print("---Klavyede Bulunan Yon Tuslari Ile Dronu Hareket Ettirebilirsin")
    print("---W Tusu Ile Yukselebilir, S Tusu Ile Alcalabilirsin.")
    print("---B Tusuna Basarak Konum Bilgisi Alabilirsin")
    print("---L Tusuna Basarak Dronu Indirebilirsin, Daha Sonra Secim Yaparak Tekrar Yukselebilir veya Gorev Yukleyebilirsin.")
    print("---R Tusuna Basarak RTL Moduna Gecebilirsin.")


printLambda()
armAndTakeOff(altitude)
secenekleriYazdir()

window = tk.Tk()
window.title = "Robot Kontrol Merkezi"

window.bind_all('<Key>', key)
window.mainloop()
