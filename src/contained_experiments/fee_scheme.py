import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.integrate as integrate

from matplotlib.patches import Polygon


def plot_fee_scheme():

	a, b = 5500000, 9000000  # integral limits
	x = np.linspace(0, 10000000)
	y = func(x)
	y_a = alice(x)

	fig, ax = plt.subplots()
	fig.subplots_adjust(left=0.2)
	plt.plot(x, y, 'b', linewidth=2, label='Bob Fee Curve')
	plt.plot(x, y_a, 'r', linewidth=2, label='Alice Fee Curve')
	plt.ylim(ymin=0)

	# Make the shaded region
	ix = np.linspace(a, b)
	iy = func(ix)
	verts = [(a, 0)] + list(zip(ix, iy)) + [(b, 0)]
	poly = Polygon(verts, facecolor='0.9', edgecolor='0.5')
	ax.add_patch(poly)

	b4, b3 = 1000000, 4500000
	# Make the shaded region
	a_ix = np.linspace(b4, b3)
	a_iy = func(a_ix)
	a_verts = [(b4, 0)] + list(zip(a_ix, a_iy)) + [(b3, 0)]
	a_poly = Polygon(a_verts, facecolor='0.9', edgecolor='0.5')
	ax.add_patch(a_poly)

	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.xaxis.set_ticks_position('bottom')

	ax.set_xticks((a, b, b3, b4, 2500000, 7500000, 10000000))
	ax.set_xticklabels(('$B_2$', '$B_1$', '$B_3$', '$B_4$', "2.5M", "7.5M", "10M"))

	ax.set_xlabel("$Satoshis$")
	ax.set_ylabel("$\dfrac{F_P}{S}$ μS")
	ax.legend()

	result = integrate.quad(lambda x: func(x), a, b)
	print(result)

	result = integrate.quad(lambda x: func(x), b4, b3)
	print(result)

	plt.savefig("plots/fee_scheme.png")


def func(x):
	return (10000000 - x)**2 - ((10000000 - x)**1.99999999997) - ((10000000 - x)*0.000002)


def alice(x):
	return (x**2) - (x**1.99999999997) - (x*0.000002)


if __name__ == "__main__":
	plot_fee_scheme()
