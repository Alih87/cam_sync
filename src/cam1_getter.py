#!/usr/bin/env python3
import roslib; roslib.load_manifest('cam_sync')
import rospy
from cam_sync.realsense import camera
from cv_bridge import CvBridge
import cv2
from sensor_msgs.msg import Image, PointCloud2
from std_msgs.msg import Header, Time
import numpy as np

class cam1(object):
    def __init__(self, camera_obj):
        rospy.init_node('cam1_getter', anonymous=False)
        self.cam_obj = camera_obj
        self.cam_obj.initialize_camera()
        self.frame, self.pc = None, None
        self.time = Time()
        self.frame_id = 0
        self.bridge = CvBridge()

        self.I_msg, self.pc_msg, self.head_msg = Image(), PointCloud2(), Header()
        rospy.sleep(0.5)

    def update_header(self, head_msg):
        #t = rospy.Time.now()
        # self.time.secs = t.secs
        # self.time.nsecs = t.nsecs
        self.head_msg.stamp = rospy.Time.now()
        self.head_msg.frame_id = str(self.frame_id)

        return head_msg

    def make_frames(self):
        self.frame = self.cam_obj.get_frames()
        self.pc = self.cam_obj.get_pc()
        
        # self.I_msg.data = self.frame[0].flatten().tolist()
        self.I_msg = self.bridge.cv2_to_imgmsg(self.frame[0], encoding='bgr8')
        self.pc_msg.data = np.asarray(self.frame[1], np.float32).tostring()
        self.I_msg.header, self.pc_msg.header = self.update_header(self.head_msg), self.update_header(self.head_msg)
        self.I_msg.height, self.I_msg.width = self.frame[0].shape[0], self.frame[0].shape[1]
        self.pc_msg.height, self.pc_msg.width = self.frame[1].shape[0], self.frame[1].shape[1]
        self.frame_id += 1

    def rgb_publisher(self):
        #rospy.init_node('cam1_getter', anonymous=False)
        pub = rospy.Publisher('cam1_frames', Image, queue_size=1)
        pub.publish(self.I_msg)

    def cloud_publisher(self):
        #rospy.init_node('cam1_getter', anonymous=False)
        pub = rospy.Publisher('cam1_points', PointCloud2, queue_size=1)
        pub.publish(self.pc_msg)

if __name__ == '__main__':
    CAMERA1_ID = 919122072922
    camObj = camera(CAMERA1_ID)
    camObj.Reset()
    cam_src1 = cam1(camObj)
    rate = rospy.Rate(5)
    while not rospy.is_shutdown():
        camObj.COUNT += 1
        cam_src1.make_frames()
        cam_src1.rgb_publisher()
        cam_src1.cloud_publisher()
        rate.sleep()