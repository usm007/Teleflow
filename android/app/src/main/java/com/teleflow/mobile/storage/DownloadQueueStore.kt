package com.teleflow.mobile.storage

import android.content.Context
import com.teleflow.mobile.download.DownloadJobItem
import com.teleflow.mobile.download.DownloadStatus
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

data class PersistedQueueState(
    val jobs: List<DownloadJobItem>,
    val paused: Boolean,
    val concurrency: Int
)

class DownloadQueueStore(context: Context) {
    private val file = File(context.filesDir, "download_queue_android.json")

    @Synchronized
    fun load(): PersistedQueueState {
        val root = readRoot()
        val arr = root.optJSONArray("jobs") ?: JSONArray()

        val jobs = mutableListOf<DownloadJobItem>()
        for (i in 0 until arr.length()) {
            val obj = arr.optJSONObject(i) ?: continue
            val statusName = obj.optString("status", DownloadStatus.QUEUED.name)
            val status = runCatching { DownloadStatus.valueOf(statusName) }.getOrDefault(DownloadStatus.QUEUED)
            jobs += DownloadJobItem(
                id = obj.optLong("id"),
                fileName = obj.optString("fileName"),
                sizeMb = obj.optDouble("sizeMb"),
                progress = obj.optInt("progress"),
                speedMbps = obj.optDouble("speedMbps"),
                etaSeconds = obj.optInt("etaSeconds"),
                status = status
            )
        }

        return PersistedQueueState(
            jobs = jobs,
            paused = root.optBoolean("paused", false),
            concurrency = root.optInt("concurrency", 3).coerceIn(1, 10)
        )
    }

    @Synchronized
    fun save(jobs: List<DownloadJobItem>, paused: Boolean, concurrency: Int) {
        val root = JSONObject()
        root.put("paused", paused)
        root.put("concurrency", concurrency)

        val arr = JSONArray()
        jobs.forEach { job ->
            arr.put(
                JSONObject()
                    .put("id", job.id)
                    .put("fileName", job.fileName)
                    .put("sizeMb", job.sizeMb)
                    .put("progress", job.progress)
                    .put("speedMbps", job.speedMbps)
                    .put("etaSeconds", job.etaSeconds)
                    .put("status", job.status.name)
            )
        }
        root.put("jobs", arr)
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
