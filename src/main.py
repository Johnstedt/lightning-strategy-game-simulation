import plot
import simulation


def simulations():

	test = []

	for i in range(10):
		test.append(simulation.simulate("presets/test.json"))

	plot.plot_multiple_histories(test)


if __name__ == "__main__":
	simulations()
