# Week 1 | 21-01-2019 - 27-01-2019  

## Done

* Set up this basic weekly logging structure.
* Read the lightning whitepaper.
* Set up bitcoin reference impl @ Cinnober.
* Downloaded testnet history @ home.
* Tunnel traffic to access test- and mainnet from Cinnober to home.
* Connected Go code to access remote node through SSH. 
* Written a project plan with all except risk analysis done. 

## Problems

It is still very unclear how and if it is possible to do a proper evaluation of the fee estimation once an
algorithm is proposed. The Lightning network use onion routing and most contracts will not be settled on the chain 
so an empirical analysis, like chain analysis, will most likely not be possible. I wonder if there is possible to prove
with game theory if a fee estimation can be "selfish" in a given channel network. Is the network even possible to 
model in a game theoretic sense since so much data is absent for the node?   

## Do 

I received a few books from Jerry Eriksson about Game Theory for Wireless networks. The math seems a bit over my head 
but if I find a similar game as the lightning network it would probably be worth it to learn the math behind it and
apply it. 

Anyway some tasks to do next week.

* Email Lightning Labs, Acinq, Blockstream and possibly others to see if anyone has though about this problem and
if any work has been done on it.
* Finnish the project plan, only risk analysis to be written, and hand it in.
* Start with the structure of the report.
* Test sending tx and playing around with the contracts relevant to Lightning, namely Funding tx, Commitment tx, 
Revocable Sequence Maturity Contract(RSMC), Revocable commitment Transaction, Breach Remedy Transaction, Hashed 
Timelock Contract(HTLC). 
* Set up lnd and get familiar with the repository. Find where to put tx code, how it can be updated etc.