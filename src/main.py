import plot
import simulation
import json


def simulations():

	test = []

	env = json.loads(open("presets/validate_price_model.json", "r").read())

	for i in range(5):
		h, _ = simulation.simulate(env)
		test.append(h)

	plot.plot_multiple_histories(test)


if __name__ == "__main__":
	simulations()
