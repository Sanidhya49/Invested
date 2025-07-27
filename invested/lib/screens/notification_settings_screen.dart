import 'package:flutter/material.dart';
import 'package:invested/utils/app_theme.dart';
import 'package:invested/services/notification_service.dart';

class NotificationSettingsScreen extends StatefulWidget {
  const NotificationSettingsScreen({super.key});

  @override
  State<NotificationSettingsScreen> createState() =>
      _NotificationSettingsScreenState();
}

class _NotificationSettingsScreenState
    extends State<NotificationSettingsScreen> {
  final NotificationService _notificationService = NotificationService();

  bool _guardianAlerts = true;
  bool _catalystOpportunities = true;
  bool _strategistRecommendations = true;
  bool _oracleInsights = false;
  bool _goalUpdates = true;
  bool _securityAlerts = true;
  bool _financialUpdates = true;

  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadNotificationSettings();
  }

  Future<void> _loadNotificationSettings() async {
    try {
      // Load saved settings from local storage or Firestore
      // For now, we'll use default values
      setState(() {
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading notification settings: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _saveNotificationSettings() async {
    try {
      // Save settings to local storage or Firestore
      // For now, we'll just print the settings
      print('Notification settings saved:');
      print('Guardian Alerts: $_guardianAlerts');
      print('Catalyst Opportunities: $_catalystOpportunities');
      print('Strategist Recommendations: $_strategistRecommendations');
      print('Oracle Insights: $_oracleInsights');
      print('Goal Updates: $_goalUpdates');
      print('Security Alerts: $_securityAlerts');
      print('Financial Updates: $_financialUpdates');

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Notification settings saved successfully'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error saving settings: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Widget _buildNotificationTile({
    required String title,
    required String description,
    required String icon,
    required bool value,
    required ValueChanged<bool> onChanged,
    Color? iconColor,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppTheme.spacing12),
      decoration: AppTheme.cardDecorationElevated,
      child: SwitchListTile(
        title: Row(
          children: [
            Text(icon, style: const TextStyle(fontSize: 20)),
            const SizedBox(width: AppTheme.spacing12),
            Expanded(
              child: Text(
                title,
                style: AppTheme.heading6.copyWith(
                  color: AppTheme.neutralGray900,
                ),
              ),
            ),
          ],
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(left: 32),
          child: Text(
            description,
            style: AppTheme.bodyText.copyWith(color: AppTheme.neutralGray600),
          ),
        ),
        value: value,
        onChanged: onChanged,
        activeColor: AppTheme.primaryBlue,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppTheme.spacing16,
          vertical: AppTheme.spacing8,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.neutralGray50,
      appBar: AppBar(
        title: const Text(
          'Notification Settings',
          style: TextStyle(
            color: AppTheme.neutralGray900,
            fontWeight: FontWeight.w600,
          ),
        ),
        backgroundColor: AppTheme.neutralWhite,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(
            Icons.arrow_back_ios,
            color: AppTheme.neutralGray900,
          ),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          TextButton(
            onPressed: _saveNotificationSettings,
            child: const Text(
              'Save',
              style: TextStyle(
                color: AppTheme.primaryBlue,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(AppTheme.spacing16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  Container(
                    padding: const EdgeInsets.all(AppTheme.spacing16),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryBlue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(AppTheme.radius12),
                      border: Border.all(
                        color: AppTheme.primaryBlue.withOpacity(0.2),
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.notifications_active,
                          color: AppTheme.primaryBlue,
                          size: 24,
                        ),
                        const SizedBox(width: AppTheme.spacing12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Stay Informed',
                                style: AppTheme.heading6.copyWith(
                                  color: AppTheme.primaryBlue,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(height: AppTheme.spacing4),
                              Text(
                                'Choose which notifications you want to receive',
                                style: AppTheme.captionText.copyWith(
                                  color: AppTheme.primaryBlue.withOpacity(0.8),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: AppTheme.spacing24),

                  // High Priority Notifications
                  Text(
                    'High Priority',
                    style: AppTheme.heading5.copyWith(
                      color: AppTheme.neutralGray900,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: AppTheme.spacing12),

                  _buildNotificationTile(
                    title: 'Security Alerts',
                    description:
                        'Critical security and fraud alerts from Guardian',
                    icon: '🚨',
                    value: _securityAlerts,
                    onChanged: (value) =>
                        setState(() => _securityAlerts = value),
                  ),

                  _buildNotificationTile(
                    title: 'Guardian Alerts',
                    description: 'Financial monitoring and security alerts',
                    icon: '🛡️',
                    value: _guardianAlerts,
                    onChanged: (value) =>
                        setState(() => _guardianAlerts = value),
                  ),

                  const SizedBox(height: AppTheme.spacing24),

                  // Investment Notifications
                  Text(
                    'Investment & Growth',
                    style: AppTheme.heading5.copyWith(
                      color: AppTheme.neutralGray900,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: AppTheme.spacing12),

                  _buildNotificationTile(
                    title: 'Catalyst Opportunities',
                    description: 'New growth and investment opportunities',
                    icon: '🚀',
                    value: _catalystOpportunities,
                    onChanged: (value) =>
                        setState(() => _catalystOpportunities = value),
                  ),

                  _buildNotificationTile(
                    title: 'Strategist Recommendations',
                    description:
                        'Investment strategy and portfolio recommendations',
                    icon: '📈',
                    value: _strategistRecommendations,
                    onChanged: (value) =>
                        setState(() => _strategistRecommendations = value),
                  ),

                  const SizedBox(height: AppTheme.spacing24),

                  // Goals & Updates
                  Text(
                    'Goals & Updates',
                    style: AppTheme.heading5.copyWith(
                      color: AppTheme.neutralGray900,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: AppTheme.spacing12),

                  _buildNotificationTile(
                    title: 'Goal Updates',
                    description:
                        'Progress updates and achievements for your financial goals',
                    icon: '🎯',
                    value: _goalUpdates,
                    onChanged: (value) => setState(() => _goalUpdates = value),
                  ),

                  _buildNotificationTile(
                    title: 'Financial Updates',
                    description:
                        'Account balance changes and financial summaries',
                    icon: '💰',
                    value: _financialUpdates,
                    onChanged: (value) =>
                        setState(() => _financialUpdates = value),
                  ),

                  const SizedBox(height: AppTheme.spacing24),

                  // Insights
                  Text(
                    'Insights & Analysis',
                    style: AppTheme.heading5.copyWith(
                      color: AppTheme.neutralGray900,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: AppTheme.spacing12),

                  _buildNotificationTile(
                    title: 'Oracle Insights',
                    description: 'AI-powered financial insights and analysis',
                    icon: '🔮',
                    value: _oracleInsights,
                    onChanged: (value) =>
                        setState(() => _oracleInsights = value),
                  ),

                  const SizedBox(height: AppTheme.spacing32),

                  // Test Notifications Button
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(AppTheme.spacing16),
                    decoration: BoxDecoration(
                      color: AppTheme.neutralWhite,
                      borderRadius: BorderRadius.circular(AppTheme.radius12),
                      border: Border.all(color: AppTheme.neutralGray200),
                    ),
                    child: Column(
                      children: [
                        Text(
                          'Test Notifications',
                          style: AppTheme.heading6.copyWith(
                            color: AppTheme.neutralGray900,
                          ),
                        ),
                        const SizedBox(height: AppTheme.spacing8),
                        Text(
                          'Send a test notification to verify your settings',
                          style: AppTheme.captionText.copyWith(
                            color: AppTheme.neutralGray600,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: AppTheme.spacing16),
                        ElevatedButton(
                          onPressed: () async {
                            try {
                              await _notificationService.sendNotificationToUser(
                                userId: 'test_user',
                                title: '🧪 Test Notification',
                                body:
                                    'This is a test notification to verify your settings are working correctly.',
                                category: 'test',
                                data: {'test': true},
                              );
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('Test notification sent!'),
                                  backgroundColor: Colors.green,
                                ),
                              );
                            } catch (e) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(
                                    'Error sending test notification: $e',
                                  ),
                                  backgroundColor: Colors.red,
                                ),
                              );
                            }
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppTheme.primaryBlue,
                            foregroundColor: AppTheme.neutralWhite,
                            padding: const EdgeInsets.symmetric(
                              horizontal: AppTheme.spacing24,
                              vertical: AppTheme.spacing12,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(
                                AppTheme.radius8,
                              ),
                            ),
                          ),
                          child: const Text('Send Test Notification'),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: AppTheme.spacing24),
                ],
              ),
            ),
    );
  }
}
