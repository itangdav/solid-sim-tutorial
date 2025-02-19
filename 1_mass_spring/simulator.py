# Mass-Spring Solids Simulation

import numpy as np  # numpy for linear algebra
import pygame  # pygame for visualization
import pickle

pygame.init()

import square_mesh  # square mesh
import time_integrator

# simulation setup
side_len = 1
rho = 1000  # density of square
k = 1e5  # spring stiffness
initial_stretch = 1.4
n_seg = 4  # num of segments per side of the square
h = 0.004  # time step size in s

# initialize simulation
[x, e] = square_mesh.generate(side_len, n_seg)  # node positions and edge node indices
v = np.array([[0.0, 0.0]] * len(x))  # velocity
m = [rho * side_len * side_len / ((n_seg + 1) * (n_seg + 1))] * len(
    x
)  # calculate node mass evenly
# rest length squared
l2 = []
for i in range(0, len(e)):
    diff = x[e[i][0]] - x[e[i][1]]
    l2.append(diff.dot(diff))
k = [k] * len(e)  # spring stiffness
# apply initial stretch horizontally
for i in range(0, len(x)):
    x[i][0] *= initial_stretch

# simulation with visualization
resolution = np.array([900, 900])
offset = resolution / 2
scale = 200


def screen_projection(x):
    return [offset[0] + scale * x[0], resolution[1] - (offset[1] + scale * x[1])]


dataset = {
    "arrays": [],
    "bs": [],
    "xs": [],
}

time_step = 0
square_mesh.write_to_file(time_step, x, n_seg)
screen = pygame.display.set_mode(resolution)
running = True
while running:
    # run until the user asks to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    print("### Time step", time_step, "###")

    # fill the background and draw the square
    screen.fill((255, 255, 255))
    for eI in e:
        pygame.draw.aaline(
            screen,
            (0, 0, 255),
            screen_projection(x[eI[0]]),
            screen_projection(x[eI[1]]),
        )
    for xI in x:
        pygame.draw.circle(
            screen, (0, 0, 255), screen_projection(xI), 0.1 * side_len / n_seg * scale
        )

    pygame.display.flip()  # flip the display

    # step forward simulation and wait for screen refresh
    x, v, arrays, inputs, outputs = time_integrator.step_forward(
        x, e, v, m, l2, k, h, 1e-2
    )

    dataset["arrays"] += arrays
    dataset["bs"] += inputs
    dataset["xs"] += outputs

    time_step += 1
    pygame.time.wait(int(h * 1000))
    square_mesh.write_to_file(time_step, x, n_seg)

    if time_step > 100:
        running = False
        file = open("dataset.pkl", "wb")
        pickle.dump(dataset, file)
        file.close()

pygame.quit()
