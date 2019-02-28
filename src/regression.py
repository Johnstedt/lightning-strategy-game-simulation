"""
sudo python3 -m pip install sklearn
"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline


y_train = [[1], [2], [4], [9], [16], [25], [36], [47], [64], [73]]
x_plot = np.linspace(0, len(y_train), len(y_train))

plt.scatter(x_plot, y_train, color='navy', s=30, marker='o', label="training points")
colors = ['teal', 'yellowgreen', 'gold', 'red', 'green', 'violet', 'grey']

x_plot = x_plot.reshape(-1, 1)
for count, degree in enumerate([1, 2, 3]):
	model = make_pipeline(PolynomialFeatures(degree), Ridge())
	model.fit(x_plot, y_train)
	y_plot = model.predict(x_plot)
	plt.plot(x_plot, y_plot, color=colors[count], linewidth=2, label="degree %d" % degree)
plt.legend(loc='lower right')
plt.savefig("plots/regression.png")

plt.clf()


def f(x):
	""" function to approximate by polynomial interpolation"""
	return x * np.sin(x)


# generate points used to plot
x_plot = np.linspace(0, 10, 100)

# generate points and keep a subset of them
x = np.linspace(0, 10, 100)
print(type(x))
print("x ", x)
rng = np.random.RandomState(0)
print("rng ", rng)
rng.shuffle(x)
print("shuffle ", x)
x = np.sort(x[:20])
print("x again ", x)
y = f(x)
print("y ", y)

# create matrix versions of these arrays
X = x[:, np.newaxis]
print("x matrix", X)
X_plot = x_plot[:, np.newaxis]

colors = ['teal', 'yellowgreen', 'gold']
lw = 2
plt.plot(x_plot, f(x_plot), color='cornflowerblue', linewidth=lw, label="ground truth")
plt.scatter(x, y, color='navy', s=30, marker='o', label="training points")

for count, degree in enumerate([3, 4, 5]):
	model = make_pipeline(PolynomialFeatures(degree), Ridge())
	model.fit(X, y)
	y_plot = model.predict(X_plot)
	plt.plot(x_plot, y_plot, color=colors[count], linewidth=lw,
			 label="degree %d" % degree)

plt.legend(loc='lower left')

plt.savefig("plots/other_regression.png")


def plot_with_regression(x, y):
	print("NEW HERE")
	x = np.array(x)
	plt.clf()
	# create matrix versions of these arrays
	X = x[:, np.newaxis]
	print("x matrix", X)
	X_plot = x_plot[:, np.newaxis]

	colors = ['teal', 'yellowgreen', 'gold']
	lw = 2
	plt.plot(x_plot, f(x_plot), color='cornflowerblue', linewidth=lw, label="ground truth")
	plt.scatter(x, y, color='navy', s=30, marker='o', label="training points")

	for count, degree in enumerate([3, 4, 5]):
		model = make_pipeline(PolynomialFeatures(degree), Ridge())
		model.fit(X, y)
		y_plot = model.predict(X_plot)
		plt.plot(x_plot, y_plot, color=colors[count], linewidth=lw,
				 label="degree %d" % degree)

	plt.legend(loc='lower left')

	plt.savefig("plots/my_regression_fnc.png")


plot_with_regression([1, 2, 3, 4, 5, 6], [1, 4, 8, 15, 25, 37])
