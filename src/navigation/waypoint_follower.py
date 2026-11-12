#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Bool
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import math


def create_pose(navigator: BasicNavigator, x: float, y: float, yaw_deg: float) -> PoseStamped:
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    
    yaw_rad = math.radians(yaw_deg)
    pose.pose.orientation.z = math.sin(yaw_rad / 2.0)
    pose.pose.orientation.w = math.cos(yaw_rad / 2.0)
    return pose


class SidewalkMissionNode(Node):
    def __init__(self):
        super().__init__('sidewalk_mission_node')
        self.auger_pub = self.create_publisher(Bool, '/hardware/auger_enable', 10)
        self.get_logger().info("Sidewalk Mission Node initialized.")

    def set_auger(self, state: bool):
        msg = Bool()
        msg.data = state
        self.auger_pub.publish(msg)
        self.get_logger().info(f"Auger state set to: {state}")


def main(args=None):
    rclpy.init(args=args)
    mission_node = SidewalkMissionNode()
    navigator = BasicNavigator()

    # Wait for Nav2 to become active
    navigator.waitUntilNav2Active()

    # Define sidewalk clearing pass (x, y in meters, yaw in degrees)
    waypoints = [
        create_pose(navigator, 2.0, 0.0, 0.0),
        create_pose(navigator, 10.0, 0.0, 0.0),
        create_pose(navigator, 10.0, 0.8, 180.0), # Shift over for return pass
        create_pose(navigator, 0.0, 0.8, 180.0),
    ]

    mission_node.set_auger(True)
    navigator.followWaypoints(waypoints)

    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback:
            mission_node.get_logger().info(
                f"Executing waypoint {feedback.current_waypoint + 1}/{len(waypoints)}"
            )
        rclpy.spin_once(mission_node, timeout_sec=0.5)

    # Always disable auger when mission ends or aborts
    mission_node.set_auger(False)

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        mission_node.get_logger().info("Sidewalk clearing pass completed!")
    else:
        mission_node.get_logger().error(f"Mission failed or canceled with code: {result}")

    mission_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
