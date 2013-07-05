#!/usr/bin/python

import roslib; roslib.load_manifest('kingfisher_nmea')
import rospy

from nmea_helpers import TxHelper
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3Stamped
from math import degrees, pi

from tf.transformations import euler_from_quaternion


class RawIMU(TxHelper):
  SENTENCE = "IMU" 

  def __init__(self):
    rospy.Subscriber("imu/data", Imu, self._cb)

  def _cb(self, msg):
    # Must convert these values:
    #  ROS frame: X forward, Y to port, Z up
    #  Sea frame: X forward, Y to starboard, Z down
    self.tx(self.gps_time(msg.header.stamp),
        degrees(msg.angular_velocity.x),
        -degrees(msg.angular_velocity.y),
        -degrees(msg.angular_velocity.z),
        msg.linear_acceleration.x,
        -msg.linear_acceleration.y,
        -msg.linear_acceleration.z)


class RawCompass(TxHelper):
  SENTENCE = "RCM" 

  def __init__(self):
    rospy.Subscriber("imu/data", Imu, self._cb)
    self.compass_id = 0

  def _cb(self, msg):
    q = msg.orientation
    roll, pitch, yaw = euler_from_quaternion([ getattr(q, f) for f in q.__slots__ ])

    # Yaw must be transformed to clockwise from north.
    yaw_ned = (pi/2) - yaw
    if yaw_ned < 0: yaw_ned += 2*pi

    # Pitch gets reported around the 180deg point.
    if roll > 0:
        roll_upright = roll - pi
    else:
        roll_upright = roll + pi

    self.tx(self.gps_time(),
        self.compass_id,
        degrees(yaw_ned),
        degrees(pitch),
        degrees(roll_upright),
        self.gps_time(msg.header.stamp))


if __name__ == "__main__":
  rospy.init_node('nmea_imu')
  RawCompass()
  RawIMU()
  rospy.spin()
