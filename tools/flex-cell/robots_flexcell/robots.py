import numpy as np
import os
import time
from spatialmath import SE3
from spatialmath.base import trnorm
import roboticstoolbox as rtb
from numpy import pi
import random
import csv
import paho.mqtt.client as mqtt
import zmq

# kuka DH parameters
class KukaLBR(rtb.DHRobot):
    def __init__(self):
        d1 = 0.340
        d3 = 0.4
        d5 = 0.4
        d7 = 0.126+0.035
        L1 = rtb.RevoluteMDH(d=d1, a=0, alpha=0)
        L2 = rtb.RevoluteMDH(d=0, a=0, alpha=-pi/2)
        L3 = rtb.RevoluteMDH(d=d3, a=0, alpha=pi/2)
        L4 = rtb.RevoluteMDH(d=0, a=0, alpha=pi/2)
        L5 = rtb.RevoluteMDH(d=d5, a=0, alpha=-pi/2)
        L6 = rtb.RevoluteMDH(d=0, a=0, alpha=-pi/2)
        L7 = rtb.RevoluteMDH(d=d7, a=0, alpha=pi/2)
        super().__init__([L1, L2, L3, L4, L5, L6, L7],name="KUKA")

class UR5e(rtb.DHRobot):
    def __init__(self):
        L1 = rtb.RevoluteMDH(d=0.1625, a=0, alpha=0)
        L2 = rtb.RevoluteMDH(d=0, a=0, alpha=pi/2)
        L3 = rtb.RevoluteMDH(d=0, a=-0.425, alpha=0) # changed a to negative
        L4 = rtb.RevoluteMDH(d=0.1333, a=-0.3922, alpha=0) # changed a to negative
        L5 = rtb.RevoluteMDH(d=0.0997, a=0, alpha=pi/2)
        L6 = rtb.RevoluteMDH(d=0.0996, a=0, alpha=-pi/2)
        #L1 = rtb.RevoluteMDH(d=0.1625, a=0, alpha=pi/2)
        #L2 = rtb.RevoluteMDH(d=0, a=0, alpha=0)
        #L3 = rtb.RevoluteMDH(d=0, a=0.425, alpha=0)
        #L4 = rtb.RevoluteMDH(d=0.1333, a=0.3922, alpha=pi/2)
        #L5 = rtb.RevoluteMDH(d=0.0997, a=0, alpha=-pi/2)
        #L6 = rtb.RevoluteMDH(d=0.0996, a=0, alpha=0)
        super().__init__([L1, L2, L3, L4, L5, L6],name="UR5e")


