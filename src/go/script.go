package main

import (
	"fmt"
	"github.com/btcsuite/btcd/txscript"
	"log"
)

func main() {

	builder := txscript.NewScriptBuilder()

	builder.AddOp(txscript.OP_1)
	builder.AddOp(txscript.OP_1)
	builder.AddOp(txscript.OP_ADD)

	scr, err := builder.Script()

	if err != nil {
		log.Fatal("add script failed", err)
	}

	fmt.Printf("%x\n", scr)

}