package com.teleflow.mobile.download

import kotlinx.coroutines.flow.StateFlow

interface DownloadRepository {
    val jobs: StateFlow<List<DownloadJobItem>>
    val paused: StateFlow<Boolean>
    val concurrency: StateFlow<Int>

    fun enqueue(items: List<DownloadRequest>)
    fun setConcurrency(value: Int)
    fun setPaused(value: Boolean)
    fun stopAll()
}
