package com.teleflow.mobile.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.teleflow.mobile.auth.AuthStage
import com.teleflow.mobile.auth.AuthUiState

@Composable
fun AuthScreen(
    state: AuthUiState,
    onApiIdChange: (String) -> Unit,
    onApiHashChange: (String) -> Unit,
    onPhoneChange: (String) -> Unit,
    onOtpChange: (String) -> Unit,
    onPasswordChange: (String) -> Unit,
    onSubmitCredentials: () -> Unit,
    onSubmitOtp: () -> Unit,
    onSubmitPassword: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xCC10222F))
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text("Telegram Authentication", fontWeight = FontWeight.SemiBold, color = Color(0xFFB4F3DF))
            Text(state.status, color = Color(0xFFDCEFF5))

            when (state.stage) {
                AuthStage.CREDENTIALS -> {
                    OutlinedTextField(
                        value = state.apiId,
                        onValueChange = onApiIdChange,
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("API ID") },
                        enabled = !state.loading
                    )
                    OutlinedTextField(
                        value = state.apiHash,
                        onValueChange = onApiHashChange,
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("API Hash") },
                        visualTransformation = PasswordVisualTransformation(),
                        enabled = !state.loading
                    )
                    OutlinedTextField(
                        value = state.phone,
                        onValueChange = onPhoneChange,
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("Phone (+countrycode)") },
                        enabled = !state.loading
                    )
                    Button(onClick = onSubmitCredentials, enabled = !state.loading) {
                        Text("Request OTP")
                    }
                }

                AuthStage.OTP -> {
                    OutlinedTextField(
                        value = state.otp,
                        onValueChange = onOtpChange,
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("OTP Code") },
                        enabled = !state.loading
                    )
                    Text(
                        "Tip: use OTP 0000 to simulate password-required flow.",
                        color = Color(0xFFA3B7BE)
                    )
                    Button(onClick = onSubmitOtp, enabled = !state.loading) {
                        Text("Verify OTP")
                    }
                }

                AuthStage.PASSWORD -> {
                    OutlinedTextField(
                        value = state.password,
                        onValueChange = onPasswordChange,
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("2FA Password") },
                        visualTransformation = PasswordVisualTransformation(),
                        enabled = !state.loading
                    )
                    Button(onClick = onSubmitPassword, enabled = !state.loading) {
                        Text("Verify Password")
                    }
                }

                AuthStage.AUTHENTICATED -> {
                    Text("Authenticated for ${state.sessionLabel}", color = Color(0xFF8FE0BD))
                }
            }

            if (state.loading) {
                Spacer(modifier = Modifier.height(6.dp))
                Text("Working...", color = Color(0xFFECECEC))
            }
        }
    }
}