class KukaLBR_RL(KukaLBR):
    def __init__(self,motion_time=2.0,mqtt_enabled=False,mqtt_address="127.0.0.1",mqtt_port=1883,zmq_enabled=False,zmq_port=5557):
        self.prev_q0 = 0
        self.prev_q1 = 0
        self.prev_q2 = 0
        self.prev_q3 = 0
        self.prev_q4 = 0
        self.prev_q5 = 0
        self.prev_q6 = 0
        self.actual_q0 = 0
        self.actual_q1 = 0
        self.actual_q2 = 0
        self.actual_q3 = 0
        self.actual_q4 = 0
        self.actual_q5 = 0
        self.actual_q6 = 0
        self.target_q0 = 0
        self.target_q1 = 0
        self.target_q2 = 0
        self.target_q3 = 0
        self.target_q4 = 0
        self.target_q5 = 0
        self.target_q6 = 0
        self.is_busy = False
        self.mqtt_enabled = mqtt_enabled
        self.motion_time = motion_time
        self.n_steps_motion = int(self.motion_time/0.05)
        if self.mqtt_enabled:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.connect(mqtt_address, mqtt_port, 60)
            self.mqtt_client.loop_start()
        self.zmq_enabled = zmq_enabled
        if self.zmq_enabled:
            self.zmq_context = zmq.Context()
            self.socket_zmq = self.zmq_context.socket(zmq.PUB)
            try:
                self.socket_zmq.bind("tcp://*:" + str(zmq_port))
            except zmq.error.ZMQError as exc:
                print ("zmq socket kuka already in use, try restarting it")
                print(exc)
        super().__init__()

    def compute_ik_num(self,x,y,z,rounded=False):
        T = SE3(trnorm(np.array([[np.cos(-np.pi),0,np.sin(-np.pi),x],[0,1,0,y],[np.sin(-np.pi),0,np.cos(-np.pi),z],[0,0,0,1]]))) # Rotation of pi around the y-axis
        sol1 = self.ikine_LM(T,q0=[0,0,0,-np.pi/2,0,np.pi/2,0])
        if (sol1.success):
            solution1 = sol1.q
            if (rounded):
                solution1 = np.round(solution1,2)
            return solution1
        return np.nan

    def compute_ik_validity(self,x,y,z,rounded=False):
        T = SE3(trnorm(np.array([[np.cos(-np.pi),0,np.sin(-np.pi),x],[0,1,0,y],[np.sin(-np.pi),0,np.cos(-np.pi),z],[0,0,0,1]]))) # Rotation of pi around the y-axis
        sol1 = self.ikine_LM(T,q0=[0,0,0,-np.pi/2,0,np.pi/2,0])
        sol1_feasible = sol1.success
        sol2 = self.ik_lm_chan(T,q0=[0,0,0,0,0,np.pi,0])
        sol2_feasible = sol2.success
        if (not sol1_feasible and not sol2_feasible):
            return False
        return True

    def compute_xyz_flexcell(self,X,Y,Z=0,rx=0,ry=0,rz=0):
        ## Inversed axis, (x->y,y->x)
        #Z_table_level = 0.20
        Z_table_level = 0.25
        #Z_table_level = 0.05
        YMIN = 0
        YMAX = 23
        XMIN = 0
        XMAX = 15
        HOLE_DIST = 0.05
        x_min = -0.35
        x_max = 0.6#0.45
        y_min = -0.145
        y_max = 1.055
        #comp_x = x_max - ((X)*HOLE_DIST)
        #comp_y = y_min + ((Y)*HOLE_DIST)
        comp_x = (x_max - ((X)*HOLE_DIST))
        comp_y = (y_min + ((Y)*HOLE_DIST))
        comp_z = Z_table_level + Z * HOLE_DIST
        rx = rx
        ry = ry
        rz = rz

        return comp_x,comp_y,comp_z

    def compute_inverse_xyz_flexcell(self,x,y,z,rx=0,ry=0,rz=0):
        ## Inversed axis, (x->y,y->x)
        #Z_table_level = 0.20
        Z_table_level = 0.25
        #Z_table_level = 0.05
        YMIN = 0
        YMAX = 23
        XMIN = 0
        XMAX = 15
        HOLE_DIST = 0.05
        x_min = -0.35
        x_max = 0.6#0.45
        y_min = -0.145
        y_max = 1.055

        X = (x_max - x)/HOLE_DIST
        Y = (y - y_min)/HOLE_DIST
        Z = (z - Z_table_level)/HOLE_DIST

        return round(X),round(Y),round(Z)

    def compute_q(self,x,y,z):
        solution1 = self.compute_ik_num(x,y,z,rounded=False)
        if (solution1 is not np.nan):
            return np.array([solution1])

    def compute_trajectory(self,q_actual,q_target,n_steps=None,plot=False):
        if n_steps == None:
            n_steps = self.n_steps_motion
        q_traj = rtb.jtraj(q_actual, q_target, n_steps)
        if plot:
            self.plot(q_traj.q, backend='pyplot', movie='kuka.gif')
        return q_traj.q

    def transmit_robot_motion(self,q,use_real_robot=False):
        if len(q.shape) == 2:
            for i in range(len(q)):
                joint_pos = q[i]
                if use_real_robot:
                    #q_degrees = np.degrees(np.array(joint_pos))
                    #kuka_robot.move_ptp_rad(q=q_degrees) #TO BE IMPLEMENTED
                    pass
                for j in range(len(joint_pos)):
                    if self.mqtt_enabled:
                        self.send_mqtt_string(f"actual_q_{j} {joint_pos[j]}")
                    if self.zmq_enabled:
                        self.send_zmq_string(f"actual_q_{j} {joint_pos[j]}")
        else:
            joint_pos = q
            if use_real_robot:
                #ur5e_robot.movej(q=np.array(q)) #TO BE IMPLEMENTED
                pass
            for j in range(len(joint_pos)):
                if self.mqtt_enabled:
                    self.send_mqtt_string(f"actual_q_{j} {joint_pos[j]}")
                if self.zmq_enabled:
                    self.send_zmq_string(f"actual_q_{j} {joint_pos[j]}")

    def send_mqtt_string(self,msg):
        msg_split = msg.split(" ")
        topic = msg_split[0]
        payload = msg_split[1]
        self.mqtt_client.publish("kuka/" + topic,payload)

    def send_zmq_string(self,msg):
        self.socket_zmq.send_string(msg)

    def get_actual_position(self):
        return np.array([self.actual_q0,self.actual_q1,self.actual_q2,
                         self.actual_q3,self.actual_q4,self.actual_q5,self.actual_q6])

    def get_previous_position(self):
        return np.array([self.prev_q0,self.prev_q1,self.prev_q2,
                         self.prev_q3,self.prev_q4,self.prev_q5,self.prev_q6])

    def get_target_position(self):
        return np.array([self.target_q0,self.target_q1,self.target_q2,
                         self.target_q3,self.target_q4,self.target_q5,self.target_q6])

    def set_actual_position(self,array):
        self.actual_q0 = array[0]
        self.actual_q1 = array[1]
        self.actual_q2 = array[2]
        self.actual_q3 = array[3]
        self.actual_q4 = array[4]
        self.actual_q5 = array[5]
        self.actual_q6 = array[6]

    def set_previous_position(self,array):
        self.prev_q0 = array[0]
        self.prev_q1 = array[1]
        self.prev_q2 = array[2]
        self.prev_q3 = array[3]
        self.prev_q4 = array[4]
        self.prev_q5 = array[5]
        self.prev_q6 = array[6]

    def set_target_position(self,array):
        self.target_q0 = array[0]
        self.target_q1 = array[1]
        self.target_q2 = array[2]
        self.target_q3 = array[3]
        self.target_q4 = array[4]
        self.target_q5 = array[5]
        self.target_q6 = array[6]

    def set_motion_time(self,motion_time):
        self.motion_time = motion_time
        self.n_steps_motion = int(self.motion_time/0.05)

