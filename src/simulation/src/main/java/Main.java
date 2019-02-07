import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;

public class Main {



    public static void main(String[] args){

        Game g = new Game(
                Arrays.asList(
                        new Player("Routing_Node", Arrays.asList(Policies.INCREASE_PRICE, Policies.DECREASE_PRICE)),
                        new Player("Non_Routing_Node", Collections.singletonList(Policies.PAY))
                )
        );

        g.play();
    }

}