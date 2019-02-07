public class Channel {

    private Node first;
    private Node second;
    private int first_balance;
    private int second_balance;
    private boolean advertiesed;

    Channel(Node first, Node second, int first_balance, int second_balance, boolean advertised){

        this.first = first;
        this.second = second;
        this.first_balance = first_balance;
        this.second_balance = second_balance;
        this.advertiesed  = advertised;
    }

    public Node getOpposite(String id) {
        if(first.getId().equals(id)){
            return second;
        }
        return first;
    }

    public Node getFirst() {
        return first;
    }

    public Node getSecond() {
        return second;
    }

    public int getFirst_balance() {
        return first_balance;
    }

    public int getSecond_balance() {
        return second_balance;
    }

    public boolean isAdvertiesed() {
        return advertiesed;
    }


}
