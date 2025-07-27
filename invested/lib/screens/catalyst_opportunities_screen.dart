import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
// The old OpportunityCard import is no longer needed as we define a new one below.
// import '../widgets/opportunity_card.dart';

// Main Screen Widget
class CatalystOpportunitiesScreen extends StatefulWidget {
  const CatalystOpportunitiesScreen({super.key});
  @override
  State<CatalystOpportunitiesScreen> createState() =>
      _CatalystOpportunitiesScreenState();
}

class _CatalystOpportunitiesScreenState
    extends State<CatalystOpportunitiesScreen> {
  // --- NO CHANGES TO STATE VARIABLES OR BACKEND LOGIC ---
  bool isLoading = false;
  List<dynamic> opportunities = [];
  String error = '';

  // This function is UNCHANGED.
  Future<void> fetchOpportunities() async {
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
            Uri.parse('http://10.0.2.2:8000/run-catalyst'),
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
              data['opportunities']
                  .replaceAll("```json", '')
                  .replaceAll("```", ''),
            );
            setState(() => opportunities = parsed['opportunities'] ?? []);
          } catch (_) {
            setState(
              () => error = 'Could not parse opportunities from the AI.',
            );
          }
        } else {
          setState(() => error = 'Error from server: ${response.statusCode}');
        }
      }
    } catch (e) {
      if (mounted) setState(() => error = 'Failed to fetch opportunities: $e');
    } finally {
      if (mounted) setState(() => isLoading = false);
    }
  }

  // This function is UNCHANGED.
  @override
  void initState() {
    super.initState();
    fetchOpportunities();
  }

  // --- UI CODE: This 'build' method has been updated ---
  @override
  Widget build(BuildContext context) {
    // Defined color theme
    final Color primaryGreen = Colors.green.shade700;
    final Color backgroundColor = Colors.grey.shade100;

    Widget bodyContent;

    if (isLoading && opportunities.isEmpty) {
      // --- Improved Loading State ---
      bodyContent = Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(primaryGreen),
            ),
            const SizedBox(height: 20),
            const Text(
              'Finding opportunities for you...',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
          ],
        ),
      );
    } else if (error.isNotEmpty) {
      // --- Improved Error State ---
      bodyContent = Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.cloud_off, color: Colors.grey, size: 50),
              const SizedBox(height: 20),
              const Text(
                'Could Not Fetch Data',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                error,
                style: const TextStyle(color: Colors.redAccent),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    } else if (opportunities.isEmpty) {
      // --- Improved Empty State ---
      bodyContent = Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.thumb_up_alt_outlined, color: primaryGreen, size: 50),
              const SizedBox(height: 20),
              const Text(
                'All Good!',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              const Text(
                "No new opportunities found right now. You're on the right track!",
                style: TextStyle(color: Colors.grey),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    } else {
      // --- Improved List Display ---
      bodyContent = ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 80),
        children: [
          const Text(
            'Catalyst Opportunities',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Actionable suggestions to improve your finances.',
            style: TextStyle(fontSize: 16, color: Colors.grey),
          ),
          const SizedBox(height: 24),
          ...opportunities.map(
            (opp) => OpportunityCard(
              title: opp['title'] ?? 'Opportunity',
              description: opp['description'] ?? '',
              category: opp['category'] ?? 'General',
            ),
          ),
        ],
      );
    }

    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        backgroundColor: Colors.green.shade700,
        title: const Text(
          'Catalyst',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        elevation: 2,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: fetchOpportunities,
        color: primaryGreen,
        child: bodyContent,
      ),
    );
  }
}

// --- NEW Themed OpportunityCard Widget ---
// You can move this to its own file (e.g., widgets/opportunity_card.dart) if you prefer.
class OpportunityCard extends StatelessWidget {
  final String title;
  final String description;
  final String category;

  const OpportunityCard({
    super.key,
    required this.title,
    required this.description,
    required this.category,
  });

  // Helper function to get an icon based on the category
  IconData _getIconForCategory(String category) {
    switch (category.toLowerCase()) {
      case 'savings':
        return Icons.account_balance_wallet_outlined;
      case 'investment':
        return Icons.trending_up_rounded;
      case 'debt reduction':
        return Icons.credit_card_off_outlined;
      case 'budgeting':
        return Icons.pie_chart_outline_rounded;
      default:
        return Icons.lightbulb_outline_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final Color primaryGreen = Colors.green.shade700;
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(_getIconForCategory(category), color: primaryGreen),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    category,
                    style: TextStyle(
                      color: primaryGreen,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              description,
              style: TextStyle(
                fontSize: 15,
                color: Colors.grey.shade700,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
