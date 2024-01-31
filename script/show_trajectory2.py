#!/usr/bin/python3
# coding=gbk

import rospy
from nav_msgs.msg import Odometry

from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped

path_pub = rospy.Publisher('/robot2/robot_trajectory', Path, queue_size=10)
trajectory = Path()

def callback(data):
    global trajectory
    global path_pub

    this_pose_stamped = PoseStamped()

    this_pose_stamped.pose = data.pose.pose
    this_pose_stamped.header.frame_id = data.header.frame_id
    this_pose_stamped.header.stamp = rospy.Time.now()
    
    trajectory.header.frame_id = this_pose_stamped.header.frame_id
    trajectory.header.stamp = rospy.Time.now()
    trajectory.poses.append(this_pose_stamped)
    path_pub.publish(trajectory)

def listener():

    rospy.init_node('show_trajectory2', anonymous=False)
    rospy.Subscriber("/robot2/odom", Odometry, callback)
    # rospy.loginfo('Start Show Robot trajectory ')
    rospy.spin()

if __name__ == '__main__':
    listener()
