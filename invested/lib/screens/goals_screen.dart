import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:math';
import '../utils/app_theme.dart';
import '../widgets/add_goal_modal.dart';

class GoalsScreen extends StatefulWidget {
  const GoalsScreen({super.key});
  @override
  State<GoalsScreen> createState() => _GoalsScreenState();
}

class _GoalsScreenState extends State<GoalsScreen> {
  bool isLoading = false;
  bool isAnalyzing = false;
  List<dynamic> goals = [];
  Map<String, dynamic>? analysis;
  String error = '';
  int _retryCount = 0;
  static const int maxRetries = 2;

  @override
  void initState() {
    super.initState();
    fetchGoals();
  }

  Future<void> fetchGoals() async {
    if (isLoading) return;
    setState(() {
      isLoading = true;
      error = '';
    });

    final user = FirebaseAuth.instance.currentUser;
    final idToken = await user?.getIdToken();

    for (int attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        final response = await http
            .get(
              Uri.parse('http://10.0.2.2:8000/get-goals'),
              headers: {
                'Authorization': 'Bearer $idToken',
                'Content-Type': 'application/json',
              },
            )
            .timeout(Duration(seconds: 30 + (attempt * 10)));

        if (mounted) {
          if (response.statusCode == 200) {
            final data = json.decode(response.body);
            setState(() {
              goals = data['goals'] ?? [];
              _retryCount = 0;
            });
            break;
          } else {
            if (attempt == maxRetries) {
              setState(
                () => error = 'Error from server: ${response.statusCode}',
              );
            } else {
              continue;
            }
          }
        }
      } catch (e) {
        if (attempt == maxRetries) {
          if (mounted) {
            setState(() => error = 'Failed to fetch goals. Please try again.');
          }
        } else {
          await Future.delayed(Duration(seconds: (attempt + 1) * 2));
          continue;
        }
      }
    }

