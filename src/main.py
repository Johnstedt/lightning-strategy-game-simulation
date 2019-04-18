import plot
import simulation
import json


def simulations():

	histories = []
	graphs = []

	env = json.loads(open("presets/allocation.json", "r").read())

	for i in range(3):
		h, g = simulation.simulate(env)
		histories.append(h)
		graphs.append(g)

	plot.plot_multiple_histories(histories)
	plot.plot_wealth_distribution(graphs)


if __name__ == "__main__":
	simulations()
