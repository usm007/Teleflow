package com.teleflow.mobile.scan

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class ScanViewModel(
    private val repository: ScanRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(ScanUiState())
    val uiState: StateFlow<ScanUiState> = _uiState.asStateFlow()

    private var scanJob: Job? = null

    fun loadChats() {
        viewModelScope.launch {
            runCatching {
                repository.loadChats()
            }.onSuccess { chats ->
                val firstId = chats.firstOrNull()?.id
                _uiState.update {
                    it.copy(
                        loadingChats = false,
                        chats = chats,
                        selectedChatId = firstId,
                        lastError = ""
                    )
                }
                if (firstId != null) {
                    selectChat(firstId)
                }
            }.onFailure { err ->
                _uiState.update {
                    it.copy(loadingChats = false, lastError = err.message ?: "Failed to load chats")
                }
            }
        }
    }

    fun selectChat(chatId: Long) {
        scanJob?.cancel()
        viewModelScope.launch {
            val cached = repository.loadCachedVideos(chatId)
            _uiState.update {
                it.copy(
                    selectedChatId = chatId,
                    videos = cached,
                    cacheStatus = if (cached.isNotEmpty()) "Loaded ${cached.size} cached videos. Refreshing..." else "No cached videos yet. Scanning...",
                    progressStatus = if (cached.isNotEmpty()) "Scan progress: ${cached.size} / ?" else "Scan progress: 0 / ?",
                    scanInProgress = true,
                    lastError = ""
                )
            }

            scanJob = launch {
                repository.scanChat(chatId).collect { event ->
                    when (event) {
                        is ScanEvent.Progress -> handleProgress(event)
                        is ScanEvent.Finished -> handleFinished(event)
                    }
                }
            }
        }
    }

    fun onSearchQueryChange(query: String) {
        _uiState.update { it.copy(searchQuery = query) }
    }

    private fun handleProgress(progress: ScanEvent.Progress) {
        val pct = if (progress.total > 0) {
            ((progress.scanned.toDouble() / progress.total.toDouble()) * 100).toInt().coerceIn(0, 100)
        } else {
            0
        }

        _uiState.update { state ->
            val merged = (state.videos + progress.newItems)
                .associateBy { it.id }
                .values
                .sortedByDescending { it.id }

            state.copy(
                videos = merged,
                progressStatus = "Scan progress: ${progress.scanned} / ${progress.total} (${pct}%)",
                scanInProgress = true
            )
        }
    }

    private fun handleFinished(event: ScanEvent.Finished) {
        _uiState.update {
            it.copy(
                videos = event.allVideos,
                cacheStatus = "Scan refreshed",
                progressStatus = "Scan complete: ${event.allVideos.size} files",
                scanInProgress = false
            )
        }
    }

    companion object {
        fun factory(repository: ScanRepository): ViewModelProvider.Factory {
            return object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T {
                    return ScanViewModel(repository) as T
                }
            }
        }
    }
}
