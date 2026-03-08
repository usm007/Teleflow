package com.teleflow.mobile.scan

import com.teleflow.mobile.storage.ScanCacheStore
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import kotlin.math.min
import kotlin.random.Random

class FakeScanRepository(
    private val store: ScanCacheStore
) : ScanRepository {

    override suspend fun loadChats(): List<ChatSummary> {
        delay(160)
        return listOf(
            ChatSummary(1001L, "Product Launch Clips", "channel"),
            ChatSummary(1002L, "Client Deliverables", "group"),
            ChatSummary(1003L, "Personal Saved Media", "dm")
        )
    }

    override suspend fun loadCachedVideos(chatId: Long): List<VideoItem> {
        delay(80)
        return store.loadVideos(chatId)
            ?.sortedByDescending { it.id }
            ?.map { it.copy(isNew = false) }
            ?: emptyList()
    }

    override fun scanChat(chatId: Long): Flow<ScanEvent> = flow {
        val existing = store.loadVideos(chatId).associateBy { it.id }
        val runIndex = store.loadScanCount(chatId)
        val totalCount = 18 + min(runIndex, 4) * 2
        val generated = buildVideoList(chatId, totalCount)

        var scanned = 0
        val merged = existing.toMutableMap()

        generated.chunked(3).forEach { batch ->
            delay(190)
            val newItems = mutableListOf<VideoItem>()
            batch.forEach { item ->
                scanned += 1
                if (!merged.containsKey(item.id)) {
                    val markedNew = item.copy(isNew = true)
                    merged[item.id] = markedNew
                    newItems += markedNew
                }
            }
            emit(ScanEvent.Progress(scanned = scanned, total = generated.size, newItems = newItems))
        }

        val all = merged.values
            .sortedByDescending { it.id }
            .map { it.copy(isNew = false) }

        store.saveVideos(chatId, all)
        store.saveScanCount(chatId, runIndex + 1)

        emit(ScanEvent.Finished(all))
    }

    private fun buildVideoList(chatId: Long, count: Int): List<VideoItem> {
        val now = LocalDateTime.now()
        val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")
        val rng = Random(chatId + count)

        return (0 until count).map { idx ->
            val offset = idx.toLong()
            val date = now.minusHours(offset).format(formatter)
            val id = (chatId * 10_000L) + (count - idx)
            VideoItem(
                id = id,
                chatId = chatId,
                name = "${id}_clip_${idx + 1}.mp4",
                dateAdded = date,
                sizeMb = 6.0 + rng.nextDouble() * 44.0
            )
        }
    }
}
