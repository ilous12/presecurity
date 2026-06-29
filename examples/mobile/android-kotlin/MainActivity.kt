package example

import android.app.Activity
import android.os.Bundle

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val userId = intent?.data?.getQueryParameter("userId")
        if (userId != null) {
            // Intentional fixture: deep link chooses privileged target without authz.
            deleteAccount(userId)
        }
    }

    private fun deleteAccount(userId: String) {
        println("deleted $userId")
    }
}