    if (mounted) setState(() => isLoading = false);
  }

  Future<void> analyzeGoals() async {
    if (isAnalyzing) return;
    setState(() {
      isAnalyzing = true;
      error = '';
    });

    final user = FirebaseAuth.instance.currentUser;
    final idToken = await user?.getIdToken();

    for (int attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        final response = await http
            .post(
              Uri.parse('http://10.0.2.2:8000/analyze-goals'),
              headers: {
                'Authorization': 'Bearer $idToken',
                'Content-Type': 'application/json',
              },
              body: '{}',
            )
            .timeout(Duration(seconds: 60 + (attempt * 10)));

        if (mounted) {
          if (response.statusCode == 200) {
            final data = json.decode(response.body);
            try {
              final parsed = json.decode(data['analysis']);
              setState(() {
                analysis = parsed;
                _retryCount = 0;
              });
              break;
            } catch (_) {
              if (attempt == maxRetries) {
                setState(() => error = 'Could not parse analysis from the AI.');
              } else {
                continue;
              }
            }
          } else {
            if (attempt == maxRetries) {
              setState(
                () => error = 'Error from server: ${response.statusCode}',
              );
            } else {
              continue;
            }
          }
        }
      } catch (e) {
        if (attempt == maxRetries) {
          if (mounted) {
            setState(
              () => error = 'Failed to analyze goals. Please try again.',
            );
          }
        } else {
          await Future.delayed(Duration(seconds: (attempt + 1) * 2));
          continue;
        }
      }
    }

    if (mounted) setState(() => isAnalyzing = false);
  }

  Future<void> deleteGoal(String goalId) async {
    final user = FirebaseAuth.instance.currentUser;
    final idToken = await user?.getIdToken();

    try {
      final response = await http
          .delete(
            Uri.parse('http://10.0.2.2:8000/delete-goal/$goalId'),
            headers: {
              'Authorization': 'Bearer $idToken',
              'Content-Type': 'application/json',
            },
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        await fetchGoals();
        if (analysis != null) {
          await analyzeGoals();
        }
      }
    } catch (e) {
      print('Error deleting goal: $e');
    }
  }

  void _showAddGoalModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => AddGoalModal(
        onGoalAdded: () {
          fetchGoals();
          if (analysis != null) {
            analyzeGoals();
          }
        },
      ),
    );
  }

  Widget _buildPieChart() {
    if (analysis == null || analysis!['pie_chart_data'] == null) {
      return Container(
        height: 200,
        decoration: AppTheme.cardDecorationElevated,
        child: const Center(
          child: Text('No chart data available', style: AppTheme.bodyMedium),
        ),
      );
    }

    final pieData = analysis!['pie_chart_data'] as List;
    if (pieData.isEmpty) {
      return Container(
        height: 200,
        decoration: AppTheme.cardDecorationElevated,
        child: const Center(
          child: Text(
            'Add goals to see chart analysis',
            style: AppTheme.bodyMedium,
          ),
        ),
      );
    }

    return Container(
      height: 300,
      decoration: AppTheme.cardDecorationElevated,
      child: Column(
        children: [
          const SizedBox(height: AppTheme.spacing16),
          Text('Goal Distribution', style: AppTheme.heading4),
          const SizedBox(height: AppTheme.spacing16),
          Expanded(
            child: CustomPaint(
              size: const Size(200, 200),
              painter: PieChartPainter(pieData),
            ),
          ),
          const SizedBox(height: AppTheme.spacing16),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(
                horizontal: AppTheme.spacing16,
              ),
              itemCount: pieData.length,
              itemBuilder: (context, index) {
                final item = pieData[index];
                return Padding(
                  padding: const EdgeInsets.only(bottom: AppTheme.spacing8),
                  child: Row(
                    children: [
                      Container(
                        width: 12,
                        height: 12,
                        decoration: BoxDecoration(
                          color: Color(
                            int.parse(item['color'].replaceAll('#', '0xFF')),
                          ),
                          borderRadius: BorderRadius.circular(6),
                        ),
                      ),
                      const SizedBox(width: AppTheme.spacing8),
                      Expanded(
                        child: Text(
                          '${item['category']} (${item['percentage'].toStringAsFixed(1)}%)',
                          style: AppTheme.bodyMedium,
                        ),
                      ),
                      Text(
                        '₹${item['amount'].toStringAsFixed(0)}',
                        style: AppTheme.bodyMedium.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisSection() {
    if (analysis == null) return const SizedBox.shrink();

    final analysisData = analysis!['analysis'];
    final insights = analysis!['goal_insights'] as List? ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          decoration: AppTheme.cardDecorationElevated,
          child: Padding(
            padding: const EdgeInsets.all(AppTheme.spacing20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Overall Progress', style: AppTheme.heading4),
                const SizedBox(height: AppTheme.spacing16),
                Row(
                  children: [
                    Expanded(
                      child: _buildProgressCard(
                        'Total Goals',
                        analysisData['total_goals'].toString(),
                        Icons.flag_rounded,
                        AppTheme.primaryBlue,
                      ),
                    ),
                    const SizedBox(width: AppTheme.spacing12),
                    Expanded(
                      child: _buildProgressCard(
                        'Progress',
                        '${analysisData['overall_progress'].toStringAsFixed(1)}%',
                        Icons.trending_up_rounded,
                        AppTheme.secondaryGreen,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppTheme.spacing16),
                Row(
                  children: [
                    Expanded(
                      child: _buildProgressCard(
                        'Target Amount',
                        '₹${analysisData['total_target_amount'].toStringAsFixed(0)}',
                        Icons.account_balance_wallet_rounded,
                        AppTheme.accentOrange,
                      ),
                    ),
                    const SizedBox(width: AppTheme.spacing12),
                    Expanded(
                      child: _buildProgressCard(
                        'Monthly Savings',
                        '₹${analysisData['monthly_savings_needed'].toStringAsFixed(0)}',
                        Icons.savings_rounded,
                        AppTheme.secondaryGreenDark,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: AppTheme.spacing16),
        if (insights.isNotEmpty) ...[
          Text('Goal Insights', style: AppTheme.heading4),
          const SizedBox(height: AppTheme.spacing12),
          ...insights.map((insight) => _buildInsightCard(insight)).toList(),
        ],
      ],
    );
  }

  Widget _buildProgressCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacing16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(AppTheme.radius12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: AppTheme.spacing8),
          Text(value, style: AppTheme.heading4.copyWith(color: color)),
          Text(
            title,
            style: AppTheme.captionText.copyWith(color: color),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildInsightCard(Map<String, dynamic> insight) {
    final status = insight['status'] ?? 'unknown';
    Color statusColor;
    IconData statusIcon;

    switch (status) {
      case 'on_track':
        statusColor = AppTheme.secondaryGreen;
        statusIcon = Icons.check_circle_rounded;
        break;
      case 'behind':
        statusColor = AppTheme.errorRed;
        statusIcon = Icons.warning_rounded;
        break;
      case 'ahead':
        statusColor = AppTheme.accentOrange;
        statusIcon = Icons.trending_up_rounded;
        break;
      default:
        statusColor = AppTheme.neutralGray600;
        statusIcon = Icons.info_rounded;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: AppTheme.spacing12),
      decoration: AppTheme.cardDecorationElevated,
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacing16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(statusIcon, color: statusColor, size: 20),
                const SizedBox(width: AppTheme.spacing8),
                Expanded(
                  child: Text(
                    insight['title'] ?? 'Unknown Goal',
                    style: AppTheme.heading5,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppTheme.spacing8,
                    vertical: AppTheme.spacing4,
                  ),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(AppTheme.radius12),
                  ),
                  child: Text(
                    '${insight['progress'].toStringAsFixed(1)}%',
                    style: AppTheme.captionText.copyWith(
                      color: statusColor,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacing8),
            Text(
              insight['insights'] ?? 'No insights available',
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.neutralGray700,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.neutralGray50,
      appBar: AppBar(
        title: const Text('Financial Goals'),
        backgroundColor: AppTheme.primaryBlue,
        foregroundColor: AppTheme.neutralWhite,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_rounded),
          onPressed: () => Navigator.of(context).pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.analytics_rounded),
            onPressed: goals.isNotEmpty ? analyzeGoals : null,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: fetchGoals,
        child: isLoading
            ? const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(
                        AppTheme.primaryBlue,
                      ),
                    ),
                    SizedBox(height: AppTheme.spacing16),
                    Text('Loading your goals...', style: AppTheme.bodyMedium),
                  ],
                ),
              )
            : error.isNotEmpty
            ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.error_outline_rounded,
                      size: 64,
                      color: AppTheme.errorRed,
                    ),
                    const SizedBox(height: AppTheme.spacing16),
                    Text(
                      error,
                      textAlign: TextAlign.center,
                      style: AppTheme.bodyMedium.copyWith(
                        color: AppTheme.errorRed,
                      ),
                    ),
                    const SizedBox(height: AppTheme.spacing16),
                    ElevatedButton(
                      onPressed: fetchGoals,
                      style: AppTheme.primaryButtonStyle,
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              )
            : goals.isEmpty
            ? const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.flag_rounded,
                      size: 64,
                      color: AppTheme.neutralGray400,
                    ),
                    SizedBox(height: AppTheme.spacing16),
                    Text(
                      'No goals set yet',
                      style: AppTheme.heading4,
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: AppTheme.spacing8),
                    Text(
                      'Add your first financial goal to get started',
                      style: AppTheme.bodyMedium,
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              )
            : SingleChildScrollView(
                padding: const EdgeInsets.all(AppTheme.spacing16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (isAnalyzing)
                      Container(
                        padding: const EdgeInsets.all(AppTheme.spacing16),
                        decoration: AppTheme.cardDecorationElevated,
                        child: Row(
                          children: [
                            const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  AppTheme.primaryBlue,
                                ),
                              ),
                            ),
                            const SizedBox(width: AppTheme.spacing12),
                            Text(
                              'Analyzing your goals...',
                              style: AppTheme.bodyMedium,
                            ),
                          ],
                        ),
                      ),
                    if (analysis != null) ...[
                      _buildPieChart(),
                      const SizedBox(height: AppTheme.spacing16),
                      _buildAnalysisSection(),
                      const SizedBox(height: AppTheme.spacing16),
                    ],
                    Text('Your Goals', style: AppTheme.heading4),
                    const SizedBox(height: AppTheme.spacing12),
                    ...goals.map((goal) => _buildGoalCard(goal)).toList(),
                  ],
                ),
              ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddGoalModal,
        backgroundColor: AppTheme.primaryBlue,
        foregroundColor: AppTheme.neutralWhite,
        child: const Icon(Icons.add_rounded),
      ),
    );
  }

  Widget _buildGoalCard(Map<String, dynamic> goal) {
    final progress = goal['target_amount'] > 0
        ? (goal['current_amount'] / goal['target_amount']) * 100
        : 0.0;
    final daysLeft = _calculateDaysLeft(goal['target_date']);

    return Container(
      margin: const EdgeInsets.only(bottom: AppTheme.spacing12),
      decoration: AppTheme.cardDecorationElevated,
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacing16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    goal['title'] ?? 'Untitled Goal',
                    style: AppTheme.heading5,
                  ),
                ),
                PopupMenuButton<String>(
                  onSelected: (value) {
                    if (value == 'delete') {
                      _showDeleteConfirmation(goal['id']);
                    }
                  },
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'delete',
                      child: Row(
                        children: [
                          Icon(Icons.delete_rounded, color: AppTheme.errorRed),
                          SizedBox(width: AppTheme.spacing8),
                          Text('Delete Goal'),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacing8),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '₹${goal['current_amount'].toStringAsFixed(0)} / ₹${goal['target_amount'].toStringAsFixed(0)}',
                        style: AppTheme.bodyLarge.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: AppTheme.spacing4),
                      LinearProgressIndicator(
                        value: progress / 100,
                        backgroundColor: AppTheme.neutralGray200,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          AppTheme.primaryBlue,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: AppTheme.spacing16),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '${progress.toStringAsFixed(1)}%',
                      style: AppTheme.heading5.copyWith(
                        color: AppTheme.primaryBlue,
                      ),
                    ),
                    Text(
                      daysLeft > 0 ? '$daysLeft days left' : 'Overdue',
                      style: AppTheme.captionText.copyWith(
                        color: daysLeft > 0
                            ? AppTheme.neutralGray600
                            : AppTheme.errorRed,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacing8),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppTheme.spacing8,
                    vertical: AppTheme.spacing4,
                  ),
                  decoration: BoxDecoration(
                    color: _getCategoryColor(goal['category']).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(AppTheme.radius12),
                  ),
                  child: Text(
                    goal['category'] ?? 'General',
                    style: AppTheme.captionText.copyWith(
                      color: _getCategoryColor(goal['category']),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const SizedBox(width: AppTheme.spacing8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppTheme.spacing8,
                    vertical: AppTheme.spacing4,
                  ),
                  decoration: BoxDecoration(
                    color: _getPriorityColor(goal['priority']).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(AppTheme.radius12),
                  ),
                  child: Text(
                    goal['priority'] ?? 'Medium',
                    style: AppTheme.captionText.copyWith(
                      color: _getPriorityColor(goal['priority']),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Color _getCategoryColor(String? category) {
    switch (category?.toLowerCase()) {
      case 'car':
        return AppTheme.primaryBlue;
      case 'house':
        return AppTheme.secondaryGreen;
      case 'vacation':
        return AppTheme.accentOrange;
      case 'education':
        return AppTheme.secondaryGreenDark;
      case 'retirement':
        return AppTheme.neutralGray600;
      default:
        return AppTheme.neutralGray600;
    }
  }

  Color _getPriorityColor(String? priority) {
    switch (priority?.toLowerCase()) {
      case 'high':
        return AppTheme.errorRed;
      case 'medium':
        return AppTheme.accentOrange;
      case 'low':
        return AppTheme.secondaryGreen;
      default:
        return AppTheme.neutralGray600;
    }
  }

  int _calculateDaysLeft(String? targetDate) {
    if (targetDate == null || targetDate.isEmpty) return 0;
    try {
      final target = DateTime.parse(targetDate);
      final now = DateTime.now();
      return target.difference(now).inDays;
    } catch (e) {
      return 0;
    }
  }

  void _showDeleteConfirmation(String goalId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Goal'),
        content: const Text('Are you sure you want to delete this goal?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              deleteGoal(goalId);
            },
            style: TextButton.styleFrom(foregroundColor: AppTheme.errorRed),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}

class PieChartPainter extends CustomPainter {
  final List<dynamic> data;

  PieChartPainter(this.data);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 10;
    final rect = Rect.fromCircle(center: center, radius: radius);

    double startAngle = 0;
    for (final item in data) {
      final sweepAngle = (item['percentage'] / 100) * 2 * pi;
      final paint = Paint()
        ..color = Color(int.parse(item['color'].replaceAll('#', '0xFF')))
        ..style = PaintingStyle.fill;

      canvas.drawArc(rect, startAngle, sweepAngle, true, paint);
      startAngle += sweepAngle;
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
