#!/usr/bin/python

import roslib; roslib.load_manifest('kingfisher_node')
import rospy

from sensor_msgs.msg import Range
import serial

ser = None

def _shutdown():
    global ser
    rospy.loginfo("Sonar shutting down.")
    rospy.loginfo("Closing Sonar serial port.")
    ser.close()

def serial_lines(ser, brk="\n"):
    buf = ""
    while True:
        rlist, _, _ = select.select([ ser ], [], [], 1.0)
        if not rlist:
            continue
        new = ser.read(ser.inWaiting())
        buf += new
        if brk in new:
            msg, buf = buf.split(brk)[-2:]
            yield msg

if __name__ == '__main__':
    global ser
    rospy.init_node('sonarmite')
    range_pub = rospy.Publisher('depth', Range)
    range_msg = Range(radiation_type=Range.ULTRASOUND, 
                      field_of_view=0.26,
                      min_range=0.1, 
                      max_range=100.0)
    range_msg.header.frame_id = "sonar"

    port = rospy.get_param('~port', '/dev/ttyUSB0')
    baud = rospy.get_param('~baud', 9600)
    
    rospy.on_shutdown(_shutdown)

    try:
        ser = serial.Serial(port=port, baudrate=baud, timeout=.5)
        lines = serial_lines(ser)

        while not rospy.is_shutdown(): 
            data = lines.next()
            try:
                fields = re.split(" ", data)
                range_msg.range = float(fields[1])
                range_msg.header.timestamp = rospy.Time.now()
                imu_pub.publish(imu_data)
            except ValueError as e:
                rospy.logerr(str(e))
                continue

        rospy.loginfo('Closing Digital Compass Serial port')
        ser.close()

    except rospy.ROSInterruptException:
        pass
