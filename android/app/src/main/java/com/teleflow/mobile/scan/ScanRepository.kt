package com.teleflow.mobile.scan

import kotlinx.coroutines.flow.Flow

interface ScanRepository {
    suspend fun loadChats(): List<ChatSummary>
    suspend fun loadCachedVideos(chatId: Long): List<VideoItem>
    fun scanChat(chatId: Long): Flow<ScanEvent>
}
