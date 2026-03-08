package com.teleflow.mobile.auth

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecureSessionStore(context: Context) {
    private val prefs: SharedPreferences

    init {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        prefs = EncryptedSharedPreferences.create(
            context,
            FILE_NAME,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun loadSession(): AuthSession? {
        val phone = prefs.getString(KEY_PHONE, null) ?: return null
        val token = prefs.getString(KEY_TOKEN, null) ?: return null
        val createdAt = prefs.getLong(KEY_CREATED_AT, 0L)
        return AuthSession(phone = phone, token = token, createdAtMillis = createdAt)
    }

    fun saveSession(phone: String, token: String) {
        prefs.edit()
            .putString(KEY_PHONE, phone)
            .putString(KEY_TOKEN, token)
            .putLong(KEY_CREATED_AT, System.currentTimeMillis())
            .apply()
    }

    fun clearSession() {
        prefs.edit().clear().apply()
    }

    companion object {
        private const val FILE_NAME = "teleflow_secure_session"
        private const val KEY_PHONE = "phone"
        private const val KEY_TOKEN = "token"
        private const val KEY_CREATED_AT = "created_at"
    }
}
