package com.teleflow.mobile.auth

enum class AuthStage {
    CREDENTIALS,
    OTP,
    PASSWORD,
    AUTHENTICATED
}

data class AuthUiState(
    val stage: AuthStage = AuthStage.CREDENTIALS,
    val loading: Boolean = false,
    val apiId: String = "",
    val apiHash: String = "",
    val phone: String = "",
    val otp: String = "",
    val password: String = "",
    val status: String = "Enter API credentials to continue.",
    val sessionLabel: String = ""
)

data class AuthSession(
    val phone: String,
    val token: String,
    val createdAtMillis: Long
)
