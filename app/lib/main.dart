import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const CatLogApp());
}

class CatLogApp extends StatelessWidget {
  const CatLogApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CatLog',
      theme: ThemeData(
        colorScheme:
            ColorScheme.fromSeed(seedColor: Colors.orange), // テーマ色をオレンジに
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static const String apiBaseUrl =
      String.fromEnvironment('CATLOG_API_BASE', defaultValue: 'http://127.0.0.1:8000');

  late Future<CatStatusData> _statusFuture;

  @override
  void initState() {
    super.initState();
    _statusFuture = _fetchStatus();
  }

  Future<CatStatusData> _fetchStatus() async {
    final uri = Uri.parse('$apiBaseUrl/current_status');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception('ステータス取得に失敗しました (${response.statusCode})');
    }

    final Map<String, dynamic> jsonBody = json.decode(response.body);
    return CatStatusData.fromJson(jsonBody);
  }

  Future<void> _refresh() async {
    setState(() {
      _statusFuture = _fetchStatus();
    });
    await _statusFuture;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('CatLog 🐱'),
        backgroundColor: Colors.orange[100],
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refresh,
            tooltip: '最新の状態を再取得',
          ),
        ],
      ),
      body: FutureBuilder<CatStatusData>(
        future: _statusFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return _ErrorView(
              message: snapshot.error?.toString() ?? '不明なエラーが発生しました',
              onRetry: _refresh,
            );
          }

          final data = snapshot.data ?? CatStatusData.empty();
          return RefreshIndicator(
            onRefresh: _refresh,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // 1. ステータスカード
                  _buildStatusCard(data),
                  const SizedBox(height: 20),

                  // 2. 見出し
                  const Text(
                    '最新の様子',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 10),

                  // 3. 動画リスト（ダミー）
                  Expanded(
                    child: ListView(
                      children: const [
                        VideoTile(
                            time: '12:30',
                            title: 'ごはんを食べました',
                            icon: Icons.rice_bowl),
                        VideoTile(
                            time: '10:15',
                            title: 'お昼寝中...',
                            icon: Icons.bedtime),
                        VideoTile(
                            time: '08:00',
                            title: 'トイレに行きました',
                            icon: Icons.cleaning_services),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  // ステータスカードを作るパーツ
  Widget _buildStatusCard(CatStatusData data) {
    final statusText = data.status ?? '不明';
    final lastUpdated =
        data.lastUpdated != null ? _formatDate(data.lastUpdated!) : '取得中...';
    final isSafe = statusText.contains('在宅') || statusText.contains('睡眠');
    final color = isSafe ? Colors.green : Colors.red;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1), // 安全なら緑、脱走なら赤にする
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(Icons.home, size: 60, color: color),
          const SizedBox(height: 10),
          Text(
            '現在: $statusText',
            style: TextStyle(
                fontSize: 24, fontWeight: FontWeight.bold, color: color),
          ),
          const SizedBox(height: 5),
          Text('最終確認: $lastUpdated'),
          if (data.batteryLevel != null) ...[
            const SizedBox(height: 8),
            Text('バッテリー残量: ${data.batteryLevel}%'),
          ],
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.year}/${_twoDigits(date.month)}/${_twoDigits(date.day)} '
        '${_twoDigits(date.hour)}:${_twoDigits(date.minute)}';
  }

  String _twoDigits(int v) => v.toString().padLeft(2, '0');
}

class _ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorView({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.red),
            const SizedBox(height: 12),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 12),
            ElevatedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('再試行'),
            ),
          ],
        ),
      ),
    );
  }
}

class CatStatusData {
  final String? status;
  final int? batteryLevel;
  final DateTime? lastUpdated;

  const CatStatusData({
    required this.status,
    required this.batteryLevel,
    required this.lastUpdated,
  });

  factory CatStatusData.fromJson(Map<String, dynamic> json) {
    return CatStatusData(
      status: json['status'] as String?,
      batteryLevel: json['battery_level'] as int?,
      lastUpdated: json['last_updated'] != null
          ? DateTime.tryParse(json['last_updated'].toString())
          : null,
    );
  }

  factory CatStatusData.empty() =>
      const CatStatusData(status: null, batteryLevel: null, lastUpdated: null);
}

// 動画リストの1行分を作るパーツ
class VideoTile extends StatelessWidget {
  final String time;
  final String title;
  final IconData icon;

  const VideoTile({
    super.key,
    required this.time,
    required this.title,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.orange[50],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: Colors.orange),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(time),
        trailing: const Icon(Icons.play_circle_fill, color: Colors.grey),
        onTap: () {
          // タップした時の処理（後で作る）
          print('動画を再生: $title');
        },
      ),
    );
  }
}