class UR5e_RL(UR5e):

    def __init__(self,motion_time=2.0,mqtt_enabled=False,mqtt_address="127.0.0.1",mqtt_port=1883,zmq_enabled=False,zmq_port=5558):
        self.prev_q0 = 0
        self.prev_q1 = 0
        self.prev_q2 = 0
        self.prev_q3 = 0
        self.prev_q4 = 0
        self.prev_q5 = 0
        self.actual_q0 = 0
        self.actual_q1 = 0
        self.actual_q2 = 0
        self.actual_q3 = 0
        self.actual_q4 = 0
        self.actual_q5 = 0
        self.target_q0 = 0
        self.target_q1 = 0
        self.target_q2 = 0
        self.target_q3 = 0
        self.target_q4 = 0
        self.target_q5 = 0
        self.is_busy = False
        self.mqtt_enabled = mqtt_enabled
        self.mqtt_enabled = mqtt_enabled
        self.motion_time = motion_time
        self.n_steps_motion = int(self.motion_time/0.05)
        if self.mqtt_enabled:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.connect(mqtt_address, mqtt_port, 60)
            self.mqtt_client.loop_start()
        self.zmq_enabled = zmq_enabled
        if self.zmq_enabled:
            self.zmq_context = zmq.Context()
            self.socket_zmq = self.zmq_context.socket(zmq.PUB)
            try:
                self.socket_zmq.bind("tcp://*:" + str(zmq_port))
            except zmq.error.ZMQError as exc:
                print ("socket zmq UR5e already in use, try restarting it")
                print(exc)
        super().__init__()

    def compute_fk(self,j1, j2, j3, j4 , j5, j6):
        a2 = 0.425
        a3 = 0.3922
        d1 = 0.1625
        d4 = 0.1333
        d5 = 0.0997
        d6 = 0.0996
        T_0_1 = np.array([[np.cos(j1), -np.sin(j1), 0, 0],[np.sin(j1), np.cos(j1), 0, 0],[0, 0, 1, d1],[0,0,0,1]])
        T_1_2 = np.array([[np.cos(j2), -np.sin(j2), 0, 0],[0, 0, -1, 0],[np.sin(j2), np.cos(j2), 0, 0],[0,0,0,1]])
        T_2_3 = np.array([[np.cos(j3), -np.sin(j3), 0, a2],[np.sin(j3), np.cos(j3), 0, 0],[0,0,1,0],[0,0,0,1]])
        T_3_4 = np.array([[np.cos(j4), -np.sin(j4), 0, a3],[np.sin(j4), np.cos(j4), 0, 0],[0, 0, 1, d4],[0,0,0,1]])
        T_4_5 = np.array([[np.cos(j5), -np.sin(j5), 0, 0],[0,0,-1,-d5],[np.sin(j5), np.cos(j5), 0, 0],[0,0,0,1]])
        T_5_6 = np.array([[np.cos(j6), -np.sin(j6), 0, 0],[0,0,1,d6],[-np.sin(j6),-np.cos(j6), 0,0],[0,0,0,1]])
        T_0_6 = T_0_1 @ T_1_2 @ T_2_3 @ T_3_4 @ T_4_5 @ T_5_6
        return T_0_6

    def compute_ik_num(self,x,y,z,rounded=False):
        #T = SE3(trnorm(np.array([[-1,0,0,x],[0,1,0,y],[0,0,-1,z],[0,0,0,1]])))
        T = SE3(trnorm(np.array([[1,0,0,x],[0,np.cos(5*np.pi/4),-np.sin(5*np.pi/4),y],[0,np.sin(5*np.pi/4),np.cos(5*np.pi/4),z],[0,0,0,1]]))) # Rotation of 5*pi/4 on the x-axis

        #sol = self.ikine_LM(T,q0=[0,0,0,np.pi,0,0])
        sol = self.ikine_LM(T,q0=[-np.pi/2,np.pi/4,0,np.pi/2,0,0])
        #sol = self.ikine_LM(T,q0=[0,-np.pi/2,0,-np.pi/2,0,0])
        if (sol.success):
            solution = sol.q
            if (rounded):
                solution = np.round(solution,2)
            return solution
        return np.nan

    def compute_ik_validity(self,x,y,z,rounded=False):
        T = SE3(trnorm(np.array([[1,0,0,x],[0,np.cos(5*np.pi/4),-np.sin(5*np.pi/4),y],[0,np.sin(5*np.pi/4),np.cos(5*np.pi/4),z],[0,0,0,1]]))) # Rotation of 5*pi/4 on the x-axis

        sol = self.ikine_LM(T,q0=[-np.pi/2,np.pi/4,0,np.pi/2,0,0])
        #sol = self.ikine_LM(T,q0=[0,-np.pi/2,0,-np.pi/2,0,0])
        return sol.success

    def compute_ik_analytic(self,x,y,z):
        a2 = 0.425
        a3 = 0.3922
        d1 = 0.1625
        d4 = 0.1333
        d5 = 0.0997
        d6 = 0.0996
        # desired position and orientation [m]
        T = np.array([[0,0,1,x],[0.5,-0.866,0,y],[0.866,0.5,0,z],[0,0,0,1]])
        #T = SE3(trnorm(T))
        x = T[0][3]
        y = T[1][3]
        z = T[2][3]

        # Joint angles
        P_0_5 = T @ np.array([0,0,-d6,1]).T

        # j1
        r1 = np.sqrt(P_0_5[0]**2 + P_0_5[1]**2)
        phi1 = np.arctan2(P_0_5[1], P_0_5[0])
        phi2 = np.arccos(d4/r1)
        j1 = phi1 - phi2 + pi/2


        # j5
        j5 = np.arccos((x*np.sin(j1)-y*np.cos(j1)-d4)/d6)
        if np.isnan(j5):
            j5 = 0.0

        # j6
        R_0_6 = T[0:3,0:3]
        X_0_6_rot = R_0_6[:,0]
        Y_0_6_rot = R_0_6[:,1]
        X_6_0_rot = -X_0_6_rot
        Y_6_0_rot = -Y_0_6_rot
        num1 = (-Y_6_0_rot[0]*np.sin(j1) + Y_6_0_rot[1]*np.cos(j1))
        num2 = (X_6_0_rot[0]*np.sin(j1)-X_6_0_rot[1]*np.cos(j1))

        if np.round(j5,5) == 0:
            j6 = 0.0
        else:
            j6 = np.arctan2((num1/np.sin(j5)),(num2/np.sin(j5))) + pi
        if np.isnan(j6):
            j6 = 0.0

        # j3
        T_0_1 = np.array([[np.cos(j1), -np.sin(j1), 0, 0],[np.sin(j1), np.cos(j1), 0, 0],[0,0,1,d1],[0,0,0,1]])
        T_1_6 = np.linalg.inv(T_0_1) @ T
        T_4_5 = np.array([[np.cos(j5), -np.sin(j5), 0, 0],[0,0,-1,-d5],[np.sin(j5), np.cos(j5),0,0],[0,0,0,1]])
        T_5_6 = np.array([[np.cos(j6), -np.sin(j6),0,0],[0,0,1,d6],[-np.sin(j6), -np.cos(j6), 0, 0],[0,0,0,1]])
        T_1_4 = T_1_6 @ np.linalg.inv(T_4_5 @ T_5_6)
        P_1_3 = T_1_4 @ np.array([0,-d4,0,1]).T - np.array([0,0,0,1]).T
        P_1_4 = T_1_4[0:3,3]
        P_1_4_a = -P_1_4[0]
        P_1_4_b = -P_1_4[2]
        P_1_4_c = np.sqrt(P_1_4_a**2 + P_1_4_b**2)
        phi3 = np.arccos((P_1_4_c**2 - a2**2 - a3**2)/(-2*a2*a3))
        j3 = np.pi - phi3
        if np.isnan(j3):
            j3 = 0.0
        # check that (P_1_4_c == c) in non-right triangle
        if np.sqrt(a2**2+a3**2-2*a2*a3*np.cos(phi3)) != P_1_4_c:
            #print("Woops")
            pass

        # j2
        phi4 = np.arctan2(-P_1_4_b,-P_1_4_a)
        phi5 = np.arcsin((-a3 * np.sin(-j3))/P_1_4_c)
        j2 = phi4 - phi5

        # j4
        T_1_2 = np.array([[np.cos(j2), -np.sin(j2), 0, 0],[0, 0, -1, 0],[np.sin(j2), np.cos(j2), 0, 0],[0,0,0,1]])
        T_2_3 = np.array([[np.cos(j3), -np.sin(j3), 0, a2],[np.sin(j3), np.cos(j3), 0, 0],[0,0,1,0],[0,0,0,1]])
        T_3_4 = np.linalg.inv(T_1_2 @ T_2_3) @ T_1_4
        X_3_4_rot = T_3_4[0:3,0]
        j4 = np.arctan2(X_3_4_rot[1],X_3_4_rot[0])

        return j1, j2, j3, j4, j5 ,j6

    def compute_xyz_flexcell(self,X,Y,Z=0,rx=0,ry=0,rz=0):
        ## Inversed axis, (x->y,y->x)
        #Z_table_level = -0.080
        #Z_table_level = -0.035
        Z_table_level = 0.020 # Real measured from the table
        YMIN = 0
        YMAX = 23
        XMIN = 0
        XMAX = 15
        HOLE_DIST = 0.05
        x_min = -0.072
        x_max = 1.128
        #y_max = 0.831#0.431
        y_max = 0.731 - 0.020 # compensation
        y_min = -0.369 - 0.020 # compensation

        #comp_x = x_max - ((Y+1)*HOLE_DIST) #(Y+1)
        #comp_y = (y_max - ((X)*HOLE_DIST)) # (X+1)
        comp_x = x_max - ((Y+1)*HOLE_DIST) #(Y+1)
        comp_y = (y_max - ((X)*HOLE_DIST)) # (X+1)
        comp_z = Z_table_level + Z * HOLE_DIST
        rx = rx
        ry = ry
        rz = rz

        return comp_x,comp_y,comp_z

    def compute_inverse_xyz_flexcell(self,x,y,z,rx=0,ry=0,rz=0):
        ## Inversed axis, (x->y,y->x)
        #Z_table_level = -0.080
        #Z_table_level = -0.035
        Z_table_level = 0.020 # Real measured from the table
        YMIN = 0
        YMAX = 23
        XMIN = 0
        XMAX = 15
        HOLE_DIST = 0.05
        x_min = -0.072
        x_max = 1.128
        #y_max = 0.831#0.431
        y_max = 0.731 - 0.020 # compensation
        y_min = -0.369 - 0.020 # compensation

        Y = (x_max - x)/HOLE_DIST - 1
        X = (y_max - y)/HOLE_DIST
        Z = (z - Z_table_level)/HOLE_DIST
        return round(X),round(Y),round(Z)

    def compute_yz_joint(self,yc,zc):
        theta = np.arctan(zc/yc)
        alpha = np.pi/4 + theta
        zj = np.sqrt(zc**2 + yc**2) * np.cos(np.pi/2 - alpha)
        yj = np.sqrt(zc**2 + yc**2) * np.sin(np.pi/2 - alpha)
        return yj,zj

    def compute_inverse_yz_joint(self,yj,zj):
        if ((yj == 0.0) or (zj == 0.0)):
            return yj,zj
        theta = np.arctan(yj/zj)
        alpha = np.pi/4 + theta
        zc = np.sqrt(zj**2 + yj**2) * np.sin(np.pi/2 - alpha)
        yc = np.sqrt(zj**2 + yj**2) * np.cos(np.pi/2 - alpha)
        return yc,zc

    def compute_q(self,x,y,z):
        solution1 = self.compute_ik_num(x,y,z,rounded=False)
        j1,j2,j3,j4,j5,j6 = self.compute_ik_analytic(x,y,z)
        solution_analytic = np.array([j1,j2,j3,j4,j5,j6])
        if (solution1 is not np.nan):
            return np.array([solution1,solution_analytic])
        else:
            return np.array([solution_analytic])

    def compute_trajectory(self,q_actual,q_target,n_steps=None,plot=False):
        if n_steps == None:
            n_steps = self.n_steps_motion
        q_traj = rtb.jtraj(q_actual, q_target, n_steps)
        if plot:
            self.plot(q_traj.q, backend='pyplot', movie='ur5e.gif')
        return q_traj.q

    def transmit_robot_motion(self,q,use_real_robot=False):
        if len(q.shape) == 2:
            for i in range(len(q)):
                joint_pos = q[i]
                if use_real_robot:
                    #ur5e_robot.movej(q=np.array(q)) #TO BE IMPLEMENTED
                    pass
                for j in range(len(joint_pos)):
                    if self.mqtt_enabled:
                        self.send_mqtt_string(f"actual_q_{j} {joint_pos[j]}")
                    if self.zmq_enabled:
                        self.send_zmq_string(f"actual_q_{j} {joint_pos[j]}")
        else:
            joint_pos = q
            if use_real_robot:
                #ur5e_robot.movej(q=np.array(q)) #TO BE IMPLEMENTED
                pass
            for j in range(len(joint_pos)):
                if self.mqtt_enabled:
                    self.send_mqtt_string(f"actual_q_{j} {joint_pos[j]}")
                if self.zmq_enabled:
                    self.send_zmq_string(f"actual_q_{j} {joint_pos[j]}")

    def send_mqtt_string(self,msg):
        msg_split = msg.split(" ")
        topic = msg_split[0]
        payload = msg_split[1]
        self.mqtt_client.publish("ur5e/" + topic,payload)

    def send_zmq_string(self,msg):
        self.socket_zmq.send_string(msg)

    def get_actual_position(self):
        return np.array([self.actual_q0,self.actual_q1,self.actual_q2,
                         self.actual_q3,self.actual_q4,self.actual_q5])

    def get_target_position(self):
        return np.array([self.target_q0,self.target_q1,self.target_q2,
                         self.target_q3,self.target_q4,self.target_q5])

    def get_previous_position(self):
        return np.array([self.prev_q0,self.prev_q1,self.prev_q2,
                         self.prev_q3,self.prev_q4,self.prev_q5])

    def set_actual_position(self,array):
        self.actual_q0 = array[0]
        self.actual_q1 = array[1]
        self.actual_q2 = array[2]
        self.actual_q3 = array[3]
        self.actual_q4 = array[4]
        self.actual_q5 = array[5]


    def set_target_position(self,array):
        self.target_q0 = array[0]
        self.target_q1 = array[1]
        self.target_q2 = array[2]
        self.target_q3 = array[3]
        self.target_q4 = array[4]
        self.target_q5 = array[5]

    def set_previous_position(self,array):
        self.prev_q0 = array[0]
        self.prev_q1 = array[1]
        self.prev_q2 = array[2]
        self.prev_q3 = array[3]
        self.prev_q4 = array[4]
        self.prev_q5 = array[5]

    def set_motion_time(self,motion_time):
        self.motion_time = motion_time
        self.n_steps_motion = int(self.motion_time/0.05)


