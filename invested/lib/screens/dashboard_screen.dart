import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'oracle_chat_screen.dart';
import 'guardian_alerts_screen.dart';
import 'catalyst_opportunities_screen.dart';
import 'strategist_screen.dart';
import 'profile_screen.dart';
import 'insights_screen.dart';
import 'subscriptions_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool isLoadingNetWorth = false;
  Map<String, dynamic>? netWorthData;
  String netWorthError = '';

  @override
  void initState() {
    super.initState();
    fetchNetWorth();
  }

  Future<void> fetchNetWorth() async {
    if (isLoadingNetWorth) return;

    setState(() {
      isLoadingNetWorth = true;
      netWorthError = '';
    });

    final user = FirebaseAuth.instance.currentUser;
    if (user == null) {
      setState(() {
        isLoadingNetWorth = false;
        netWorthError = 'User not authenticated';
      });
      return;
    }

    final idToken = await user.getIdToken();
    try {
      final response = await http
          .get(
            Uri.parse('http://10.0.2.2:8000/get-user-data'),
            headers: {
              'Authorization': 'Bearer $idToken',
              'Content-Type': 'application/json',
            },
          )
          .timeout(const Duration(seconds: 30));

      if (mounted) {
        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          setState(() {
            netWorthData = data;
            isLoadingNetWorth = false;
          });
        } else {
          setState(() {
            netWorthError = 'Failed to fetch net worth data';
            isLoadingNetWorth = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          netWorthError = 'Connection error: $e';
          isLoadingNetWorth = false;
        });
      }
    }
  }

  String formatCurrency(dynamic amount) {
    if (amount == null) return '₹0';
    final numValue = amount is String
        ? double.tryParse(amount) ?? 0
        : amount.toDouble();
    return '₹${numValue.toStringAsFixed(0)}';
  }

  String formatPercentage(dynamic current, dynamic previous) {
    if (current == null || previous == null || previous == 0) return '0%';
    final currentVal = current is String
        ? double.tryParse(current) ?? 0
        : current.toDouble();
    final previousVal = previous is String
        ? double.tryParse(previous) ?? 0
        : previous.toDouble();
    final change = ((currentVal - previousVal) / previousVal) * 100;
    return '${change >= 0 ? '+' : ''}${change.toStringAsFixed(1)}%';
  }

  @override
  Widget build(BuildContext context) {
    final user = FirebaseAuth.instance.currentUser;

    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        backgroundColor: Colors.green.shade700,
        title: const Text(
          'Dashboard',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 22,
          ),
        ),
        centerTitle: true,
        elevation: 2,
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.person_outline, color: Colors.white),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ProfileScreen()),
              );
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: fetchNetWorth,
        color: Colors.green,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Section
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
                      Row(
                        children: [
                          CircleAvatar(
                            radius: 25,
                            backgroundColor: Colors.green.shade100,
                            child: Text(
                              user?.displayName
                                      ?.substring(0, 1)
                                      .toUpperCase() ??
                                  'I',
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: Colors.green.shade700,
                              ),
                            ),
                          ),
                          const SizedBox(width: 15),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  "Welcome back, ${user?.displayName ?? 'Investor'} 👋",
                                  style: TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.green.shade800,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  "Your financial journey continues...",
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.green.shade600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 25),

              // Profile Quick Access
              Card(
                elevation: 3,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                color: Colors.white,
                child: InkWell(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const ProfileScreen(),
                      ),
                    );
                  },
                  borderRadius: BorderRadius.circular(16),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        CircleAvatar(
                          radius: 20,
                          backgroundColor: Colors.green.shade100,
                          child: Text(
                            user?.displayName?.substring(0, 1).toUpperCase() ??
                                'U',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.green.shade700,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Profile & Settings',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.green.shade700,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                'Manage your account and connect financial accounts',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Icon(
                          Icons.arrow_forward_ios,
                          color: Colors.green.shade600,
                          size: 16,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 25),

              // Net Worth Section
              const Text(
                "💰 Net Worth Overview",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 15),

              if (isLoadingNetWorth)
                Card(
                  elevation: 3,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Container(
                    height: 120,
                    padding: const EdgeInsets.all(20),
                    child: const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          CircularProgressIndicator(color: Colors.green),
                          SizedBox(height: 12),
                          Text('Fetching your net worth...'),
                        ],
                      ),
                    ),
                  ),
                )
              else if (netWorthError.isNotEmpty)
                Card(
                  elevation: 3,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  color: Colors.red.shade50,
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        Icon(
                          Icons.error_outline,
                          color: Colors.red.shade400,
                          size: 32,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Unable to fetch net worth',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Colors.red.shade700,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          netWorthError,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.red.shade600,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                )
              else if (netWorthData != null)
                Card(
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  color: Colors.white,
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'Total Net Worth',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: Colors.black87,
                              ),
                            ),
                            Icon(
                              Icons.account_balance_wallet,
                              color: Colors.green.shade600,
                              size: 24,
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          formatCurrency(netWorthData!['total_networth']),
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: Colors.green.shade700,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              netWorthData!['change_percentage'] != null &&
                                      double.tryParse(
                                            netWorthData!['change_percentage']
                                                .toString(),
                                          ) !=
                                          null &&
                                      double.parse(
                                            netWorthData!['change_percentage']
                                                .toString(),
                                          ) >=
                                          0
                                  ? Icons.trending_up
                                  : Icons.trending_down,
                              color:
                                  netWorthData!['change_percentage'] != null &&
                                      double.tryParse(
                                            netWorthData!['change_percentage']
                                                .toString(),
                                          ) !=
                                          null &&
                                      double.parse(
                                            netWorthData!['change_percentage']
                                                .toString(),
                                          ) >=
                                          0
                                  ? Colors.green
                                  : Colors.red,
                              size: 16,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              netWorthData!['change_percentage'] != null
                                  ? '${netWorthData!['change_percentage']}% this month'
                                  : 'No change data',
                              style: TextStyle(
                                fontSize: 14,
                                color:
                                    netWorthData!['change_percentage'] !=
                                            null &&
                                        double.tryParse(
                                              netWorthData!['change_percentage']
                                                  .toString(),
                                            ) !=
                                            null &&
                                        double.parse(
                                              netWorthData!['change_percentage']
                                                  .toString(),
                                            ) >=
                                            0
                                    ? Colors.green
                                    : Colors.red,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        const Divider(),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: _buildNetWorthItem(
                                'Assets',
                                formatCurrency(netWorthData!['total_assets']),
                                Colors.blue.shade600,
                                Icons.arrow_upward,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: _buildNetWorthItem(
                                'Liabilities',
                                formatCurrency(
                                  netWorthData!['total_liabilities'],
                                ),
                                Colors.red.shade600,
                                Icons.arrow_downward,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                )
              else
                Card(
                  elevation: 3,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  color: Colors.grey.shade50,
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        Icon(
                          Icons.account_balance_wallet_outlined,
                          color: Colors.grey.shade400,
                          size: 32,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'No net worth data available',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Colors.grey.shade600,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Connect your financial accounts to see your net worth',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade500,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
              const SizedBox(height: 25),

              // Quick Stats Section
              const Text(
                "📊 Quick Overview",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 15),
              Row(
                children: [
                  Expanded(
                    child: _buildStatCard(
                      "💹 Portfolio",
                      "Active",
                      Colors.blue.shade50,
                      Colors.blue.shade700,
                      Icons.trending_up,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildStatCard(
                      "💰 Savings",
                      "Growing",
                      Colors.green.shade50,
                      Colors.green.shade700,
                      Icons.account_balance_wallet,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildStatCard(
                      "🔔 Alerts",
                      "3 New",
                      Colors.orange.shade50,
                      Colors.orange.shade700,
                      Icons.notifications_active,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildStatCard(
                      "💡 Opportunities",
                      "2 Available",
                      Colors.purple.shade50,
                      Colors.purple.shade700,
                      Icons.lightbulb,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 30),

              // AI Agents Section
              const Text(
                "🤖 Your AI Financial Team",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 15),
              _buildAgentCard(
                context,
                "Oracle",
                "Your AI financial advisor",
                "Ask questions about your finances",
                Icons.chat_bubble_outline,
                Colors.green.shade600,
                () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const OracleChatScreen(),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              _buildAgentCard(
                context,
                "Guardian",
                "Proactive alerts & monitoring",
                "Stay informed about your financial health",
                Icons.shield_outlined,
                Colors.blue.shade600,
                () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const GuardianAlertsScreen(),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              _buildAgentCard(
                context,
                "Catalyst",
                "Opportunity finder",
                "Discover ways to improve your finances",
                Icons.rocket_launch_outlined,
                Colors.orange.shade600,
                () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const CatalystOpportunitiesScreen(),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              _buildAgentCard(
                context,
                "Strategist",
                "Investment analysis",
                "Get personalized investment recommendations",
                Icons.analytics_outlined,
                Colors.purple.shade600,
                () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const StrategistScreen(),
                  ),
                ),
              ),
              const SizedBox(height: 30),

              // Quick Actions
              const Text(
                "⚡ Quick Actions",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 15),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const GuardianAlertsScreen(),
                          ),
                        );
                      },
                      icon: const Icon(Icons.notifications_active),
                      label: const Text("View Alerts"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange.shade600,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const OracleChatScreen(),
                          ),
                        );
                      },
                      icon: const Icon(Icons.chat),
                      label: const Text("Ask Oracle"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green.shade600,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const InsightsScreen(),
                          ),
                        );
                      },
                      icon: const Icon(Icons.analytics),
                      label: const Text("Insights"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue.shade600,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const SubscriptionsScreen(),
                          ),
                        );
                      },
                      icon: const Icon(Icons.subscriptions),
                      label: const Text("Subscriptions"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.purple.shade600,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.white,
        selectedItemColor: Colors.green.shade700,
        unselectedItemColor: Colors.grey.shade600,
        currentIndex: 0, // Dashboard is selected
        onTap: (index) {
          switch (index) {
            case 0: // Dashboard - already here
              break;
            case 1: // Oracle
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const OracleChatScreen(),
                ),
              );
              break;
            case 2: // Guardian
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const GuardianAlertsScreen(),
                ),
              );
              break;
            case 3: // Catalyst
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const CatalystOpportunitiesScreen(),
                ),
              );
              break;
            case 4: // Insights
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const InsightsScreen(),
                ),
              );
              break;
            case 5: // Subscriptions
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const SubscriptionsScreen(),
                ),
              );
              break;
          }
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.chat_bubble_outline),
            label: 'Oracle',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.notifications_active_outlined),
            label: 'Alerts',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.trending_up),
            label: 'Opportunities',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics),
            label: 'Insights',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.subscriptions),
            label: 'Subscriptions',
          ),
        ],
      ),
    );
  }

  Widget _buildNetWorthItem(
    String label,
    String amount,
    Color color,
    IconData icon,
  ) {
    return Column(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          amount,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    Color bgColor,
    Color textColor,
    IconData icon,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      color: bgColor,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: textColor, size: 24),
            const SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(
                fontSize: 12,
                color: textColor,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: textColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAgentCard(
    BuildContext context,
    String title,
    String subtitle,
    String description,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: color, size: 28),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: color,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      description,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_ios, color: color, size: 16),
            ],
          ),
        ),
      ),
    );
  }
}
