package com.teleflow.mobile.auth

import kotlinx.coroutines.delay
import java.util.UUID

class AndroidAuthRepository(
    private val store: SecureSessionStore
) : AuthRepository {
    private var currentPhone: String = ""
    private var awaitingPassword = false

    override suspend fun restoreSession(): AuthSession? {
        return store.loadSession()
    }

    override suspend fun submitCredentials(apiId: String, apiHash: String, phone: String): AuthStage {
        delay(250)
        require(apiId.toIntOrNull() != null) { "API ID must be numeric." }
        require(apiHash.trim().length >= 8) { "API Hash seems invalid." }
        require(phone.trim().startsWith("+")) { "Phone should start with + and country code." }

        currentPhone = phone.trim()
        awaitingPassword = false
        return AuthStage.OTP
    }

    override suspend fun submitOtp(code: String): AuthStage {
        delay(220)
        require(code.length >= 4) { "OTP code is too short." }

        if (code == "0000") {
            awaitingPassword = true
            return AuthStage.PASSWORD
        }

        store.saveSession(
            phone = currentPhone,
            token = "session_${UUID.randomUUID()}"
        )
        awaitingPassword = false
        return AuthStage.AUTHENTICATED
    }

    override suspend fun submitPassword(password: String): AuthStage {
        delay(220)
        require(awaitingPassword) { "Password flow not active." }
        require(password.length >= 6) { "Password is too short." }

        store.saveSession(
            phone = currentPhone,
            token = "session_${UUID.randomUUID()}"
        )
        awaitingPassword = false
        return AuthStage.AUTHENTICATED
    }

    override suspend fun signOut() {
        store.clearSession()
        currentPhone = ""
        awaitingPassword = false
    }
}
