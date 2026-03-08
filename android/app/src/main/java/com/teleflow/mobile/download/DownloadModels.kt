package com.teleflow.mobile.download

enum class DownloadStatus {
    QUEUED,
    DOWNLOADING,
    DONE,
    STOPPED
}

data class DownloadJobItem(
    val id: Long,
    val fileName: String,
    val sizeMb: Double,
    val progress: Int = 0,
    val speedMbps: Double = 0.0,
    val etaSeconds: Int = 0,
    val status: DownloadStatus = DownloadStatus.QUEUED
)

data class DownloadUiState(
    val jobs: List<DownloadJobItem> = emptyList(),
    val concurrency: Int = 3,
    val paused: Boolean = false,
    val statusText: String = "Queue idle"
)

data class DownloadRequest(
    val id: Long,
    val fileName: String,
    val sizeMb: Double
)