class UR5e_RoboSim(rtb.DHRobot):
    def __init__(self):
        #L1 = rtb.RevoluteMDH(d=0.1625, a=0, alpha=0)
        #L2 = rtb.RevoluteMDH(d=0, a=0, alpha=pi/2)
        #L3 = rtb.RevoluteMDH(d=0, a=0.425, alpha=0) # changed a to negative
        #L4 = rtb.RevoluteMDH(d=0.1333, a=0.3922, alpha=0) # changed a to negative
        #L5 = rtb.RevoluteMDH(d=0.0997, a=0, alpha=pi/2)
        #L6 = rtb.RevoluteMDH(d=0.0996, a=0, alpha=-pi/2)
        L1 = rtb.RevoluteDH(d=0.089159, a=0, alpha=pi/2)
        L2 = rtb.RevoluteDH(d=0, a=-0.425, alpha=0)
        L3 = rtb.RevoluteDH(d=0, a=-0.39225, alpha=0)
        L4 = rtb.RevoluteDH(d=0.10915, a=0, alpha=pi/2)
        L5 = rtb.RevoluteDH(d=0.09465, a=0, alpha=-pi/2)
        L6 = rtb.RevoluteDH(d=0.0823, a=0, alpha=0)
        super().__init__([L1, L2, L3, L4, L5, L6],name="UR5e")

