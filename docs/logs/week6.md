# Done

* Simulation improved slightly with liquidity checks and Dijkstra rerouting if not liquid. The rerouting
part is not done yet.
* The book borrowed from Gabriel might be appropriate for this problem, read the two first chapters
and it may be useful in applying game theoretic structure to this graph problem. 
* Optimized the price curve problem, takes 33 minutes with Johnson, slightly longer Floyd-Warshall 
* Finnish Lightning segment, only needs last re-reading.
* Did two huge plots on the mainnet, testnet networks with Gephi. 

# Problem

This problem seem to go only deeper and deeper. A huge hurdle to add discounts to the fee price for a 
balanced channel as the fee calculation is quite stupid and does not discriminate the difference in 
channel state. Next week I must draft a proposal to change this in the protocol.

The simulation is still possible to do without this, but remarks on throughput might be mute
since a protocol improvement might do more for throughput than som policies ever may.  

# Do

* Draft proposal to change fee structure.
* Finnish document for peer review 1.
* Get rerouting if path not liquid in simulation. 
* Curving the price curve dependent on discount and or liquidity. How even? 
* Figure out approximate methods for price simulation.
* Closing and opening channel strategies in simulation instead of only opening when joining.


