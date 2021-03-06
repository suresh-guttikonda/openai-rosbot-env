#!/usr/bin/env python3

import rospy
from openai_ros import utils, rosbot_gazebo_env
from sensor_msgs.msg import LaserScan, Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from gazebo_msgs.msg import ModelState
import time

class TurtleBot3Env(rosbot_gazebo_env.RosbotGazeboEnv):
    """
        TurtleBot3Env class acts as abstract turtlebot environment template
    """

    def __init__(self, reset_type = 'SIMULATION'):
        """
        Initialize TurtleBot3Env class

        Sensor Topic List:
        * /odom : Odometry readings of the base of the robot
        * /imu  : IMU readings to get relative accelerations and orientations
        * /scan : Laser readings

        Actuator Topic List:
        * /cmd_vel : Move the robot through Twist commands

        """

        super(TurtleBot3Env, self).__init__(reset_type = reset_type)

        self._laser_scan = None
        self._imu_data = None
        self._odom_data = None
        self._particle_cloud = None
        self._amcl_pose = None
        self._gazebo_pose = None
        self._map_data = None

        self._global_frame_id = None
        self._scan_frame_id = None

        # env variables
        self._request_map = False
        self._request_laser = False
        self._request_odom = False
        self._request_imu = False
        self._request_amcl = False
        self._request_gazebo_data = False

        # setup subscribers and publishers
        self.gazebo.unpause_sim()
        self._check_all_systems_are_ready()

        rospy.Subscriber('/scan', LaserScan, self._laser_scan_callback)
        rospy.Subscriber('/imu', Imu, self._imu_data_callback)
        rospy.Subscriber('/odom', Odometry, self._odom_data_callback)

        self._cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size = 5)
        self._init_pose_pub = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size = 5)
        self._gazebo_pose_pub = rospy.Publisher('/gazebo/set_model_state', ModelState, queue_size = 5)

        self._check_publishers_connection()
        self.gazebo.pause_sim()
        rospy.loginfo('status: system check passed')

    #### public methods ####

    def get_laser_scan(self):
        """
        Laser Scan Getter
        """
        return self._laser_scan

    def get_imu_data(self):
        """
        Imu data Getter
        """
        return self._imu_data

    def get_odom_data(self):
        """
        Odometry data Getter
        """
        return self._odom_data

    def get_amcl_pose(self):
    	"""
    	AMCL pose Getter
    	"""
    	return self._amcl_pose

    def get_particle_cloud(self):
    	"""
    	AMCL particle cloud Getter
    	"""
    	return self._particle_cloud

    def get_gazebo_pose(self):
    	"""
    	Gazebo(ground truth) pose Getter
    	"""
    	return self._gazebo_pose

    #### private methods ####

    def _check_all_systems_are_ready(self):
        """
        Checks all sensors and other simulation systems are operational
        """

        rospy.logdebug('TurtleBot3Env._check_all_systems_are_ready() start')
        if self._request_map:
            self._check_map_data_is_ready()
        if self._request_amcl:
            self._check_amcl_data_is_ready()
        if self._request_gazebo_data:
            self._check_gazebo_data_is_ready()

        self._check_all_sensors_are_ready()

    def _check_publishers_connection(self):
        """
        Checks all publishers are operational
        """

        rospy.logdebug('TurtleBot3Env._check_publishers_connection() start')
        self._check_cmd_vel_pub_ready()
        self._check_init_pose_pub_ready()
        self._check_gazebo_pose_pub_ready()

    def _check_cmd_vel_pub_ready(self):
        """
        Checks command velocity publisher is operational
        """
        rospy.logdebug('TurtleBot3Env._check_cmd_vel_pub_ready() start')
        utils.check_publisher_connections(self._cmd_vel_pub)

    def _check_map_data_is_ready(self):
        """
        Checks map service is operational
        """
        rospy.logdebug('TurtleBot3Env._check_map_data_is_ready() start')
        pass

    def _check_init_pose_pub_ready(self):
        """
        Checks initial pose publisher is operational
        """
        rospy.logdebug('TurtleBot3Env._check_init_pose_pub_ready() start')
        pass

    def _check_gazebo_pose_pub_ready(self):
        """
        Check gazebo pose publisher is operational
        """
        rospy.logdebug('TurtleBot3Env._check_gazebo_pose_pub_ready() start')
        pass

    def _check_all_sensors_are_ready(self):
        """
        Checks all sensors are operational
        """

        rospy.logdebug('TurtleBot3Env._check_all_sensors_are_ready() start')
        if self._request_laser:
            self._check_laser_scan_is_ready()
        if self._request_imu:
            self._check_imu_data_is_ready()
        if self._request_odom:
            self._check_odom_data_is_ready()

    def _check_amcl_data_is_ready(self):
        """
        Checks amcl topic is operational
        """
        rospy.logdebug('TurtleBot3Env._check_amcl_data_is_ready() start')
        pass

    def _check_gazebo_data_is_ready(self):
        """
        Checks gazebo topic is operational
        """
        rospy.logdebug('TurtleBot3Env._check_gazebo_data_is_ready() start')
        pass

    def _check_laser_scan_is_ready(self):
        """
        Checks laser scan topic is operational

        Returns
        -------
        laser_scan: rospy.Message
            Message
        """

        rospy.logdebug('TurtleBot3Env._check_laser_scan_is_ready() start')
        topic_name = '/scan'
        topic_class = LaserScan
        time_out = 5.0
        self._laser_scan  = utils.receive_topic_msg(topic_name, topic_class, time_out)
        return self._laser_scan

    def _check_imu_data_is_ready(self):
        """
        Checks imu topic is operational

        Returns
        -------
        imu_data: rospy.Message
            Message
        """

        rospy.logdebug('TurtleBot3Env._check_imu_data_is_ready() start')
        topic_name = '/imu'
        topic_class = Imu
        time_out = 5.0
        self._imu_data = utils.receive_topic_msg(topic_name, topic_class, time_out)
        return self._imu_data

    def _check_odom_data_is_ready(self):
        """
        Checks odom topic is operational

        Returns
        -------
        odom_data: rospy.Message
            Message
        """

        rospy.logdebug('TurtleBot3Env._check_odom_data_is_ready() start')
        topic_name = '/odom'
        topic_class = Odometry
        time_out = 5.0
        self._odom_data = utils.receive_topic_msg(topic_name, topic_class, time_out)
        return self._odom_data

    def _laser_scan_callback(self, data):
        """
        This function is called when laser scan is received

        Parameters
        ----------
        data: rospy.Message
            data received from laser scan topic
        """

        rospy.logdebug('TurtleBot3Env._laser_scan_callback() start')
        self._laser_scan = data

    def _imu_data_callback(self, data):
        """
        This function is called when imu data is received

        Parameters
        ----------
        data: rospy.Message
            data received from imu topic
        """

        rospy.logdebug('TurtleBot3Env._imu_data_callback() start')
        self._imu_data = data

    def _odom_data_callback(self, data):
        """
        This function is called when odom data is received

        Parameters
        ----------
        data: rospy.Message
            data received from odom topic
        """

        rospy.logdebug('TurtleBot3Env._odom_data_callback() start')
        self._odom_data = data

    def _move_base(self, linear_speed: float, angular_speed: float,
                    motion_error: float = 0.05, update_rate: float = 10):
        """
        Move the rosbot base, based on the linear and angular speeds.

        Parameters
        ----------
        linear_speed: float
            speed in the linear motion of the robot base frame (x-axis direction)
        angular_speed: float
            speed of the angular turning of the robot base frame
        motion_error: float
            acceptable deviation from the given speed and odometry readings
        update_rate: float
            rate at which we check the odometry

        """

        rospy.logdebug('TurtleBot3Env._move_base() start')
        # publish twist message
        cmd_vel_msg = Twist()
        cmd_vel_msg.linear.x = linear_speed
        cmd_vel_msg.angular.z = angular_speed
        self._check_cmd_vel_pub_ready()
        self._cmd_vel_pub.publish(cmd_vel_msg)
        time.sleep(0.2)
        # wait for the given twist message to be executed correctly
        delta = self._wait_until_twist_achieved(cmd_vel_msg, motion_error, update_rate)

        # unpublish twist message
        cmd_vel_msg.linear.x = 0.0
        cmd_vel_msg.angular.z = 0.0
        self._check_cmd_vel_pub_ready()
        self._cmd_vel_pub.publish(cmd_vel_msg)

    def _wait_until_twist_achieved(self, cmd_vel_msg: Twist, motion_error: float, update_rate: float, time_out: float = 3.0):
        """
        Wait for the robot to achieve given cmd_vel, by referencing the odometry velocity readings

        Parameters
        ----------
        cmd_vel_msg: Twist
            velocity in terms of linear and angular parts
        motion_error: float
            acceptable deviation from the given speed and odometry readings
        update_rate: float
            rate at which we check the odometry
        time_out: float
            timeout in seconds

        Returns
        -------
        duration: float
            time taken to achieve required twist (in seconds)
        """

        rospy.logdebug('TurtleBot3Env._wait_until_twist_achieved() start')
        # compute the acceptable ranges for linear and angular velocity
        min_linear_speed = cmd_vel_msg.linear.x - motion_error
        max_linear_speed = cmd_vel_msg.linear.x + motion_error
        min_angular_speed = cmd_vel_msg.angular.z - motion_error
        max_angular_speed = cmd_vel_msg.angular.z + motion_error

        rate = rospy.Rate(update_rate)
        start_time = rospy.get_rostime().to_sec()
        duration = 0.0

        # loop until the twist is achieved
        while not rospy.is_shutdown():

            # TODO: check if robot has crashed

            current_odom = self._check_odom_data_is_ready()
            duration = rospy.get_rostime().to_sec() - start_time
            if current_odom is None:
                # odom data not available
                rospy.logwarn('odom is not available')
                break

            odom_linear_vel = current_odom.twist.twist.linear.x
            odom_angular_vel = current_odom.twist.twist.angular.z

            # check whether linear and angular veloctiy are valid
            is_linear_vel_valid = (
                                    (odom_linear_vel <= max_linear_speed) and
                                    (odom_linear_vel > min_linear_speed)
                                  )
            is_angular_vel_valid = (
                                    (odom_angular_vel <= max_angular_speed) and
                                    (odom_angular_vel > min_angular_speed)
                                   )

            if is_linear_vel_valid and is_angular_vel_valid:
                # required twist achieved
                break
            elif duration < time_out:
                # otherwise
                rate.sleep()
            else:
                rospy.logwarn('motion cannot be achieved')
                break
        return duration
