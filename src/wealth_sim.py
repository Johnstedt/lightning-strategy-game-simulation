import plot
import simulation
import json
import os


def simulations(directory):

	histories = []
	graphs = []
	fail = []

	env = json.loads(open("presets/wealth1.json", "r").read())

	for i in range(2):
		h, g, failures = simulation.simulate(env)
		histories.append(h)
		graphs.append(g)
		fail.append(failures)

	env = json.loads(open("presets/wealth2.json", "r").read())

	for i in range(2):
		h, g, failures = simulation.simulate(env)
		histories.append(h)
		graphs.append(g)
		fail.append(failures)

	env = json.loads(open("presets/wealth3.json", "r").read())

	for i in range(2):
		h, g, failures = simulation.simulate(env)
		histories.append(h)
		graphs.append(g)
		fail.append(failures)

	env = json.loads(open("presets/wealth4.json", "r").read())

	for i in range(2):
		h, g, failures = simulation.simulate(env)
		histories.append(h)
		graphs.append(g)
		fail.append(failures)

	if not os.path.exists("plots/{}".format(directory)):
		os.mkdir("plots/{}".format(directory))
	plot.plot_multiple_histories(histories, directory)
	plot.plot_wealth_distribution(graphs, directory)
	plot.plot_wealth_distribution_in(graphs, directory)

	plot.plot_path_length(graphs[0], directory)

	undirected = []

	for gs in graphs:
		undirected.append(gs.to_undirected())

	plot.plot_robustness_random(undirected, 10, directory)
	plot.plot_robustness_coordinated(undirected, 7, directory)

	print(fail)


if __name__ == "__main__":
	simulations("wealth_sim")


