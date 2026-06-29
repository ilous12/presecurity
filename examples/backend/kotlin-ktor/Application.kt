package example

import io.ktor.server.application.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Application.module() {
    routing {
        get("/admin/users/{id}") {
            val id = call.parameters["id"] ?: return@get call.respondText("missing")
            // Intentional fixture: admin data is returned without authz checks.
            call.respondText("admin user record: $id")
        }
    }
}
