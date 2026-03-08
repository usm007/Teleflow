package com.teleflow.mobile.scan

data class ChatSummary(
    val id: Long,
    val name: String,
    val type: String
)

data class VideoItem(
    val id: Long,
    val chatId: Long,
    val name: String,
    val dateAdded: String,
    val sizeMb: Double,
    val isNew: Boolean = false
)

data class ScanUiState(
    val loadingChats: Boolean = true,
    val chats: List<ChatSummary> = emptyList(),
    val selectedChatId: Long? = null,
    val videos: List<VideoItem> = emptyList(),
    val cacheStatus: String = "",
    val progressStatus: String = "",
    val scanInProgress: Boolean = false,
    val searchQuery: String = "",
    val lastError: String = ""
)

sealed class ScanEvent {
    data class Progress(
        val scanned: Int,
        val total: Int,
        val newItems: List<VideoItem>
    ) : ScanEvent()

    data class Finished(val allVideos: List<VideoItem>) : ScanEvent()
}
