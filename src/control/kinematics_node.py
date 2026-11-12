#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, Float32MultiArray


class DiffDriveController(Node):
    def __init__(self):
        super().__init__('diff_drive_controller')

        # Snowbot physical parameters (override via YAML)
        self.declare_parameter('wheel_separation', 0.65)  # meters
        self.declare_parameter('wheel_radius', 0.15)      # meters
        self.declare_parameter('cmd_timeout', 0.5)        # seconds (watchdog)

        self.L = self.get_parameter('wheel_separation').value
        self.R = self.get_parameter('wheel_radius').value
        self.timeout = self.get_parameter('cmd_timeout').value

        self.estop_active = False
        self.last_cmd_time = self.get_clock().now()
        self.target_v = 0.0
        self.target_w = 0.0

        self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_cb, 10)
        self.create_subscription(Bool, '/safety/estop', self.estop_cb, 10)
        self.wheel_pub = self.create_publisher(Float32MultiArray, '/hardware/wheel_setpoints_rad_s', 10)

        # 20 Hz control loop with watchdog
        self.create_timer(0.05, self.control_loop)

    def estop_cb(self, msg: Bool):
        self.estop_active = msg.data
        if self.estop_active:
            self.get_logger().warn("SOFTWARE E-STOP TRIGGERED! Zeroing wheel velocities.")

    def cmd_vel_cb(self, msg: Twist):
        self.target_v = msg.linear.x
        self.target_w = msg.angular.z
        self.last_cmd_time = self.get_clock().now()

    def control_loop(self):
        elapsed = (self.get_clock().now() - self.last_cmd_time).nanoseconds / 1e9
        if self.estop_active or elapsed > self.timeout:
            v, w = 0.0, 0.0
        else:
            v, w = self.target_v, self.target_w

        # Differential drive inverse kinematics (rad/s)
        w_left = (v - (w * self.L / 2.0)) / self.R
        w_right = (v + (w * self.L / 2.0)) / self.R

        out = Float32MultiArray()
        out.data = [float(w_left), float(w_right)]
        self.wheel_pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = DiffDriveController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
