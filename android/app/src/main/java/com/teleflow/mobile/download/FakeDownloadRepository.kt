package com.teleflow.mobile.download

import com.teleflow.mobile.storage.DownloadQueueStore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlin.math.roundToInt
import kotlin.random.Random

class FakeDownloadRepository(
    private val store: DownloadQueueStore
) : DownloadRepository {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    private val _jobs = MutableStateFlow<List<DownloadJobItem>>(emptyList())
    override val jobs: StateFlow<List<DownloadJobItem>> = _jobs.asStateFlow()

    private val _paused = MutableStateFlow(false)
    override val paused: StateFlow<Boolean> = _paused.asStateFlow()

    private val _concurrency = MutableStateFlow(3)
    override val concurrency: StateFlow<Int> = _concurrency.asStateFlow()

    init {
        val persisted = store.load()
        _jobs.value = persisted.jobs
        _paused.value = persisted.paused
        _concurrency.value = persisted.concurrency
        scope.launch { tickLoop() }
    }

    override fun enqueue(items: List<DownloadRequest>) {
        if (items.isEmpty()) return

        val current = _jobs.value
        val existingIds = current.map { it.id }.toSet()
        val additions = items
            .filterNot { existingIds.contains(it.id) }
            .map {
                DownloadJobItem(
                    id = it.id,
                    fileName = it.fileName,
                    sizeMb = it.sizeMb,
                    progress = 0,
                    speedMbps = 0.0,
                    etaSeconds = 0,
                    status = DownloadStatus.QUEUED
                )
            }

        _jobs.value = current + additions
        persistState()
    }

    override fun setConcurrency(value: Int) {
        _concurrency.value = value.coerceIn(1, 10)
        persistState()
    }

    override fun setPaused(value: Boolean) {
        _paused.value = value
        persistState()
    }

    override fun stopAll() {
        _jobs.value = _jobs.value.map {
            if (it.status == DownloadStatus.DONE) it else it.copy(status = DownloadStatus.STOPPED, speedMbps = 0.0, etaSeconds = 0)
        }
        _paused.value = false
        persistState()
    }

    private suspend fun tickLoop() {
        while (true) {
            delay(400)
            val snapshot = _jobs.value
            if (snapshot.isEmpty()) continue

            if (_paused.value) {
                _jobs.value = snapshot.map {
                    if (it.status == DownloadStatus.DOWNLOADING) it.copy(speedMbps = 0.0) else it
                }
                continue
            }

            val activeCount = snapshot.count { it.status == DownloadStatus.DOWNLOADING }
            val slots = (_concurrency.value - activeCount).coerceAtLeast(0)
            var promoted = 0

            val promotedList = snapshot.map { job ->
                if (promoted < slots && job.status == DownloadStatus.QUEUED) {
                    promoted += 1
                    job.copy(status = DownloadStatus.DOWNLOADING)
                } else {
                    job
                }
            }

            val updated = promotedList.map { job ->
                if (job.status != DownloadStatus.DOWNLOADING) return@map job

                val speed = 0.8 + Random.nextDouble() * 2.4
                val increment = (speed * 5.0).roundToInt().coerceAtLeast(1)
                val next = (job.progress + increment).coerceAtMost(100)
                val remainingPercent = (100 - next).coerceAtLeast(0)
                val eta = if (next >= 100) 0 else (remainingPercent / increment.toDouble() * 2.0).roundToInt().coerceAtLeast(1)

                if (next >= 100) {
                    job.copy(progress = 100, status = DownloadStatus.DONE, speedMbps = 0.0, etaSeconds = 0)
                } else {
                    job.copy(progress = next, speedMbps = speed, etaSeconds = eta)
                }
            }

            _jobs.value = updated
            persistState()
        }
    }

    private fun persistState() {
        scope.launch {
            store.save(
                jobs = _jobs.value,
                paused = _paused.value,
                concurrency = _concurrency.value
            )
        }
    }
}
