package main

import (
	"encoding/hex"
	"encoding/json"
	"fmt"
	"github.com/btcsuite/btcd/chaincfg/chainhash"


	"github.com/btcsuite/btcd/wire"

	"github.com/btcsuite/btcd/rpcclient"
	"log"

	"github.com/itchyny/base58-go"
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


	reply := rawFee(client, 6)

	fmt.Printf("%f\n", reply.FeeRate)

	roughTx()
}

func roughTx()  {

	//tx := wire.NewMsgTx(2)

	encoding := base58.FlickrEncoding

	encoded, err := encoding.Encode([]byte("100"))
	if err != nil {
		fmt.Println(err.Error())

	}
	fmt.Println(encoded)

	out1, _ := encoding.Decode([]byte("2N8UVXCopUgBtCbi1j5E8HBCFdKLXsjkEdc"))

	fmt.Println(out1)

	//output2, _ := hex.DecodeString()

}

func Input() *wire.OutPoint{
	txHash, _ := hex.DecodeString("cf6ac19824c3e35d22c2feaf8e2e7fbd60803137c537220f80774ea21f09add0")
	txHash = reverse(txHash)
	prevTxHash, _ := chainhash.NewHash(txHash)

	prevTxHash.SetBytes(txHash)

	return wire.NewOutPoint(prevTxHash, 0)

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

func reverse(numbers []byte) []byte {
	newNumbers := make([]byte, len(numbers))
	for i, j := 0, len(numbers)-1; i < j; i, j = i+1, j-1 {
		newNumbers[i], newNumbers[j] = numbers[j], numbers[i]
	}
	return newNumbers
}