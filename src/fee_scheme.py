import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import scipy

from matplotlib.patches import Polygon

def plot_fee_scheme():

	k = np.arange(1, 10000000, 1)

	colors = ['r--', 'b--', 'y--']
	colors_b = ['ro', 'bo', 'yo']

	plt.plot(k, k**2, "r-")
	plt.plot(k, k**2, "b-")

	a, b = 2, 9  # integral limits
	x = np.linspace(0, 10)
	y = func(x)

	fig, ax = plt.subplots()
	plt.plot(x, y, 'r', linewidth=2)
	plt.ylim(ymin=0)

	# Make the shaded region
	ix = np.linspace(a, b)
	iy = func(ix)
	verts = [(a, 0)] + list(zip(ix, iy)) + [(b, 0)]
	poly = Polygon(verts, facecolor='0.9', edgecolor='0.5')
	ax.add_patch(poly)

	plt.text(0.5 * (a + b), 30, r"$\int_a^b f(x)\mathrm{d}x$",
			 horizontalalignment='center', fontsize=20)

	plt.figtext(0.9, 0.05, '$x$')
	plt.figtext(0.1, 0.9, '$y$')

	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.xaxis.set_ticks_position('bottom')

	ax.set_xticks((a, b))
	ax.set_xticklabels(('$a$', '$b$'))
	ax.set_yticks([])

	plt.savefig("plots/fee_scheme.png")

def func(x):
	return (x - 3) * (x - 5) * (x - 7) + 85


if __name__ == "__main__":
	plot_fee_scheme()
