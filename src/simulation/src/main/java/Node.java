import java.util.*;

public class Node {

    private final String id = UUID.randomUUID().toString();
    private List<Channel> channels;
    private int fee;
    private int funds;

    Node(int fee, int funds) {
        this.fee = fee;
        this.funds = funds;
        this.channels = new ArrayList<>();
    }

    public int getFee() {
        return fee;
    }

    public void addChannel(Channel c){
        channels.add(c);
    }

    // Potentially add extra hops for security
    public void findCheapestPath(Node end, List<Node> nodes){

        System.out.println("NEW TRANSACTION");

        HashMap<Node, Integer> g = new HashMap<>();
        HashMap<Node, Integer> dist = new HashMap<>();
        HashMap<Node, Channel> path = new HashMap<>();

        for(Node n : nodes){
            g.put(n, Integer.MAX_VALUE -100);
            dist.put(n, Integer.MAX_VALUE -100);
            path.put(n, null);
        }

        dist.put(this, 0);
        g.put(this, 0);

        while (!g.isEmpty()){
            Node next = getMinKey(g);

            List<Channel> channels = next.getChannels();

            for( Channel c : channels){
                Integer alt = dist.get(next) + c.getOpposite(next.getId()).getFee();

                if(alt < dist.get(c.getOpposite(next.getId()))){

                    Node point = c.getOpposite(next.getId());
                    dist.put(point, alt);

                    if(g.containsKey(point)){
                        g.put(point, alt);
                    }
                    path.put(point, c);
                }
            }
        }

        Node onWay = end;
        while (!onWay.getId().equals(this.id)){
            Channel c = path.get(onWay);
            System.out.println(c.getFirst().getId() + " " + c.getSecond().getId());
            onWay = c.getOpposite(onWay.getId());
        }

    }

    private Node getMinKey(Map<Node, Integer> map) {
        Node minKey = null;
        int minValue = Integer.MAX_VALUE;
        Set<Node> keys = map.keySet();
        for(Node key : keys) {
            int value = map.get(key);
            if(value < minValue) {
                minValue = value;
                minKey = key;
            }
        }
        map.remove(minKey);
        return minKey;
    }

    private List<Channel> getChannels() {
        return this.channels;
    }

    public String getId(){
        return id;
    }

}