#!/usr/bin/env python3
import roslib; roslib.load_manifest('cam_sync')
import rospy
from cam_sync.realsense import camera
from sensor_msgs.msg import Image

class cam2(object):
    def __init__(self, camera_obj):
        self.cam_obj = camera_obj
        self.cam_obj.initialize_camera()
        rospy.sleep(0.5)

    def make_frames(self):
        frame = self.cam_obj.get_frames()
        pc = self.cam_obj.get_pc()

    def frame_publisher(self):
        rospy.init_node('cam1_getter', anonymous=False)
        pub = rospy.Publisher('cam1_frames', Image, queue_size=1)
    
if __name__ == '__main__':
    CAMERA2_ID = 117322070906
    camObj = camera(CAMERA2_ID)
    cam_src2 = cam2(camObj)
    while not rospy.is_shutdown():
        cam_src2.make_frames()
        