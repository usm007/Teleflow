package com.teleflow.mobile.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.teleflow.mobile.download.DownloadJobItem
import com.teleflow.mobile.download.DownloadStatus
import com.teleflow.mobile.download.DownloadUiState

@Composable
fun DownloadQueueScreen(
    state: DownloadUiState,
    onQueueLatest: () -> Unit,
    onIncreaseConcurrency: () -> Unit,
    onDecreaseConcurrency: () -> Unit,
    onTogglePause: () -> Unit,
    onStopAll: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xCC122B3D)),
        shape = RoundedCornerShape(14.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Text("Download Queue", color = Color(0xFFBEE8FF), fontWeight = FontWeight.SemiBold)
                androidx.compose.foundation.layout.Spacer(modifier = Modifier.weight(1f))
                Text(state.statusText, color = Color(0xFF9CC8DD), style = MaterialTheme.typography.bodySmall)
            }

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                Button(onClick = onQueueLatest) { Text("Queue Latest 5") }
                Button(onClick = onDecreaseConcurrency) { Text("-") }
                Text(
                    text = "${state.concurrency}",
                    color = Color.White,
                    modifier = Modifier
                        .background(Color(0x552B4253), RoundedCornerShape(8.dp))
                        .padding(horizontal = 10.dp, vertical = 8.dp)
                )
                Button(onClick = onIncreaseConcurrency) { Text("+") }
                Button(onClick = onTogglePause) { Text(if (state.paused) "Resume" else "Pause") }
                Button(onClick = onStopAll) { Text("Stop") }
            }

            if (state.jobs.isEmpty()) {
                Text("No queued downloads", color = Color(0xFFAFC6D0))
            } else {
                LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.height(240.dp)) {
                    items(state.jobs, key = { it.id }) { job ->
                        JobRow(job)
                    }
                }
            }
        }
    }
}

@Composable
private fun JobRow(job: DownloadJobItem) {
    val statusColor = when (job.status) {
        DownloadStatus.QUEUED -> Color(0xFFE8D17A)
        DownloadStatus.DOWNLOADING -> Color(0xFF95D6FF)
        DownloadStatus.DONE -> Color(0xFF8DE3B0)
        DownloadStatus.STOPPED -> Color(0xFFFFA2AE)
    }

    Card(colors = CardDefaults.cardColors(containerColor = Color(0x99384D5C))) {
        Column(modifier = Modifier.fillMaxWidth().padding(10.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(job.fileName, color = Color(0xFFF2F8FB), modifier = Modifier.weight(1f), style = MaterialTheme.typography.bodyMedium)
                Text(job.status.name, color = statusColor, style = MaterialTheme.typography.bodySmall)
            }
            LinearProgressIndicator(progress = { job.progress / 100f }, modifier = Modifier.fillMaxWidth())
            Text(
                text = "${job.progress}%  |  ${"%.2f".format(job.speedMbps)} MB/s  |  ETA ${job.etaSeconds}s",
                color = Color(0xFFABC5CF),
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}
