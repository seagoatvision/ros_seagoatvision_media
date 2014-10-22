#! /usr/bin/env python

# Copyright (C) 2012-2014  Octets - octets.etsmtl.ca
#
#    This file is part of SeaGoatVision.
#
#    SeaGoatVision is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from SeaGoatVision.server.media.media_streaming import MediaStreaming
from SeaGoatVision.commons.param import Param
from SeaGoatVision.server.core.configuration import Configuration
from SeaGoatVision.commons import log

import roslib

roslib.load_manifest('rospy')
roslib.load_manifest('sensor_msgs')
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

logger = log.get_logger(__name__)


class ROS(MediaStreaming):
    """
    Return image from ROS
    """

    def __init__(self, config):
        # Go into configuration/template_media for more information
        super(ROS, self).__init__()
        self.config = Configuration()
        self.own_config = config
        self.media_name = config.name
        if config.device:
            self.device_name = config.device
            self.default_ros_name = config.device
        else:
            self.default_ros_name = "/usb_cam/image_raw"
        self._is_opened = True
        self.run = True
        self.video = None
        self.image = None
        self.bridge = CvBridge()
        self.image_sub = None

        self._create_params()
        self.deserialize(self.config.read_media(self.get_name()))

    def _create_params(self):
        self.param_ipc_name = Param("ros_name", self.default_ros_name)
        self.param_ipc_name.add_notify(self.reload)

    def open(self):
        rospy.init_node('ImageView')
        self.image_sub = rospy.Subscriber(self.param_ipc_name.get(), Image,
                                          self.handle_image)

        logger.info("Open media device ros %s" % self.default_ros_name)
        return MediaStreaming.open(self)

    def handle_image(self, image):
        try:
            self.image = self.bridge.imgmsg_to_cv2(image, "bgr8")
        except CvBridgeError, e:
            print(e)
            self.image = None

    def next(self):
        return self.image

    def close(self):
        MediaStreaming.close(self)
        if self.image_sub:
            self.image_sub.unregister()
            self.image_sub = None
        self.image = None
        return True
