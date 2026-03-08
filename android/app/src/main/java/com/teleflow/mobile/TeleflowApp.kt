package com.teleflow.mobile

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.TextButton
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.teleflow.mobile.auth.AndroidAuthRepository
import com.teleflow.mobile.auth.AuthStage
import com.teleflow.mobile.auth.AuthViewModel
import com.teleflow.mobile.auth.SecureSessionStore
import com.teleflow.mobile.background.BackgroundCoordinator
import com.teleflow.mobile.download.DownloadStatus
import com.teleflow.mobile.download.DownloadViewModel
import com.teleflow.mobile.download.FakeDownloadRepository
import com.teleflow.mobile.storage.DownloadQueueStore
import com.teleflow.mobile.ui.AuthScreen
import com.teleflow.mobile.ui.DownloadQueueScreen
import com.teleflow.mobile.scan.FakeScanRepository
import com.teleflow.mobile.scan.ScanViewModel
import com.teleflow.mobile.storage.ScanCacheStore
import com.teleflow.mobile.ui.ScanScreen

@Composable
fun TeleflowApp() {
    val context = LocalContext.current
    val authRepository = remember(context) { provideAuthRepository(context) }
    val scanRepository = remember(context) { provideScanRepository(context) }
    val downloadRepository = remember(context) { provideDownloadRepository(context) }
    val authViewModel: AuthViewModel = viewModel(factory = AuthViewModel.factory(authRepository))
    val scanViewModel: ScanViewModel = viewModel(factory = ScanViewModel.factory(scanRepository))
    val downloadViewModel: DownloadViewModel = viewModel(factory = DownloadViewModel.factory(downloadRepository))
    val authState by authViewModel.uiState.collectAsStateWithLifecycle()
    val scanState by scanViewModel.uiState.collectAsStateWithLifecycle()
    val downloadState by downloadViewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        authViewModel.restoreSession()
        scanViewModel.loadChats()
    }

    LaunchedEffect(downloadState.jobs, downloadState.paused) {
        val active = downloadState.jobs.count { it.status == DownloadStatus.DOWNLOADING }
        val queued = downloadState.jobs.count { it.status == DownloadStatus.QUEUED }
        val hasWork = active > 0 || queued > 0

        if (hasWork) {
            BackgroundCoordinator.startQueueRuntime(context, active, queued)
        } else {
            BackgroundCoordinator.stopQueueRuntime(context)
        }
    }

    MaterialTheme {
        Scaffold(
            topBar = {
                TopAppBar(
                    title = {
                        Text("Teleflow Android", fontWeight = FontWeight.SemiBold)
                    },
                    actions = {
                        if (authState.stage == AuthStage.AUTHENTICATED) {
                            TextButton(onClick = { authViewModel.signOut() }) {
                                Text("Sign out")
                            }
                        }
                    }
                )
            }
        ) { innerPadding ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .background(
                        Brush.verticalGradient(
                            colors = listOf(
                                Color(0xFF06111A),
                                Color(0xFF0B1E2C),
                                Color(0xFF0D2A26)
                            )
                        )
                    )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    if (authState.stage == AuthStage.AUTHENTICATED) {
                        SectionCard(
                            title = "Phase 3 Scan Flow",
                            body = "Cached-first video list and inline scan progress are now wired on Android."
                        )
                        ScanScreen(
                            state = scanState,
                            onSelectChat = scanViewModel::selectChat,
                            onSearchQueryChange = scanViewModel::onSearchQueryChange
                        )
                        DownloadQueueScreen(
                            state = downloadState,
                            onQueueLatest = { downloadViewModel.enqueueFromVideos(scanState.videos) },
                            onIncreaseConcurrency = downloadViewModel::increaseConcurrency,
                            onDecreaseConcurrency = downloadViewModel::decreaseConcurrency,
                            onTogglePause = downloadViewModel::togglePause,
                            onStopAll = downloadViewModel::stopAll
                        )
                    } else {
                        AuthScreen(
                            state = authState,
                            onApiIdChange = authViewModel::onApiIdChange,
                            onApiHashChange = authViewModel::onApiHashChange,
                            onPhoneChange = authViewModel::onPhoneChange,
                            onOtpChange = authViewModel::onOtpChange,
                            onPasswordChange = authViewModel::onPasswordChange,
                            onSubmitCredentials = authViewModel::submitCredentials,
                            onSubmitOtp = authViewModel::submitOtp,
                            onSubmitPassword = authViewModel::submitPassword
                        )
                    }
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "Desktop behavior from main.py/core.py is being ported incrementally. Next: real Telegram transport and download queue parity.",
                        color = Color(0xFFD9EEF2),
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }
    }
}

@Composable
private fun SectionCard(title: String, body: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xCC10222F))
    ) {
        Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(text = title, color = Color(0xFF86E3C3), fontWeight = FontWeight.Bold)
            Text(text = body, color = Color(0xFFE9F5F8), style = MaterialTheme.typography.bodyMedium)
        }
    }
}

private fun provideAuthRepository(context: Context): AndroidAuthRepository {
    val appContext = context.applicationContext
    return AndroidAuthRepository(SecureSessionStore(appContext))
}

private fun provideScanRepository(context: Context): FakeScanRepository {
    val appContext = context.applicationContext
    return FakeScanRepository(ScanCacheStore(appContext))
}

private fun provideDownloadRepository(context: Context): FakeDownloadRepository {
    val appContext = context.applicationContext
    return FakeDownloadRepository(DownloadQueueStore(appContext))
}