class UR5e_RoboSim_Simulation(UR5e_RoboSim):

    def __init__(self,motion_time=2.0,mqtt_enabled=False,mqtt_address="127.0.0.1",mqtt_port=1883,zmq_enabled=False,zmq_port=5558):
        self.prev_q0 = 0
        self.prev_q1 = 0
        self.prev_q2 = 0
        self.prev_q3 = 0
        self.prev_q4 = 0
        self.prev_q5 = 0
        self.actual_q0 = 0
        self.actual_q1 = 0
        self.actual_q2 = 0
        self.actual_q3 = 0
        self.actual_q4 = 0
        self.actual_q5 = 0
        self.target_q0 = 0
        self.target_q1 = 0
        self.target_q2 = 0
        self.target_q3 = 0
        self.target_q4 = 0
        self.target_q5 = 0
        self.is_busy = False
        self.mqtt_enabled = mqtt_enabled
        self.mqtt_enabled = mqtt_enabled
        self.motion_time = motion_time
        self.n_steps_motion = int(self.motion_time/0.05)
        if self.mqtt_enabled:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.connect(mqtt_address, mqtt_port, 60)
            self.mqtt_client.loop_start()
        self.zmq_enabled = zmq_enabled
        if self.zmq_enabled:
            self.zmq_context = zmq.Context()
            self.socket_zmq = self.zmq_context.socket(zmq.PUB)
            try:
                self.socket_zmq.bind("tcp://*:" + str(zmq_port))
            except zmq.error.ZMQError as exc:
                print ("socket zmq UR5e already in use, try restarting it")
                print(exc)
        super().__init__()

    def compute_fk(self,j1, j2, j3, j4 , j5, j6):
        a2 = 0.425
        a3 = 0.3922
        d1 = 0.1625
        d4 = 0.1333
        d5 = 0.0997
        d6 = 0.0996
        T_0_1 = np.array([[np.cos(j1), -np.sin(j1), 0, 0],[np.sin(j1), np.cos(j1), 0, 0],[0, 0, 1, d1],[0,0,0,1]])
        T_1_2 = np.array([[np.cos(j2), -np.sin(j2), 0, 0],[0, 0, -1, 0],[np.sin(j2), np.cos(j2), 0, 0],[0,0,0,1]])
        T_2_3 = np.array([[np.cos(j3), -np.sin(j3), 0, a2],[np.sin(j3), np.cos(j3), 0, 0],[0,0,1,0],[0,0,0,1]])
        T_3_4 = np.array([[np.cos(j4), -np.sin(j4), 0, a3],[np.sin(j4), np.cos(j4), 0, 0],[0, 0, 1, d4],[0,0,0,1]])
        T_4_5 = np.array([[np.cos(j5), -np.sin(j5), 0, 0],[0,0,-1,-d5],[np.sin(j5), np.cos(j5), 0, 0],[0,0,0,1]])
        T_5_6 = np.array([[np.cos(j6), -np.sin(j6), 0, 0],[0,0,1,d6],[-np.sin(j6),-np.cos(j6), 0,0],[0,0,0,1]])
        T_0_6 = T_0_1 @ T_1_2 @ T_2_3 @ T_3_4 @ T_4_5 @ T_5_6
        return T_0_6

    def compute_ik_num(self,x,y,z,rounded=False):
        T = SE3(trnorm(np.array([[1,0,0,x],[0,np.cos(5*np.pi/4),-np.sin(5*np.pi/4),y],[0,np.sin(5*np.pi/4),np.cos(5*np.pi/4),z],[0,0,0,1]])))
        #T = SE3(trnorm(np.array([[np.cos(5*np.pi/4),-np.sin(5*np.pi/4),0,x],[np.sin(5*np.pi/4),np.cos(5*np.pi/4),0,y],[0,0,1,z],[0,0,0,1]])))
        #T = SE3(trnorm(np.array([[1,0,0,x],[0,1,0,y],[0,0,1,z],[0,0,0,1]])))


        #sol = self.ikine_LM(T,q0=[0,0,0,np.pi,0,0])
        sol = self.ikine_LM(T,q0=[-np.pi/2,-np.pi/2,np.pi/4,0,-np.pi/2,0])
        #sol = self.ikine_LM(T,q0=[0,-np.pi/2,0,-np.pi/2,0,0])
        if (sol.success):
            solution = sol.q
            if (rounded):
                solution = np.round(solution,2)
            return solution
        return np.nan

    def compute_ik_validity(self,x,y,z,rounded=False):
        T = SE3(trnorm(np.array([[1,0,0,x],[0,np.cos(5*np.pi/4),-np.sin(5*np.pi/4),y],[0,np.sin(5*np.pi/4),np.cos(5*np.pi/4),z],[0,0,0,1]]))) # Rotation of 5*pi/4 on the x-axis

        sol = self.ikine_LM(T,q0=[-np.pi/2,-np.pi/4,0,np.pi/2,0,0])
        #sol = self.ikine_LM(T,q0=[0,-np.pi/2,0,-np.pi/2,0,0])
        return sol.success

    def compute_ik_analytic(self,x,y,z):
        a2 = 0.425
        a3 = 0.3922
        d1 = 0.1625
        d4 = 0.1333
        d5 = 0.0997
        d6 = 0.0996
        # desired position and orientation [m]
        T = np.array([[0,0,1,x],[0.5,-0.866,0,y],[0.866,0.5,0,z],[0,0,0,1]])
        #T = SE3(trnorm(T))
        x = T[0][3]
        y = T[1][3]
        z = T[2][3]

        # Joint angles
        P_0_5 = T @ np.array([0,0,-d6,1]).T

        # j1
        r1 = np.sqrt(P_0_5[0]**2 + P_0_5[1]**2)
        phi1 = np.arctan2(P_0_5[1], P_0_5[0])
        phi2 = np.arccos(d4/r1)
        j1 = phi1 - phi2 + pi/2


        # j5
        j5 = np.arccos((x*np.sin(j1)-y*np.cos(j1)-d4)/d6)
        if np.isnan(j5):
            j5 = 0.0

        # j6
        R_0_6 = T[0:3,0:3]
        X_0_6_rot = R_0_6[:,0]
        Y_0_6_rot = R_0_6[:,1]
        X_6_0_rot = -X_0_6_rot
        Y_6_0_rot = -Y_0_6_rot
        num1 = (-Y_6_0_rot[0]*np.sin(j1) + Y_6_0_rot[1]*np.cos(j1))
        num2 = (X_6_0_rot[0]*np.sin(j1)-X_6_0_rot[1]*np.cos(j1))

        if np.round(j5,5) == 0:
            j6 = 0.0
        else:
            j6 = np.arctan2((num1/np.sin(j5)),(num2/np.sin(j5))) + pi
        if np.isnan(j6):
            j6 = 0.0

        # j3
        T_0_1 = np.array([[np.cos(j1), -np.sin(j1), 0, 0],[np.sin(j1), np.cos(j1), 0, 0],[0,0,1,d1],[0,0,0,1]])
        T_1_6 = np.linalg.inv(T_0_1) @ T
        T_4_5 = np.array([[np.cos(j5), -np.sin(j5), 0, 0],[0,0,-1,-d5],[np.sin(j5), np.cos(j5),0,0],[0,0,0,1]])
        T_5_6 = np.array([[np.cos(j6), -np.sin(j6),0,0],[0,0,1,d6],[-np.sin(j6), -np.cos(j6), 0, 0],[0,0,0,1]])
        T_1_4 = T_1_6 @ np.linalg.inv(T_4_5 @ T_5_6)
        P_1_3 = T_1_4 @ np.array([0,-d4,0,1]).T - np.array([0,0,0,1]).T
        P_1_4 = T_1_4[0:3,3]
        P_1_4_a = -P_1_4[0]
        P_1_4_b = -P_1_4[2]
        P_1_4_c = np.sqrt(P_1_4_a**2 + P_1_4_b**2)
        phi3 = np.arccos((P_1_4_c**2 - a2**2 - a3**2)/(-2*a2*a3))
        j3 = np.pi - phi3
        if np.isnan(j3):
            j3 = 0.0
        # check that (P_1_4_c == c) in non-right triangle
        if np.sqrt(a2**2+a3**2-2*a2*a3*np.cos(phi3)) != P_1_4_c:
            #print("Woops")
            pass

        # j2
        phi4 = np.arctan2(-P_1_4_b,-P_1_4_a)
        phi5 = np.arcsin((-a3 * np.sin(-j3))/P_1_4_c)
        j2 = phi4 - phi5

        # j4
        T_1_2 = np.array([[np.cos(j2), -np.sin(j2), 0, 0],[0, 0, -1, 0],[np.sin(j2), np.cos(j2), 0, 0],[0,0,0,1]])
        T_2_3 = np.array([[np.cos(j3), -np.sin(j3), 0, a2],[np.sin(j3), np.cos(j3), 0, 0],[0,0,1,0],[0,0,0,1]])
        T_3_4 = np.linalg.inv(T_1_2 @ T_2_3) @ T_1_4
        X_3_4_rot = T_3_4[0:3,0]
        j4 = np.arctan2(X_3_4_rot[1],X_3_4_rot[0])

        return j1, j2, j3, j4, j5 ,j6

    def compute_xyz_flexcell(self,X,Y,Z=0,rx=0,ry=0,rz=0):
        ## Inversed axis, (x->y,y->x)
        #Z_table_level = -0.080
        #Z_table_level = -0.035
        Z_table_level = 0.020 # Real measured from the table
        YMIN = 0
        YMAX = 23
        XMIN = 0
        XMAX = 15
        HOLE_DIST = 0.05
        x_min = -0.072
        x_max = 1.128
        #y_max = 0.831#0.431
        y_max = 0.731 - 0.020 # compensation
        y_min = -0.369 - 0.020 # compensation

        #comp_x = x_max - ((Y+1)*HOLE_DIST) #(Y+1)
        #comp_y = (y_max - ((X)*HOLE_DIST)) # (X+1)
        comp_x = x_max - ((Y+1)*HOLE_DIST) #(Y+1)
        comp_y = (y_max - ((X)*HOLE_DIST)) # (X+1)
        comp_z = Z_table_level + Z * HOLE_DIST
        rx = rx
        ry = ry
        rz = rz

        return comp_x,comp_y,comp_z

    def compute_inverse_xyz_flexcell(self,x,y,z,rx=0,ry=0,rz=0):
        ## Inversed axis, (x->y,y->x)
        #Z_table_level = -0.080
        #Z_table_level = -0.035
        Z_table_level = 0.020 # Real measured from the table
        YMIN = 0
        YMAX = 23
        XMIN = 0
        XMAX = 15
        HOLE_DIST = 0.05
        x_min = -0.072
        x_max = 1.128
        #y_max = 0.831#0.431
        y_max = 0.731 - 0.020 # compensation
        y_min = -0.369 - 0.020 # compensation

        Y = (x_max - x)/HOLE_DIST - 1
        X = (y_max - y)/HOLE_DIST
        Z = (z - Z_table_level)/HOLE_DIST
        return round(X),round(Y),round(Z)

    def compute_yz_joint(self,yc,zc):
        theta = np.arctan(zc/yc)
        alpha = np.pi/4 + theta
        zj = np.sqrt(zc**2 + yc**2) * np.cos(np.pi/2 - alpha)
        yj = np.sqrt(zc**2 + yc**2) * np.sin(np.pi/2 - alpha)
        return yj,zj

    def compute_inverse_yz_joint(self,yj,zj):
        if ((yj == 0.0) or (zj == 0.0)):
            return yj,zj
        theta = np.arctan(yj/zj)
        alpha = np.pi/4 + theta
        zc = np.sqrt(zj**2 + yj**2) * np.sin(np.pi/2 - alpha)
        yc = np.sqrt(zj**2 + yj**2) * np.cos(np.pi/2 - alpha)
        return yc,zc

    def compute_q(self,x,y,z):
        solution1 = self.compute_ik_num(x,y,z,rounded=False)
        j1,j2,j3,j4,j5,j6 = self.compute_ik_analytic(x,y,z)
        solution_analytic = np.array([j1,j2,j3,j4,j5,j6])
        if (solution1 is not np.nan):
            return np.array([solution1,solution_analytic])
        else:
            return np.array([solution_analytic])

    def compute_trajectory(self,q_actual,q_target,n_steps=None,plot=False):
        if n_steps == None:
            n_steps = self.n_steps_motion
        q_traj = rtb.jtraj(q_actual, q_target, n_steps)
        if plot:
            self.plot(q_traj.q, backend='pyplot', movie='ur5e.gif')
        return q_traj.q

    def transmit_robot_motion(self,q,use_real_robot=False):
        if len(q.shape) == 2:
            for i in range(len(q)):
                joint_pos = q[i]
                if use_real_robot:
                    #ur5e_robot.movej(q=np.array(q)) #TO BE IMPLEMENTED
                    pass
                for j in range(len(joint_pos)):
                    if self.mqtt_enabled:
                        self.send_mqtt_string(f"actual_q_{j} {joint_pos[j]}")
                    if self.zmq_enabled:
                        self.send_zmq_string(f"actual_q_{j} {joint_pos[j]}")
        else:
            joint_pos = q
            if use_real_robot:
                #ur5e_robot.movej(q=np.array(q)) #TO BE IMPLEMENTED
                pass
            for j in range(len(joint_pos)):
                if self.mqtt_enabled:
                    self.send_mqtt_string(f"actual_q_{j} {joint_pos[j]}")
                if self.zmq_enabled:
                    self.send_zmq_string(f"actual_q_{j} {joint_pos[j]}")

    def send_mqtt_string(self,msg):
        msg_split = msg.split(" ")
        topic = msg_split[0]
        payload = msg_split[1]
        self.mqtt_client.publish("ur5e/" + topic,payload)

    def send_zmq_string(self,msg):
        self.socket_zmq.send_string(msg)

    def get_actual_position(self):
        return np.array([self.actual_q0,self.actual_q1,self.actual_q2,
                         self.actual_q3,self.actual_q4,self.actual_q5])

    def get_target_position(self):
        return np.array([self.target_q0,self.target_q1,self.target_q2,
                         self.target_q3,self.target_q4,self.target_q5])

    def get_previous_position(self):
        return np.array([self.prev_q0,self.prev_q1,self.prev_q2,
                         self.prev_q3,self.prev_q4,self.prev_q5])

    def set_actual_position(self,array):
        self.actual_q0 = array[0]
        self.actual_q1 = array[1]
        self.actual_q2 = array[2]
        self.actual_q3 = array[3]
        self.actual_q4 = array[4]
        self.actual_q5 = array[5]


    def set_target_position(self,array):
        self.target_q0 = array[0]
        self.target_q1 = array[1]
        self.target_q2 = array[2]
        self.target_q3 = array[3]
        self.target_q4 = array[4]
        self.target_q5 = array[5]

    def set_previous_position(self,array):
        self.prev_q0 = array[0]
        self.prev_q1 = array[1]
        self.prev_q2 = array[2]
        self.prev_q3 = array[3]
        self.prev_q4 = array[4]
        self.prev_q5 = array[5]

    def set_motion_time(self,motion_time):
        self.motion_time = motion_time
        self.n_steps_motion = int(self.motion_time/0.05)
