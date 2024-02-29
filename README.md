# graduation_project_2023
Intelligent Robotics Laboratory Undergraduate Graduation Project 2023 DONT

## 1. launch the robot-control program

    roslaunch graduation_project project_control.launch

  ### gesture poses:

        (1) go straight: the five fingers
        (2) go left: keep "go straight" pose and tilt to the left large
        (3) go right: keep "go straight" pose and tilt to the right large
        (4) stop: zero

        (6) control robot1: "one" 
        (7) control robot2: "two" 
        (8) control robot3: "three" 


## 2. Look at the camera and control the robots with gestures

    rqt_image_view


## 3. start the robot-following program

    roslaunch graduation_project project_following.launch


## 4. Start the program that displays the robot's trajectory in rviz

    roslaunch graduation_project project_trajectory.launch



## 5.end all programs:

    killall gzserver
    killall gzclient
