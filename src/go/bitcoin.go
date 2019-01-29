package main

import (
	"encoding/json"
	"fmt"

	// "github.com/btcsuite/btcd/chaincfg" // What is this
	"github.com/btcsuite/btcd/rpcclient"
	// "github.com/btcsuite/btcutil"
	"log"
)

type EstimateSmartFeeCmd struct {
	NumBlocks int64
}

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

	acc, err := client.GetNewAddress("acc1")
	if err != nil {
		//log.Fatalf("error listing accounts: %v", err2)
	}
	fmt.Println(acc)

	fmt.Println(client.DumpPrivKey(acc))

	amount, err := client.GetReceivedByAddress(acc)
	if err != nil {
		log.Fatalf("error listing amount: %v", err)
	}

	fmt.Println(amount)

	reply := rawFee(client, 6)

	fmt.Printf("%f\n", reply.FeeRate)
}

func rawFee(client *rpcclient.Client, fee int) *reply {

	var params []json.RawMessage
	{
		numBlocksJSON, err := json.Marshal(fee)
		if err != nil {
			log.Fatal("could not marshal numBlocks",err)
		}
		/*modeJSON, err := json.Marshal(mode)
		if err != nil {
			return nil, errors.Wrap(err, "could not marshal mode")
		}*/
		params = []json.RawMessage{numBlocksJSON}
	}

	var data json.RawMessage
	{
		var err error
		data, err = client.RawRequest("estimatesmartfee", params)
		if err != nil {
			log.Fatal("could not estimate fee",err)
		}
	}

	var reply = new(reply)
	err := json.Unmarshal(data, &reply)
	if err != nil {
		log.Fatal("could not unmarshal data", err)
	}

	return reply
}

type reply = struct {
	FeeRate float64  `json:"feerate"`
	Blocks  int64    `json:"blocks"`
	Errors  []string `json:"errors,omitempty"`
}

func listTxs(client *rpcclient.Client) *[]transaction {

	var params []json.RawMessage
	{
		params = []json.RawMessage{}
	}

	var data json.RawMessage
	{
		var err error
		data, err = client.RawRequest("listtransactions", params)
		if err != nil {
			log.Fatal("could not estimate fee",err)
		}
	}

	var reply = new([]transaction)
	err := json.Unmarshal(data, &reply)
	if err != nil {
		log.Fatal("could not unmarshal data", err)
	}

	return reply
}

type transaction = struct {
	Address string  `json:"address"`
	Category string `json:"category"`
	Amount  float64    `json:"blocks"`
	Errors  []string `json:"errors,omitempty"`
}