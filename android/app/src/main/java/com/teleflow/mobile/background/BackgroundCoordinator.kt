package com.teleflow.mobile.background

import android.content.Context
import android.content.Intent
import androidx.core.content.ContextCompat
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import com.teleflow.mobile.download.DownloadForegroundService

object BackgroundCoordinator {
    private const val HEARTBEAT_WORK_NAME = "teleflow_queue_heartbeat"

    fun startQueueRuntime(context: Context, active: Int, queued: Int) {
        val appContext = context.applicationContext
        val intent = Intent(appContext, DownloadForegroundService::class.java).apply {
            putExtra(DownloadForegroundService.EXTRA_ACTIVE, active)
            putExtra(DownloadForegroundService.EXTRA_QUEUED, queued)
        }
        ContextCompat.startForegroundService(appContext, intent)

        val work = OneTimeWorkRequestBuilder<QueueHeartbeatWorker>().build()
        WorkManager.getInstance(appContext)
            .enqueueUniqueWork(HEARTBEAT_WORK_NAME, ExistingWorkPolicy.REPLACE, work)
    }

    fun stopQueueRuntime(context: Context) {
        val appContext = context.applicationContext
        appContext.stopService(Intent(appContext, DownloadForegroundService::class.java))
        WorkManager.getInstance(appContext).cancelUniqueWork(HEARTBEAT_WORK_NAME)
    }
}
