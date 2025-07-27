import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
// I'm assuming 'alert_card.dart' is no longer needed since we are defining it here.
// If you still need it, you can keep the import.
// import '../widgets/alert_card.dart';

// Main Screen Widget
class GuardianAlertsScreen extends StatefulWidget {
  const GuardianAlertsScreen({super.key});
  @override
  State<GuardianAlertsScreen> createState() => _GuardianAlertsScreenState();
}

class _GuardianAlertsScreenState extends State<GuardianAlertsScreen> {
  // --- NO CHANGES TO STATE VARIABLES OR BACKEND LOGIC ---
  bool isLoading = false;
  List<dynamic> alerts = [];
  String error = '';
  bool _hasFetchedOnce = false;

  // This function is UNCHANGED.
  Future<void> fetchAlerts() async {
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
            Uri.parse('http://10.0.2.2:8000/run-guardian'),
            headers: {
              'Authorization': 'Bearer $idToken',
              'Content-Type': 'application/json',
            },
            body: '{}',
          )
          .timeout(const Duration(seconds: 30));
      if (mounted) {
        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          try {
            final parsed = json.decode(
              data['alerts'].replaceAll("```json", '').replaceAll("```", ''),
            );
            setState(() => alerts = parsed['alerts'] ?? []);
          } catch (_) {
            setState(() => error = 'Could not parse alerts from the AI.');
          }
        } else {
          setState(() => error = 'Error from server: ${response.statusCode}');
        }
      }
    } catch (e) {
      if (mounted) setState(() => error = 'Failed to fetch alerts: $e');
    } finally {
      if (mounted) setState(() => isLoading = false);
    }
  }

  // This function is UNCHANGED.
  @override
  void initState() {
    super.initState();
    // This logic ensures data is fetched only on the first load.
    if (!_hasFetchedOnce) {
      fetchAlerts();
      setState(() {
        _hasFetchedOnce = true;
      });
    }
  }

  // --- UI CODE: This 'build' method has been updated ---
  @override
  Widget build(BuildContext context) {
    // Defined color theme
    final Color primaryGreen = Colors.green.shade800;
    final Color lightGrey = Colors.grey.shade200;
    final Color darkText = Colors.grey.shade800;

    Widget content;

    if (isLoading && alerts.isEmpty) {
      // --- Improved Loading State ---
      content = Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(primaryGreen),
            ),
            const SizedBox(height: 16),
            const Text('Fetching your alerts...'),
          ],
        ),
      );
    } else if (error.isNotEmpty) {
      // --- Improved Error State ---
      content = Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, color: Colors.red.shade400, size: 48),
            const SizedBox(height: 16),
            Text(
              'An Error Occurred',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text(
              error,
              style: TextStyle(color: darkText),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    } else if (alerts.isEmpty) {
      // --- Improved Empty State ---
      content = Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.check_circle_outline, color: primaryGreen, size: 48),
            const SizedBox(height: 16),
            Text('All Clear!', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Text(
              "No financial alerts found.\nPull down to refresh.",
              style: TextStyle(color: darkText),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    } else {
      // --- Improved List Display ---
      content = ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            'Proactive Alerts',
            style: Theme.of(
              context,
            ).textTheme.titleLarge?.copyWith(color: darkText),
          ),
          const SizedBox(height: 8),
          Text(
            'Here are some observations about your financial health. Pull down to refresh.',
            style: TextStyle(color: Colors.grey.shade600),
          ),
          const SizedBox(height: 24),
          ...alerts.map(
            (alert) => AlertCard(
              type: alert['type'] ?? 'Alert',
              description: alert['description'] ?? 'No description provided.',
              severity: alert['severity'] ?? 'info',
            ),
          ),
        ],
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Guardian',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.white,
        foregroundColor: primaryGreen,
        elevation: 0.5,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: primaryGreen),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      backgroundColor: Colors.white,
      body: RefreshIndicator(
        onRefresh: fetchAlerts,
        color: primaryGreen,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8.0),
          child: content,
        ),
      ),
    );
  }
}

// --- NEW Themed AlertCard Widget ---
// You can move this to its own file (e.g., widgets/alert_card.dart) if you prefer.
class AlertCard extends StatelessWidget {
  final String type;
  final String description;
  final String severity;

  const AlertCard({
    super.key,
    required this.type,
    required this.description,
    required this.severity,
  });

  // Helper function to get an icon based on severity
  IconData _getIconForSeverity(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return Icons.warning_amber_rounded;
      case 'warning':
        return Icons.info_outline_rounded;
      case 'info':
      default:
        return Icons.check_circle_outline_rounded;
    }
  }

  // Helper function to get a color based on severity
  Color _getColorForSeverity(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return Colors.red.shade700;
      case 'warning':
        return Colors.amber.shade800;
      case 'info':
      default:
        return Colors.green.shade700;
    }
  }

  @override
  Widget build(BuildContext context) {
    final iconColor = _getColorForSeverity(severity);
    final iconData = _getIconForSeverity(severity);

    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.shade200, width: 1),
      ),
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(iconData, color: iconColor, size: 28),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    type,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.grey.shade900,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    description,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey.shade700,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
