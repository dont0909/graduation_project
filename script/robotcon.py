#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email.mime import image
import rospy
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import mediapipe as mp
import pyautogui
import autopy

from std_msgs.msg import String
#twist

Scrw,Scrh = autopy.screen.size()
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


class image_converter:
    def __init__(self):    
        self.image_pub = rospy.Publisher("hands", Image, queue_size=5)
        pub = rospy.Publisher('robot_control', String, queue_size=5)
        pub2 = rospy.Publisher('robot_name', String, queue_size=1)
        rate=rospy.Rate(10)
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/usb_cam/image_raw", Image, self.callback)
        self.cv_image = []
        self.new_image_flag = False
        while not rospy.is_shutdown():
            with mp_hands.Hands(model_complexity=0,min_detection_confidence=0.5,min_tracking_confidence=0.5) as hands:
                if not self.new_image_flag:
                    continue
                else:
                    self.new_image_flag = False
                    image = self.cv_image
                    # To improve performance, optionally mark the image as not writeable to
                    # pass by reference.
                    image.flags.writeable = False
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    #flip image
                    image = cv2.flip(image,1)
                    results = hands.process(image)
                    

                    # Draw the hand annotations on the image.
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)   
                    
                    #
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(
                                image,
                                hand_landmarks,
                                mp_hands.HAND_CONNECTIONS,
                                mp_drawing_styles.get_default_hand_landmarks_style(),
                                mp_drawing_styles.get_default_hand_connections_style())
                                
                            h,w,c = image.shape
                            #print(h,w,c)
                            
                            #handclose
                            tipIds = [8,12,16,20]

                            fingers_r =[]
                            fingers_l =[]
                            fingers = []
                            #finger big
                            if results.multi_handedness[0].classification[0].index == 0:
                               #print("l")
                               #cv2.putText(image,'left', (20,400),cv2.FONT_HERSHEY_PLAIN,10,(200,200,200))
                               if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
                                  fingers_l.append(1)
                               else:
                                  fingers_l.append(0)
                                  
                               for x in range(0,4):
                                  if hand_landmarks.landmark[tipIds[x]].y < hand_landmarks.landmark[tipIds[x]-2].y:
                                     fingers_l.append(1)
                                  else:
                                     fingers_l.append(0)
                               
                               #print(fingers_l)                            
                               
                            else:
                               #cv2.putText(image,'right',(20,400),cv2.FONT_HERSHEY_PLAIN,10,(200,200,200))
                               #print("r")
                               if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                                  fingers_r.append(1)
                               else:
                                  fingers_r.append(0)
                                  
                               for x in range(0,4):
                                  if hand_landmarks.landmark[tipIds[x]].y < hand_landmarks.landmark[tipIds[x]-2].y:
                                     fingers_r.append(1)
                                  else:
                                     fingers_r.append(0)
                               #print(fingers_r)
                             
                            #dx,dy = int(w*hand_landmarks.landmark[4].x),int(h*hand_landmarks.landmark[4].y) 
                            #cx,cy = int(w*hand_landmarks.landmark[8].x),int(h*hand_landmarks.landmark[8].y)   
                            #cv2.circle(image,(cx,cy),10,(100,100,200),cv2.FILLED)
                            #cv2.line(image,(dx,dy),(cx,cy),(200,100,200),3)   
                            

                            #print('big-mid:', big)
                            
                            #print('smal-mid:', small)
                            
                            #print(fingers_r)
                            #print(len(results.multi_hand_landmarks))
                            
                            if len(results.multi_hand_landmarks)==1:

                              #left hand or right hand
                               if fingers_l:
                                  fingers = fingers_l
                                  #determine the direction of the hand by the 3 fingers 
                                  small = h*hand_landmarks.landmark[20].y-h*hand_landmarks.landmark[12].y
                                  big = h*hand_landmarks.landmark[4].y-h*hand_landmarks.landmark[12].y
                               else:
                                  fingers = fingers_r
                                  small = -(h*hand_landmarks.landmark[20].y-h*hand_landmarks.landmark[12].y)
                                  big = -(h*hand_landmarks.landmark[4].y-h*hand_landmarks.landmark[12].y)
                               


                               if fingers.count(1)==1 and fingers[1]==1:
                                  robotname = "/robot1"
                                  pub2.publish(robotname)


                               if fingers.count(1)==2 and fingers[1]==1 and fingers[2]==1:
                                  robotname = "/robot2"
                                  pub2.publish(robotname)

                               if fingers.count(1)==3 and fingers[1]==1 and fingers[2]==1 and fingers[3]==1:
                                  robotname = "/robot3"
                                  pub2.publish(robotname)
                                  #stop  
                               if fingers.count(1)==0:
                                       str = "s"
                                       pub.publish(str)
                                    
                               if fingers.count(1)>=4:
                                    #go
                                    if small > 0 and big < 0 :
                                       str = "l"
                                    elif small < 0 and big > 0 :
                                       str = "r"
                                    else:
                                       str = "m"
                                    # print(str)
                                    pub.publish(str)

                               #Camera image lags when using sleep codes
                               rate.sleep()

                               
                                

                try:
                    img_msg = self.bridge.cv2_to_imgmsg(image, "bgr8")
                    img_msg.header.stamp = rospy.Time.now()
                    self.image_pub.publish(img_msg)
                except CvBridgeError as e:
                    print (e)


    def callback(self,data):
        # convert ROS topic to cv image
        try:
            self.cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            self.new_image_flag = True
        except CvBridgeError as e:
            print (e)


if __name__ == '__main__':
    try:
        # Initialize ros nodes
        rospy.init_node("gesture recognition")

        image_converter()
        rospy.spin()
    except KeyboardInterrupt:
        print ("Shutting down pose node.")
        cv2.destroyAllWindows()

