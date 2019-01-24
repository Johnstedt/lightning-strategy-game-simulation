package main

import (
	"fmt"
	"runtime"
)

func split(sum int) (x, y int) {
	x = sum * 98
	y = sum - x
	return
}

func main() {
	fmt.Println(split(5))

	fmt.Print("Go runs on ")
	switch os := runtime.GOOS; os {
	case "darwin":
		fmt.Println("OS X.")
	case "linux":
		fmt.Println("Linux.")
	default:
		// freebsd, openbsd,
		// plan9, windows...
		fmt.Printf("%s.", os)
	}

}
