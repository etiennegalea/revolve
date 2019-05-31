import numpy as np
import os
from glob import glob
import matplotlib.pyplot as plt


path = "/home/maarten/Desktop/spider9/"
dirs = glob(path + "*/")

# Base settings for alph, sigma_sq, l
base_names = ["sampling", "alpha", "sigma_sq", "l"]
base_setting = ["LHS", "0.5", "1", "0.05"]
parameter_file = "dynamic_parameters.txt"

# Initiate groups with base
zero = ["/".join(x.split("/")[:-2]) + "/" for x in dirs][0] + "0/"
groups = []
for k in range(len(base_setting)):
    groups += [[[zero, base_setting]]]

for ix, my_dir in enumerate(dirs):
    my_sub_dirs = [float(path.split("/")[-2]) for path in glob(my_dir + "*/")]
    my_sub_dirs.sort()
    my_sub_dirs = [str(x) for x in my_sub_dirs]

    # Save all fitnesses in a list. This can help you to later construct the
    for sd in my_sub_dirs:
        if os.path.isfile(my_dir + sd + "/" + parameter_file):
            break

    # Get dynamic parameters
    params = [(line.rstrip('\n')).split(",") for line in open(my_dir + sd + "/" + parameter_file)][0]

    # Group folders together based on which param they differ in from
    equality = [0]*len(base_setting)
    c= 0
    for k in range(len(base_setting)):
        if not base_setting[k] == params[k]:
            groups[k] += [[my_dir, params]]
            print(f"Added {my_dir} to group {k} with params {params}")
            c += 1
    if c == 0:
        print(f"Didn't add {my_dir}")


for ix,group in enumerate(groups):
    print("\n\n")
    # Sort group
    group = sorted(group, key=lambda x: x[1][ix])
    labels = []
    fitnesses_list_mean = []
    fitnesses_list_error = []

    for i, e in enumerate(group):
        print(e)
        labels += [e[1][ix]]

        # Get fitnesses that are generated by gridsearchanalysis
        fitnesses = np.loadtxt(e[0] + "experiment_fitnesses.txt", delimiter =",")
        fitnesses = fitnesses[:,0]
        error = np.std(fitnesses)
        mean = np.mean(fitnesses)
        fitnesses_list_mean += [mean]
        fitnesses_list_error += [error]

    ax = plt.subplot()
    plt.title("Varying " + base_names[ix])
    plt.xlim((-0.5, len(group) -0.5))
    plt.errorbar([i for i in range(len(group))],
                 fitnesses_list_mean,
                 yerr = fitnesses_list_error,
                 linewidth =3.5,
                 capsize = 6,
                 capthick = 3.0,
                 marker="o",
                 ms = 10,
                 ls ="none")
    ax.set_xticks([i for i in range(len(group))])
    ax.set_xticklabels(labels)

    plt.savefig(path + str(ix) + ".png")
    plt.show()



