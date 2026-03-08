package com.teleflow.mobile.download

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.teleflow.mobile.scan.VideoItem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class DownloadViewModel(
    private val repository: DownloadRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(DownloadUiState())
    val uiState: StateFlow<DownloadUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            combine(repository.jobs, repository.concurrency, repository.paused) { jobs, concurrency, paused ->
                val active = jobs.count { it.status == DownloadStatus.DOWNLOADING }
                val queued = jobs.count { it.status == DownloadStatus.QUEUED }
                val done = jobs.count { it.status == DownloadStatus.DONE }
                val status = when {
                    paused -> "Paused • Active $active • Queued $queued • Done $done"
                    jobs.isEmpty() -> "Queue idle"
                    else -> "Running • Active $active • Queued $queued • Done $done"
                }
                DownloadUiState(
                    jobs = jobs,
                    concurrency = concurrency,
                    paused = paused,
                    statusText = status
                )
            }.collect { state ->
                _uiState.value = state
            }
        }
    }

    fun enqueueFromVideos(videos: List<VideoItem>, maxCount: Int = 5) {
        val picks = videos.take(maxCount).map {
            DownloadRequest(id = it.id, fileName = it.name, sizeMb = it.sizeMb)
        }
        repository.enqueue(picks)
    }

    fun increaseConcurrency() {
        repository.setConcurrency(_uiState.value.concurrency + 1)
    }

    fun decreaseConcurrency() {
        repository.setConcurrency(_uiState.value.concurrency - 1)
    }

    fun togglePause() {
        repository.setPaused(!_uiState.value.paused)
    }

    fun stopAll() {
        repository.stopAll()
    }

    companion object {
        fun factory(repository: DownloadRepository): ViewModelProvider.Factory {
            return object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T {
                    return DownloadViewModel(repository) as T
                }
            }
        }
    }
}
