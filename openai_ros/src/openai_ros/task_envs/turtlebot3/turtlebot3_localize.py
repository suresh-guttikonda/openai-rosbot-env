#!/usr/bin/env python3

import rospy
from openai_ros.robot_envs import turtlebot3_env
from gym import spaces
from geometry_msgs.msg import PoseArray, PoseWithCovarianceStamped
from std_srvs.srv import Empty
from tf.transformations import quaternion_from_euler
import dynamic_reconfigure.client as dynamic_reconfig

import numpy as np

class TurtleBot3LocalizeEnv(turtlebot3_env.TurtleBot3Env):
    """
        TurtleBot3LocalizeEnv class is an implementation for localization of turtlebot3 task
    """

    def __init__(self):
        """
        Initialize TurtleBot3LocalizeEnv class

        Parameters
        ----------

        """
        super(TurtleBot3LocalizeEnv, self).__init__()

        self._motion_error = 0.05
        self._update_rate = 30
        self._init_linear_speed = 0.0
        self._init_angular_speed = 0.0
        self._linear_forward_speed = 0.5
        self._linear_turn_speed = 0.05
        self._angular_speed = 0.3

        rospy.loginfo('status: TurtleBot3LocalizeEnv is ready')

    def _check_amcl_data_is_ready(self):
        """
        Checks amcl is operational

        Returns
        -------

        """
        topic_name = '/particlecloud'
        topic_class = PoseArray
        time_out = 5.0
        self._particle_cloud = self._check_topic_data_is_ready(topic_name, topic_class, time_out)

        topic_name = '/amcl_pose'
        topic_class = PoseWithCovarianceStamped
        time_out = 1.0
        self._amcl_pose = self._check_topic_data_is_ready(topic_name, topic_class, time_out)

    def _check_init_pose_pub_ready(self):
        """
        Checks initial pose is operational
        """
        self._check_publisher_is_ready(self._init_pose_pub)

    def _init_amcl(self, is_global=True):
        """
        Initialize amcl

        Parameters
        ----------

        """

        # publish initialpose for amcl
        init_pose_msg = PoseWithCovarianceStamped()
        init_pose_msg.header.stamp = rospy.get_rostime()
        init_pose_msg.header.frame_id = 'map'

        # position
        init_pose_msg.pose.pose.position.x = 0.0    # pose_x
        init_pose_msg.pose.pose.position.y = 0.0    # pose_y
        init_pose_msg.pose.pose.position.z = 0.0
        # orientation
        quaternion = quaternion_from_euler(0.0, 0.0, 0.0)   # pose_a
        init_pose_msg.pose.pose.orientation.x = quaternion[0]
        init_pose_msg.pose.pose.orientation.y = quaternion[1]
        init_pose_msg.pose.pose.orientation.z = quaternion[2]
        init_pose_msg.pose.pose.orientation.w = quaternion[3]
        # covariance
        covariance = [0.0]*36 # 6x6 covariance
        covariance[6*0 + 0] = 0.5 * 0.5 # cov_xx
        covariance[6*1 + 1] = 0.5 * 0.5 # cov_yy
        covariance[6*5 + 5] = (np.pi/12.0) *(np.pi/12.0)    # cov_aa
        init_pose_msg.pose.covariance = covariance

        self._init_pose_pub.publish(init_pose_msg)

        if is_global:
            # TODO: do we need selective resampling ??

            # dynamic reconfigure
            particles = 20000
            client = dynamic_reconfig.Client('/amcl')
            params = {
                        'max_particles' : particles,
                     }
            config = client.update_configuration(params)

            self._init_global_localization()

        rospy.loginfo('status: amcl initialized')

    def _init_global_localization(self):
        """
        Initialize global localization for amcl
        """

        service_name = '/global_localization'
        service_class = Empty
        self._call_service(service_name, service_class)

    def _set_init_pose(self):
        """
        Set the initial pose of the turtlebot3
        """

        self._move_base( self._init_linear_speed, self._init_angular_speed,
                         self._motion_error, self._update_rate )

        self._init_amcl(is_global=True)

    def _init_env_variables(self):
        """
        Initialize environment variables
        """
        pass

    def _get_obs(self):
        """
        Return the observation from the environment
        """
        pass

    def _is_done(self):
        """
        Indicates whether or not the episode is done

        """

        # TODO
        pass

    def _compute_reward(self, observation, done):
        """
        Calculate the reward based on the observation

        """

        # TODO
        return 0

    def _set_action(self, action: int):
        """
        Apply the give action to the environment

        Parameters
        ----------
        action: int
            based on the action id number corresponding linear and angular speed for the rosbot is set

        Action List:
        * 0 = MoveFoward
        * 1 = TurnLeft
        * 2 = TurnRight

        """

        if action == 0:     # move forward
            linear_speed = self._linear_forward_speed
            angular_speed = 0.0
        elif action == 1:   # turn left
            linear_speed = self._linear_turn_speed
            angular_speed = self._angular_speed
        elif action == 2:   # turn right
            linear_speed = self._linear_turn_speed
            angular_speed = -1 * self._angular_speed
        else:               # do nothing / stop
            linear_speed = 0.0
            angular_speed = 0.0

        self._move_base( linear_speed, angular_speed,
                         self._motion_error, self._update_rate )
