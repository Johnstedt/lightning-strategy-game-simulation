import java.util.ArrayList;
import java.util.List;

public class Game {

    List<Player> players;
    List<Node> nodes;

    Game(List<Player> players){
        this.players = players;
        this.nodes = new ArrayList<>();
    }

    void play(){

        int time = 10;
        int routing = 10;
        int nonrouting = 100;

        for(int i = 0; i < routing; i++){

            Node newNode = new Node(1, 10000);

            if(i != 0) {
                for (Node n : nodes) {
                    Channel c = new Channel(newNode, n, 1000, 1000, true);
                    n.addChannel(c);
                    newNode.addChannel(c);
                }
            }
            nodes.add(newNode);
        }

        for(int i = 0; i < nonrouting; i++){

            Node newNode = new Node(1, 10000);

            Channel c = new Channel(newNode, nodes.get(i % 10), 1000,100, false);
            nodes.get(i % 10).addChannel(c);
            newNode.addChannel(c);

            nodes.add(newNode);
        }

        for (Node n : nodes){



        }

        for(int i = 0; i < time; i++){
            nodes.get(20 + i).findCheapestPath(nodes.get(40 + i), nodes);
        }


    }
}