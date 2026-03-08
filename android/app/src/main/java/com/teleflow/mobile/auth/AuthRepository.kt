package com.teleflow.mobile.auth

interface AuthRepository {
    suspend fun restoreSession(): AuthSession?
    suspend fun submitCredentials(apiId: String, apiHash: String, phone: String): AuthStage
    suspend fun submitOtp(code: String): AuthStage
    suspend fun submitPassword(password: String): AuthStage
    suspend fun signOut()
}
