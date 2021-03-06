package learn_go

import "fmt"

func c() (i int) {
	defer func() { i = i+5 }()
	return 1
}

func main()  {

	fmt.Println(c())
	defer func() { fmt.Println("Game dear main")}()
	f()
	fmt.Println("Back from f")
}

func f() {
	defer func() {
	//	if r := recover(); r != nil {  // recover from panic, will allow main to print line
	//		fmt.Println("Recovered in f", r)
	//	}
		fmt.Println("Game dear friends")
	}()
	fmt.Println("Calling g.")
	g(0)
	fmt.Println("Returned normally from g.")
}

func g(i int) {
	if i > 3 {
		fmt.Println("Panicking!")
		panic(fmt.Sprintf("%v", i))
	}
	defer fmt.Println("Defer in g", i)
	fmt.Println("Printing in g", i)
	g(i + 1)
}