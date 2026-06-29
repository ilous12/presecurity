package example;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class UserController {
  private final Connection connection;

  public UserController(Connection connection) {
    this.connection = connection;
  }

  @GetMapping("/users")
  public String users(@RequestParam String role) throws Exception {
    Statement statement = connection.createStatement();
    // Intentional fixture: request parameter is concatenated into SQL.
    ResultSet rs = statement.executeQuery("select email from users where role = '" + role + "'");
    return rs.next() ? rs.getString("email") : "";
  }
}
