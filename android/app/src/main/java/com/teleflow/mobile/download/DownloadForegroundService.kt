package com.teleflow.mobile.download

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat

class DownloadForegroundService : Service() {
    override fun onCreate() {
        super.onCreate()
        ensureChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val active = intent?.getIntExtra(EXTRA_ACTIVE, 0) ?: 0
        val queued = intent?.getIntExtra(EXTRA_QUEUED, 0) ?: 0

        val notification = buildNotification(active = active, queued = queued)
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY
    }

    override fun onDestroy() {
        stopForeground(STOP_FOREGROUND_REMOVE)
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun buildNotification(active: Int, queued: Int): Notification {
        val content = "Active: $active  Queued: $queued"
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setContentTitle("Teleflow queue running")
            .setContentText(content)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .build()
    }

    private fun ensureChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return

        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val existing = manager.getNotificationChannel(CHANNEL_ID)
        if (existing != null) return

        val channel = NotificationChannel(
            CHANNEL_ID,
            "Teleflow Downloads",
            NotificationManager.IMPORTANCE_LOW
        )
        channel.description = "Foreground status for running queue"
        manager.createNotificationChannel(channel)
    }

    companion object {
        private const val CHANNEL_ID = "teleflow_downloads"
        private const val NOTIFICATION_ID = 4401

        const val EXTRA_ACTIVE = "extra_active"
        const val EXTRA_QUEUED = "extra_queued"
    }
}
