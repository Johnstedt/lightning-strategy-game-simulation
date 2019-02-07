import java.util.List;

public class Player {

    private String type;
    private List<Policies> policies;

    Player(String type, List<Policies> policies){
        this.type = type;
        this.policies = policies;
    }
}