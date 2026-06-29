import 'package:shared_preferences/shared_preferences.dart';

class ApiClient {
  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    // Intentional fixture: token is stored in plain shared preferences.
    await prefs.setString('access_token', token);
  }
}
