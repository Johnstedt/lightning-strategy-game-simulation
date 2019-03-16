import plot
import simulation


def simulations():

	test = []

	for i in range(10):
		test.append(simulation.simulate("presets/test.json"))


	# do random curve

	# loop
		# Pick profitable curve
		# Simulate




	plot.plot_multiple_histories(test)


if __name__ == "__main__":
	simulations()
