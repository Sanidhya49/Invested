import 'package:flutter/material.dart';

class OpportunityCard extends StatelessWidget {
  final String title;
  final String description;
  final String? category;

  const OpportunityCard({
    super.key,
    required this.title,
    required this.description,
    this.category,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 8),
      color: Colors.blue.shade50,
      child: ListTile(
        leading: Icon(
          Icons.lightbulb_outline,
          color: Colors.blue.shade700,
          size: 40,
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(description),
        trailing: category != null
            ? Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.blue[200],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  category!.toUpperCase(),
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              )
            : null,
        isThreeLine: true,
      ),
    );
  }
}
