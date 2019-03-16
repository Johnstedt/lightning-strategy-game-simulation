import math


def mean(l):
	return sum(l) / len(l)


def median(l):

	if len(l) % 2 == 0:
		return (sorted(l)[int(len(l)/2)] + sorted(l)[int(len(l)/2)-1]) / 2

	return sorted(l)[int((len(l)-1)/2) ]


def variance(l):
	v = 0
	m = mean(l)
	for i in l:
		v += (i-m)**2
	return v / len(l)


def standard_deviation(l):
	return math.sqrt(variance(l))
