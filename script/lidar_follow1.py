#!/usr/bin/python3
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np

class LidarTracker:
    
    def __init__(self):
        
        rospy.init_node('lidar_follow1', anonymous=False)
        self.scanSubscriber = rospy.Subscriber('/robot1/scan', LaserScan, self.scancallback)
        self.cmd_pub = rospy.Publisher('/robot1/cmd_vel', Twist, queue_size=10)

        self.followDistance = rospy.get_param('~followDistance',0.5)
        self.minAngle = rospy.get_param('~minAngle',-1.570796)
        self.maxAngle = rospy.get_param('~maxAngle',1.570796)
        self.deltaDist = rospy.get_param('~deltaDist',0.2)
        self.winSize = rospy.get_param('~winSize',2)
        self.lidarInstallAngle = rospy.get_param('~lidarInstallAngle',0)
        self.max_velocity = 0.3
        self.min_velocity = 0.05
        rospy.loginfo('Start Follow Latest Object')
        rospy.spin()


    def scancallback(self,scan_data):
        # make scan data as a array
        ranges = np.array(scan_data.ranges)
        # arrange data index ascending order
        rangesIndex = np.argsort(ranges)
        control_name = rospy.get_param("robot_name", "/robot0")
        tempMinDistance = float("inf")
        # print(control_name)
        if control_name != "/robot1":
           
            for i in rangesIndex:
                tempMinDistance = ranges[i]
                tempMinDistanceAngle = scan_data.angle_min + i*scan_data.angle_increment
                tempMinDistanceAngle += self.lidarInstallAngle
                if tempMinDistanceAngle > 3.14159:
                    tempMinDistanceAngle -= 3.14159*2
                elif tempMinDistanceAngle < -3.14159:
                    tempMinDistanceAngle += 3.14159*2
                else:
                    pass

                windowIndex = np.clip([i-self.winSize, i+self.winSize+1],0,len(ranges))
                window = ranges[windowIndex[0]:windowIndex[1]]
                # filt senser noise point
                with np.errstate(invalid='ignore'):
                    if(np.any(abs(window - tempMinDistance) < self.deltaDist)):
                        if tempMinDistanceAngle > self.minAngle and tempMinDistanceAngle < self.maxAngle:
                            # print (tempMinDistance,tempMinDistanceAngle)
                            break
                        else:
                            pass
                    else:
                        pass
            #catches no scan, no minimum found, minimum is actually inf
            
            twist = Twist()
            if tempMinDistance > scan_data.range_max:
                twist.linear.x = 0
                twist.angular.z = 0
            else:
                
                if tempMinDistance > self.followDistance:
                    twist.linear.x = tempMinDistance - self.followDistance
                    #set a velocity threshold control
                    if twist.linear.x < self.min_velocity:
                        twist.linear.x = self.min_velocity
                    elif twist.linear.x > self.max_velocity:
                        twist.linear.x = self.max_velocity
                    else:
                        pass
                else:
                    twist.linear.x = 0.0
                if abs(tempMinDistanceAngle) > 0.05:
                    twist.angular.z = tempMinDistanceAngle*1.0
            self.cmd_pub.publish(twist)


if __name__ == '__main__':
    
    try:  
        LidarTracker()
    except rospy.ROSInterruptException:
        pass
