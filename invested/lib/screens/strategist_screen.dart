import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class StrategistScreen extends StatefulWidget {
  const StrategistScreen({super.key});
  @override
  State<StrategistScreen> createState() => _StrategistScreenState();
}

class _StrategistScreenState extends State<StrategistScreen> {
  bool isLoading = false;
  Map<String, dynamic>? strategy;
  String error = '';

  Future<void> fetchStrategy() async {
    if (isLoading) return;
    setState(() {
      isLoading = true;
      error = '';
    });
    final user = FirebaseAuth.instance.currentUser;
    final idToken = await user?.getIdToken();
    try {
      final response = await http
          .post(
            Uri.parse('http://10.0.2.2:8000/run-strategist'),
            headers: {
              'Authorization': 'Bearer $idToken',
              'Content-Type': 'application/json',
            },
            body: '{}',
          )
          .timeout(const Duration(seconds: 45));
      if (mounted) {
        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          try {
            final parsed = json.decode(
              data['strategy'].replaceAll("json", '').replaceAll("", ''),
            );
            setState(() => strategy = parsed);
          } catch (_) {
            setState(() => error = 'Could not parse strategy from the AI.');
          }
        } else {
          setState(() => error = 'Error from server: ${response.statusCode}');
        }
      }
    } catch (e) {
      if (mounted) setState(() => error = 'Failed to fetch strategy: $e');
    } finally {
      if (mounted) setState(() => isLoading = false);
    }
  }

  @override
  void initState() {
    super.initState();
    fetchStrategy();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.green.shade700,
        title: const Text("Strategist"),
        titleTextStyle: const TextStyle(
          fontSize: 22,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
        centerTitle: true,
        elevation: 2,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: RefreshIndicator(
        color: Colors.green,
        onRefresh: fetchStrategy,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              '💹 Investment Strategy',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                color: Colors.green.shade800,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Real-time analysis of your stock portfolio.',
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(color: Colors.grey.shade700),
            ),
            const SizedBox(height: 24),
            if (isLoading)
              const Center(
                child: CircularProgressIndicator(color: Colors.green),
              ),
            if (error.isNotEmpty)
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.red.shade300),
                ),
                child: Text(
                  error,
                  style: const TextStyle(color: Colors.red),
                  textAlign: TextAlign.center,
                ),
              ),
            if (strategy != null)
              Card(
                elevation: 4,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                color: Colors.green.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "📈 Strategist's Summary",
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Colors.green.shade800,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const Divider(thickness: 1.5, height: 20),
                      Text(
                        strategy!['summary'] ?? 'No summary available.',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          height: 1.6,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 24),
                      Text(
                        "✅ Recommendations",
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Colors.green.shade800,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const Divider(thickness: 1.5, height: 20),
                      ...(strategy!['recommendations'] as List<dynamic>?)?.map(
                            (rec) => Container(
                              margin: const EdgeInsets.symmetric(vertical: 6),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: Colors.green.shade200,
                                  width: 1,
                                ),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.green.withOpacity(0.1),
                                    blurRadius: 6,
                                    offset: const Offset(0, 3),
                                  ),
                                ],
                              ),
                              child: ListTile(
                                leading: Icon(
                                  rec['advice']?.toUpperCase() == 'HOLD'
                                      ? Icons.pause_circle_filled_rounded
                                      : Icons.trending_up_rounded,
                                  color: rec['advice']?.toUpperCase() == 'HOLD'
                                      ? Colors.orange.shade700
                                      : Colors.green.shade700,
                                  size: 32,
                                ),
                                title: Text(
                                  rec['symbol'] ?? '',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16,
                                  ),
                                ),
                                subtitle: Text(
                                  rec['reasoning'] ?? '',
                                  style: const TextStyle(fontSize: 14),
                                ),
                                isThreeLine: true,
                              ),
                            ),
                          ) ??
                          [const Text("No recommendations available.")],
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
