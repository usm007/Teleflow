package com.teleflow.mobile.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AssistChip
import androidx.compose.material3.AssistChipDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.teleflow.mobile.scan.ChatSummary
import com.teleflow.mobile.scan.ScanUiState
import com.teleflow.mobile.scan.VideoItem

@Composable
fun ScanScreen(
    state: ScanUiState,
    onSelectChat: (Long) -> Unit,
    onSearchQueryChange: (String) -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        ChatsRow(
            chats = state.chats,
            selectedChatId = state.selectedChatId,
            onSelectChat = onSelectChat
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(state.cacheStatus, color = Color(0xFF8ADDC0), style = MaterialTheme.typography.bodySmall)
            Spacer(modifier = Modifier.weight(1f))
            Text(state.progressStatus, color = Color(0xFF95D6FF), style = MaterialTheme.typography.bodySmall)
        }

        OutlinedTextField(
            value = state.searchQuery,
            onValueChange = onSearchQueryChange,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Search files") }
        )

        VideoListCard(
            videos = state.videos.filter {
                state.searchQuery.isBlank() || it.name.contains(state.searchQuery, ignoreCase = true)
            }
        )

        if (state.lastError.isNotBlank()) {
            Text(state.lastError, color = Color(0xFFFF9FA9))
        }
    }
}

@Composable
private fun ChatsRow(
    chats: List<ChatSummary>,
    selectedChatId: Long?,
    onSelectChat: (Long) -> Unit
) {
    if (chats.isEmpty()) {
        Text("Loading chats...", color = Color(0xFFE4EDF1))
        return
    }

    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.height(120.dp)) {
        items(chats) { chat ->
            val selected = chat.id == selectedChatId
            AssistChip(
                onClick = { onSelectChat(chat.id) },
                label = { Text("${chat.name} (${chat.type})") },
                colors = AssistChipDefaults.assistChipColors(
                    containerColor = if (selected) Color(0xFF185043) else Color(0xFF123143),
                    labelColor = Color(0xFFE8F6FB)
                )
            )
        }
    }
}

@Composable
private fun VideoListCard(videos: List<VideoItem>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xCC0F2331))
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Videos", color = Color(0xFFBDE9D7), fontWeight = FontWeight.SemiBold)
            if (videos.isEmpty()) {
                Text("No videos yet", color = Color(0xFF9EB8C4))
            } else {
                LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.height(300.dp)) {
                    items(videos, key = { it.id }) { item ->
                        VideoRow(item)
                    }
                }
            }
        }
    }
}

@Composable
private fun VideoRow(item: VideoItem) {
    Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(item.name, color = Color(0xFFEAF6FA), style = MaterialTheme.typography.bodyMedium)
            Text(
                "${item.dateAdded}  |  ${"%.1f".format(item.sizeMb)} MB",
                color = Color(0xFF9EB8C4),
                style = MaterialTheme.typography.bodySmall
            )
        }
        if (item.isNew) {
            Text("NEW", color = Color(0xFF92F3B8), fontWeight = FontWeight.Bold)
        }
    }
}
