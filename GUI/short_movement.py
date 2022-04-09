#! /usr/bin/env python3

###
# KINOVA (R) KORTEX (TM)
#
# Copyright (c) 2018 Kinova inc. All rights reserved.
#
# This software may be modified and distributed
# under the terms of the BSD 3-Clause license.
#
# Refer to the LICENSE file for details.
#
###
import csv
import time
import sys
import os
import threading
import utilities
from kortex_api.TCPTransport import TCPTransport
from kortex_api.RouterClient import RouterClient
from kortex_api.SessionManager import SessionManager

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient 

from kortex_api.autogen.messages import Session_pb2, Base_pb2, BaseCyclic_pb2

# Maximum allowed waiting time during actions (in seconds)
TIMEOUT_DURATION = 5

class kanova:
    # Parse arguments
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    
    args = utilities.parseConnectionArguments()
    def __init__ (self):

        # Create closure to set an event after an END or an ABORT
        def check_for_sequence_end_or_abort(e):
            """Return a closure checking for END or ABORT notifications on a sequence
            Arguments:
            e -- event to signal when the action is completed
                (will be set when an END or ABORT occurs)
            """

            def check(notification, e=e):
                event_id = notification.event_identifier
                task_id = notification.task_index
                if event_id == Base_pb2.SEQUENCE_TASK_COMPLETED:
                    print("Sequence task {} completed".format(task_id))
                elif event_id == Base_pb2.SEQUENCE_ABORTED:
                    print("Sequence aborted with error {}:{}" \
                        .format( \
                        notification.abort_details, \
                        Base_pb2.SubErrorCodes.Name(notification.abort_details)))
                    e.set()
                elif event_id == Base_pb2.SEQUENCE_COMPLETED:
                    print("Sequence completed.")
                    e.set()

            return check

        # Create closure to set an event after an END or an ABORT
        def check_for_end_or_abort(e):
            """Return a closure checking for END or ABORT notifications
            Arguments:
            e -- event to signal when the action is completed
                (will be set when an END or ABORT occurs)
            """

            def check(notification, e=e):
                print("EVENT : " + \
                    Base_pb2.ActionEvent.Name(notification.action_event))
                if notification.action_event == Base_pb2.ACTION_END \
                        or notification.action_event == Base_pb2.ACTION_ABORT:
                    e.set()

            return check

        def create_angular_action(actuator_count):
            print("Creating angular action")
            action = Base_pb2.Action()
            action.name = "Example angular action"
            action.application_data = ""

            for joint_id in range(actuator_count):
                joint_angle = action.reach_joint_angles.joint_angles.joint_angles.add()
                joint_angle.value = 0.0

            return action

        def move_to_home_position(base):
            # Make sure the arm is in Single Level Servoing mode
            base_servo_mode = Base_pb2.ServoingModeInformation()
            base_servo_mode.servoing_mode = Base_pb2.SINGLE_LEVEL_SERVOING
            base.SetServoingMode(base_servo_mode)

            # Move arm to ready position
            print("Moving the arm to a safe position")
            action_type = Base_pb2.RequestedActionType()
            action_type.action_type = Base_pb2.REACH_JOINT_ANGLES
            action_list = base.ReadAllActions(action_type)
            action_handle = None
            for action in action_list.action_list:
                if action.name == "Home":
                    action_handle = action.handle

            if action_handle == None:
                print("Can't reach safe position. Exiting")
                return False

            e = threading.Event()
            notification_handle = base.OnNotificationActionTopic(
                check_for_end_or_abort(e),
                Base_pb2.NotificationOptions()
            )

            base.ExecuteActionFromReference(action_handle)
            finished = e.wait(TIMEOUT_DURATION)
            base.Unsubscribe(notification_handle)

            if finished:
                print("Safe position reached")
            else:
                print("Timeout on action notification wait")
            return finished

        def hello_sequence(base, base_cyclic):
            print("Creating Action for Sequence")

            actuator_count = base.GetActuatorCount().count
            angular_action = create_angular_action(actuator_count)

            print("Creating Sequence")
            sequence = Base_pb2.Sequence()
            sequence.name = "Hello Sequence"

            print("Appending Actions to Sequence")
            task_1 = sequence.tasks.add()
            task_1.group_identifier = 0
            task_1.action.CopyFrom(angular_action)


            e = threading.Event()
            notification_handle = base.OnNotificationSequenceInfoTopic(
                check_for_sequence_end_or_abort(e),
                Base_pb2.NotificationOptions()
            )

            print("Creating sequence on device and executing it")
            handle_sequence = base.CreateSequence(sequence)
            base.PlaySequence(handle_sequence)

            print("Waiting for movement to finish ...")
            finished = e.wait(TIMEOUT_DURATION)
            base.Unsubscribe(notification_handle)

            if not finished:
                print("Timeout on action notification wait")
            return finished


        def control():
            with open(r"Live_data/classification.txt") as filename:
                print("filename :", filename)
                var = []
                file = filename.readlines()
                for col in file:
                    var.append(col[0])
            # for row in file:
            #     var.append(row[0])
                print("You have commanded the following sequences:", var)

            # # Import the utilities helper module
            # sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            # import utilities

            # # Parse arguments
            # args = utilities.parseConnectionArguments()

            # Create connection to the device and get the router
            with utilities.DeviceConnection.createTcpConnection(self.args) as router:
                # Create required services
                base = BaseClient(router)
                base_cyclic=BaseCyclicClient(router)
                
                for i in var:
                    success = True
                    # classifier_output = input("What's the classifier output:")
                    # Example core
                    if i == '0':
                        success &= move_to_home_position(base)
                    elif i == '1':
                        success &= hello_sequence(base,base_cyclic)
                        success &= move_to_home_position(base)

                    continue

            return 0 if success else 1
        
        control()
        return None
    exit

if __name__ == "__main__":
    main=kanova()
    main.show()
    exit(main())