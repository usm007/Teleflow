package com.teleflow.mobile.storage

import android.content.Context
import com.teleflow.mobile.scan.VideoItem
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

class ScanCacheStore(context: Context) {
    private val file = File(context.filesDir, "scan_cache_android.json")

    @Synchronized
    fun loadVideos(chatId: Long): List<VideoItem> {
        val root = readRoot()
        val chats = root.optJSONObject("chats") ?: return emptyList()
        val arr = chats.optJSONArray(chatId.toString()) ?: return emptyList()

        val out = mutableListOf<VideoItem>()
        for (i in 0 until arr.length()) {
            val obj = arr.optJSONObject(i) ?: continue
            out += VideoItem(
                id = obj.optLong("id"),
                chatId = obj.optLong("chatId", chatId),
                name = obj.optString("name"),
                dateAdded = obj.optString("dateAdded"),
                sizeMb = obj.optDouble("sizeMb"),
                isNew = false
            )
        }
        return out
    }

    @Synchronized
    fun saveVideos(chatId: Long, videos: List<VideoItem>) {
        val root = readRoot()
        val chats = root.optJSONObject("chats") ?: JSONObject().also { root.put("chats", it) }
        val arr = JSONArray()
        videos.forEach { item ->
            arr.put(
                JSONObject()
                    .put("id", item.id)
                    .put("chatId", item.chatId)
                    .put("name", item.name)
                    .put("dateAdded", item.dateAdded)
                    .put("sizeMb", item.sizeMb)
            )
        }
        chats.put(chatId.toString(), arr)
        writeRoot(root)
    }

    @Synchronized
    fun loadScanCount(chatId: Long): Int {
        val root = readRoot()
        val counts = root.optJSONObject("scanCounts") ?: return 0
        return counts.optInt(chatId.toString(), 0)
    }

    @Synchronized
    fun saveScanCount(chatId: Long, count: Int) {
        val root = readRoot()
        val counts = root.optJSONObject("scanCounts") ?: JSONObject().also { root.put("scanCounts", it) }
        counts.put(chatId.toString(), count)
        writeRoot(root)
    }

    private fun readRoot(): JSONObject {
        return runCatching {
            if (!file.exists()) {
                JSONObject()
            } else {
                val text = file.readText(Charsets.UTF_8)
                if (text.isBlank()) JSONObject() else JSONObject(text)
            }
        }.getOrElse {
            JSONObject()
        }
    }

    private fun writeRoot(root: JSONObject) {
        if (!file.parentFile.exists()) {
            file.parentFile.mkdirs()
        }
        file.writeText(root.toString(), Charsets.UTF_8)
    }
}
