#!/usr/bin/env python3
import pyrealsense2 as rs
import numpy as np
import sys, time

class camera(object):
    def __init__(self, SERIAL_NUM, align_frames=False):
        self.serial_num = SERIAL_NUM
        self.depth_frame, self.color_frame = None, None
        self.do_align = align_frames
        self.MAX_DISTANCE = 3.5
        self.COUNT = 0
        self.FRAME = 0

    def initialize_camera(self):
        ctx = rs.context()
        devices = ctx.query_devices()
        for dev in devices:
            dev.hardware_reset()
        print("[INFO] Reset Done!\n")

        self.pipeline = rs.pipeline()
        self.config = rs.config()

        self.config.enable_device(str(self.serial_num))
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        # For extracting depth parameters exclusive to the current device
        self.pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        self.pipeline_profile = self.config.resolve(self.pipeline_wrapper)
        self.device = self.pipeline_profile.get_device()
        self.depth_scale = self.device.first_depth_sensor().get_depth_scale()

        cfg = self.pipeline.start(self.config)
        if self.do_align:
            self.align = rs.align(rs.stream.color)

        # Get intrinsic parameters of camera from depth stream
        prof = cfg.get_stream(rs.stream.depth)
        self.intrinsics = prof.as_video_stream_profile().get_intrinsics()

        time.sleep(1)

    def get_frames(self):
        try:
            comp_frames = self.pipeline.wait_for_frames()
            self.FRAME += 1
            if self.do_align:
                comp_frames = self.align.process(comp_frames)

            color_raw, depth_raw = comp_frames.get_color_frame(), comp_frames.get_depth_frame()
            self.color_frame, self.depth_frame = np.asanyarray(color_raw.get_data()),\
                                    np.asanyarray(depth_raw.get_data()) * self.depth_scale

        except AttributeError:
            print("[INFO] No frame received...")

        except KeyboardInterrupt:
            print("\n[INFO] Stopping Pipeline.\n")
            self.pipeline.stop()

        else:
            pass

        return np.uint32(self.color_frame/255.), self.depth_frame

    def get_pc(self):
        rows, cols = self.depth_frame.shape
        c, r = np.meshgrid(np.arange(cols), np.arange(rows), sparse=True)
        r, c = r.astype(float), c.astype(float)

        valid = (self.depth_frame > 0) & (self.depth_frame < self.MAX_DISTANCE)
        valid = np.ravel(valid)
        z = self.depth_frame
        x = z * (c - self.intrinsics.ppx) / self.intrinsics.fx
        y = z * (r - self.intrinsics.ppy) / self.intrinsics.fy
        
        z = np.ravel(z)[valid]
        y = np.ravel(y)[valid]
        x = np.ravel(x)[valid]

        r = np.ravel(self.color_frame[:,:,0])[valid]
        g = np.ravel(self.color_frame[:,:,1])[valid]
        b = np.ravel(self.color_frame[:,:,2])[valid]

        xyzrgb = np.dstack((x,y,z,r,g,b)).reshape(-1,6)
        #sys.stdout.write(str(xyzrgb.shape))

        return xyzrgb
