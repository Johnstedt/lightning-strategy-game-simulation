package main

import "fmt"

func swap(x, y string) (string, string) {
	return y, x
}

func main()  {
	a, b := swap("Hi", "Goodby")
	fmt.Println(a, b)
}
