package main


import (
	"fmt"

	// "github.com/btcsuite/btcd/chaincfg"
"github.com/btcsuite/btcd/rpcclient"
// "github.com/btcsuite/btcutil"
"log"
)

func main() {
	// create new client instance
	client, err := rpcclient.New(&rpcclient.ConnConfig{
		HTTPPostMode: true,
		DisableTLS:   true,
		Host:         "127.0.0.1:18332",
		User:         "admin",
		Pass:         "admin",
	}, nil)
	if err != nil {
		log.Fatalf("error creating new btc client: %v", err)
	}

	fmt.Println(client)

	// list accounts
	blocks, err := client.GetBlockCount()
	if err != nil {
		log.Fatalf("error listing accounts: %v", err)
	}
	fmt.Println(blocks)


	//thing, err := client.

}