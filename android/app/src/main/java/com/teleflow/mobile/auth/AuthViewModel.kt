package com.teleflow.mobile.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class AuthViewModel(
    private val repository: AuthRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    fun restoreSession() {
        viewModelScope.launch {
            val session = repository.restoreSession()
            if (session != null) {
                _uiState.update {
                    it.copy(
                        stage = AuthStage.AUTHENTICATED,
                        sessionLabel = session.phone,
                        status = "Session restored"
                    )
                }
            }
        }
    }

    fun onApiIdChange(value: String) = _uiState.update { it.copy(apiId = value) }
    fun onApiHashChange(value: String) = _uiState.update { it.copy(apiHash = value) }
    fun onPhoneChange(value: String) = _uiState.update { it.copy(phone = value) }
    fun onOtpChange(value: String) = _uiState.update { it.copy(otp = value) }
    fun onPasswordChange(value: String) = _uiState.update { it.copy(password = value) }

    fun submitCredentials() {
        val current = _uiState.value
        setLoading(true)
        viewModelScope.launch {
            runCatching {
                repository.submitCredentials(current.apiId, current.apiHash, current.phone)
            }.onSuccess { stage ->
                _uiState.update {
                    it.copy(
                        stage = stage,
                        loading = false,
                        status = "OTP requested for ${current.phone}"
                    )
                }
            }.onFailure { error ->
                setError(error.message ?: "Failed to submit credentials")
            }
        }
    }

    fun submitOtp() {
        val code = _uiState.value.otp
        setLoading(true)
        viewModelScope.launch {
            runCatching { repository.submitOtp(code) }
                .onSuccess { stage ->
                    when (stage) {
                        AuthStage.PASSWORD -> {
                            _uiState.update {
                                it.copy(
                                    stage = AuthStage.PASSWORD,
                                    loading = false,
                                    status = "2FA password required"
                                )
                            }
                        }

                        AuthStage.AUTHENTICATED -> {
                            _uiState.update {
                                it.copy(
                                    stage = AuthStage.AUTHENTICATED,
                                    loading = false,
                                    sessionLabel = it.phone,
                                    status = "Authenticated"
                                )
                            }
                        }

                        else -> setError("Unexpected auth stage")
                    }
                }
                .onFailure { error ->
                    setError(error.message ?: "Failed to verify OTP")
                }
        }
    }

    fun submitPassword() {
        val pwd = _uiState.value.password
        setLoading(true)
        viewModelScope.launch {
            runCatching { repository.submitPassword(pwd) }
                .onSuccess {
                    _uiState.update {
                        it.copy(
                            stage = AuthStage.AUTHENTICATED,
                            loading = false,
                            sessionLabel = it.phone,
                            status = "Authenticated"
                        )
                    }
                }
                .onFailure { error ->
                    setError(error.message ?: "Password verification failed")
                }
        }
    }

    fun signOut() {
        viewModelScope.launch {
            repository.signOut()
            _uiState.value = AuthUiState(status = "Signed out")
        }
    }

    private fun setLoading(value: Boolean) {
        _uiState.update { it.copy(loading = value) }
    }

    private fun setError(message: String) {
        _uiState.update { it.copy(loading = false, status = message) }
    }

    companion object {
        fun factory(repository: AuthRepository): ViewModelProvider.Factory {
            return object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T {
                    return AuthViewModel(repository) as T
                }
            }
        }
    }
}
