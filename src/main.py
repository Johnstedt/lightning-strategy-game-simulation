import plot
import simulation
import json
import os


def simulations(directory):

	histories = []
	graphs = []

	env = json.loads(open("presets/price_simulation.json", "r").read())

	for i in range(10):
		h, g = simulation.simulate(env)
		histories.append(h)
		graphs.append(g)

	os.mkdir("plots/{}".format(directory))
	plot.plot_multiple_histories(histories, directory)
	plot.plot_wealth_distribution(graphs, directory)


if __name__ == "__main__":
	simulations("price_simulation")
