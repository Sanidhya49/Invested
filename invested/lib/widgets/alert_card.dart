import 'package:flutter/material.dart';

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

  Color _getSeverityColor() {
    switch (severity.toLowerCase()) {
      case 'critical':
        return Colors.red.shade100;
      case 'moderate':
        return Colors.orange.shade100;
      default:
        return Colors.green.shade100;
    }
  }

  IconData _getSeverityIcon() {
    switch (severity.toLowerCase()) {
      case 'critical':
        return Icons.warning_amber_rounded;
      case 'moderate':
        return Icons.error_outline;
      default:
        return Icons.check_circle_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 8),
      color: _getSeverityColor(),
      child: ListTile(
        leading: Icon(_getSeverityIcon(), size: 40),
        title: Text(type, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(description),
        isThreeLine: true,
      ),
    );
  }
}
