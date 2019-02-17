import numpy as np
# This is where you can build a decision tree for determining throttle, brake and steer
# commands based on the output of the perception_step() function
def decision_step(Rover):
    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward':
            # Check the extent of navigable terrain

            #check if a rock identified
            if Rover.rover_to_rock_angle != 0:
                Rover.steer = Rover.rover_to_rock_angle

                Rover.throttle = Rover.throttle_set
                if Rover.near_sample == 1:
                    Rover.steer = 0
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                    if Rover.send_pickup == False and Rover.picking_up == 0: #pick up command has not been sent
                        Rover.mode = 'stop'
                        Rover.steer = 0
                        Rover.throttle = 0
                        Rover.brake = Rover.brake_set
                        Rover.picking_up = 1  # Will be set to telemetry value data["picking_up"]
                        Rover.send_pickup = True  # Set to True to trigger rock pickup
                        print("send_pickup: ", Rover.send_pickup, "picking_up: ", Rover.picking_up)

                    elif Rover.send_pickup == False and Rover.picking_up == 1: # pickup command already sent
                        print("send_pickup: ", Rover.send_pickup, "picking_up: ", Rover.picking_up )

                else: #no rock nearby or rock has been picked up
                    Rover.picking_up = 0
                    Rover.send_pickup = False

            elif len(Rover.nav_angles) >= Rover.stop_forward:
                # If mode is forward, navigable terrain looks good
                # and velocity is below max, then throttle
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else:  # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180 / np.pi), -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                # Set mode to "stop" and hit the brakes!
                Rover.throttle = 0
                # Set brake to stored brake value
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'

        elif Rover.mode == 'forward' and Rover.throttle <= Rover.throttle_set and Rover.vel <= 0.1: #stuck at somewhere

            Rover.mode = 'stop'
            Rover.throttle = 0
            Rover.brake = 0


        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop' and Rover.picking_up == 1: # is picking_up the rock,do nothing
            Rover.throttle = 0
            Rover.brake = Rover.brake_set
            Rover.steer = 0

        elif Rover.mode == 'stop' and Rover.picking_up == 0: #finished the picking up
            times1 = 0 # check if the rover is stuck in a corner
            times2 = 0
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0

            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0

                    if len(Rover.nav_angles) > 0 and times1 < 3 and times2 < 3:


                        if np.mean(Rover.nav_angles) >= 0:
                        # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                            Rover.steer = 15  # Could be more clever here about which way to turn
                            times1 += 1
                            print("stuck 1")
                        else:
                            Rover.steer = -5
                            times2 += 1
                            print("stuck 2")

                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180 / np.pi), -15, 15)
                    Rover.mode = 'forward'
    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.throttle = 0
        Rover.steer = 0
        Rover.brake = 0

    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True

    return Rover

