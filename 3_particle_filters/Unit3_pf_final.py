from robot import *
from math import *
import random
import matplotlib.pyplot as plt
import numpy as np

max_steering_angle = pi / 4.0
bearing_noise = 0.1 # Noise parameter for sense function.
steering_noise = 0.1 # Noise parameter for move function.
distance_noise = 5.0 # Noise parameter for move function.

tolerance_xy = 15.0 # Tolerance for localization in the x and y directions.
tolerance_orientation = 0.25

# NOTE: Landmark coordinates are given in (y, x) form and NOT in the
# traditional (x, y) format for some ridiculous reason.
landmarks  = [[0.0, 100.0], [0.0, 0.0], [100.0, 0.0], [100.0, 100.0]]
# world is NOT cyclic. Robot is allowed to travel "out of bounds"
world_size = 100.0 

# extract mean position from a particle set
def get_position(p):
    x = 0.0
    y = 0.0
    orientation = 0.0
    for i in range(len(p)):
        x += p[i].x
        y += p[i].y
        # orientation is tricky because it is cyclic. By normalizing around the
        # first particle we are somewhat more robust to the 0 = 2pi problem
        orientation += (((p[i].orientation - p[0].orientation + pi) %
                         (2.0 * pi)) +
                        p[0].orientation - pi)

    return [x / len(p), y / len(p), orientation / len(p)]


# Robot motions and measurements
def generate_ground_truth(motions):
    myrobot = robot()
    myrobot.set_noise(bearing_noise, steering_noise, distance_noise)

    Z = []
    T = len(motions)

    for t in range(T):
        myrobot = myrobot.move_circular(motions[t])
        Z.append(myrobot.sense())

    print 'Robot:    ', myrobot
    return [myrobot, Z]


# Measurements associated for  generate_ground_truth()
def print_measurements(Z):
    T = len(Z)
    print ('measurements = [[%.8s, %.8s, %.8s, %.8s],'
           %(str(Z[0][0]), str(Z[0][1]), str(Z[0][2]), str(Z[0][3])))

    for t in range(1,T-1):
        print ('                [%.8s, %.8s, %.8s, %.8s],'
               %(str(Z[t][0]), str(Z[t][1]), str(Z[t][2]), str(Z[t][3])))

    print ('                [%.8s, %.8s, %.8s, %.8s]]'
           %(str(Z[T-1][0]), str(Z[T-1][1]), str(Z[T-1][2]), str(Z[T-1][3])))


# Checks to see if particle filter localizes the robot to within the desired
# tolerances (defined at top of script) of the true position.
def check_output(final_robot, estimated_position):
    error_x = abs(final_robot.x - estimated_position[0])
    error_y = abs(final_robot.y - estimated_position[1])
    error_orientation = abs(final_robot.orientation - estimated_position[2])
    error_orientation = (error_orientation + pi) % (2.0 * pi) - pi
    correct = (error_x < tolerance_xy
               and error_y < tolerance_xy 
               and error_orientation < tolerance_orientation)
    return correct

def particle_filter(motions, measurements, N = 500, plot = False):
    # Make particles
    p = []
    for i in range(N):
        r = robot()
        r.set_noise(bearing_noise, steering_noise, distance_noise)
        p.append(r)
        
    # Update particles
    for t in range(len(motions)):
        # motion update (prediction)
        for particle in range(N):
            p[particle] = p[particle].move_circular(motions[t])
            
        # measurement update
        w = []
        for particle in range(N):
            w.append(p[particle].measurement_prob(measurements[t]))

        # resampling
        # this approach works with smallish particle sets, as N increases,
        # it suffers from underflow
        #w = np.array(w)
        #w = w / sum(w)
        #print w
        #p = np.random.choice(p, N, replace = True, p = w)
        p3 = []
        index = int(random.random() * N)
        beta = 0.0
        mw = max(w)

        for i in range(N):
            beta += random.random() * 2.0 * mw
            while beta > w[index]:
                beta -= w[index]
                index = (index + 1) % N
            p3.append(p[index])

        p = p3
        
        if plot:
            x = [a.x for a in p]
            y = [a.y for a in p]

            plt.plot(x, y, 'bo', alpha = max(0.2, 100 / N))
            plt.xlim([0, 2 * world_size])
            plt.ylim([0, 2 * world_size])
            plt.show()
        
    return get_position(p)




# TEST CASES----------------------------------------------------------
# Case 1
motions = [[2. * pi / 10, 20.] for row in range(8)]
measurements = [[4.746936, 3.859782, 3.045217, 2.045506],
                [3.510067, 2.916300, 2.146394, 1.598332],
                [2.972469, 2.407489, 1.588474, 1.611094],
                [1.906178, 1.193329, 0.619356, 0.807930],
                [1.352825, 0.662233, 0.144927, 0.799090],
                [0.856150, 0.214590, 5.651497, 1.062401],
                [0.194460, 5.660382, 4.761072, 2.471682],
                [5.717342, 4.736780, 3.909599, 2.342536]]
print particle_filter(motions, measurements, plot = True)



# Case 2
number_of_iterations = 6
motions = [[2. * pi / 20, 12.] for row in range(number_of_iterations)]
x = generate_ground_truth(motions)
final_robot = x[0]
measurements = x[1]
estimated_position = particle_filter(motions, measurements, plot = True)
print_measurements(measurements)
print 'Ground truth:    ', final_robot
print 'Particle filter: ', estimated_position
print 'Code check:      ', check_output(final_robot, estimated_position)
