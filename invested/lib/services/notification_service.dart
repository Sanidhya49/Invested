import 'package:flutter/material.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // Notification categories
  static const String categoryGuardian = 'guardian_alerts';
  static const String categoryCatalyst = 'catalyst_opportunities';
  static const String categoryStrategist = 'strategist_recommendations';
  static const String categoryOracle = 'oracle_insights';
  static const String categoryGoals = 'goal_updates';
  static const String categorySecurity = 'security_alerts';
  static const String categoryFinancial = 'financial_updates';

  Future<void> initialize() async {
    try {
      // Request permission for iOS
      NotificationSettings settings = await _firebaseMessaging
          .requestPermission(
            alert: true,
            badge: true,
            sound: true,
            provisional: false,
          );

      if (settings.authorizationStatus == AuthorizationStatus.authorized) {
        print('✅ Notification permissions granted');
      } else {
        print('❌ Notification permissions denied');
      }

      // Initialize local notifications
      await _initializeLocalNotifications();

      // Get FCM token
      String? token = await _firebaseMessaging.getToken();
      if (token != null) {
        print('📱 FCM Token: $token');
        await _saveTokenToFirestore(token);
      }

      // Listen for token refresh
      _firebaseMessaging.onTokenRefresh.listen((newToken) {
        _saveTokenToFirestore(newToken);
      });

      // Handle background messages
      FirebaseMessaging.onBackgroundMessage(
        _firebaseMessagingBackgroundHandler,
      );

      // Handle foreground messages
      FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

      // Handle notification taps
      FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);

      // Check for initial notification (app opened from terminated state)
      RemoteMessage? initialMessage = await _firebaseMessaging
          .getInitialMessage();
      if (initialMessage != null) {
        _handleNotificationTap(initialMessage);
      }
    } catch (e) {
      print('❌ Error initializing notifications: $e');
    }
  }

  Future<void> _initializeLocalNotifications() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const DarwinInitializationSettings initializationSettingsIOS =
        DarwinInitializationSettings(
          requestAlertPermission: true,
          requestBadgePermission: true,
          requestSoundPermission: true,
        );

    const InitializationSettings initializationSettings =
        InitializationSettings(
          android: initializationSettingsAndroid,
          iOS: initializationSettingsIOS,
        );

    await _localNotifications.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: _onLocalNotificationTap,
    );

    // Create notification channels for Android
    await _createNotificationChannels();
  }

  Future<void> _createNotificationChannels() async {
    const AndroidNotificationChannel guardianChannel =
        AndroidNotificationChannel(
          'guardian_alerts',
          'Guardian Alerts',
          description: 'Security and monitoring alerts from Guardian agent',
          importance: Importance.high,
          playSound: true,
          enableVibration: true,
        );

    const AndroidNotificationChannel catalystChannel =
        AndroidNotificationChannel(
          'catalyst_opportunities',
          'Catalyst Opportunities',
          description: 'Growth opportunities from Catalyst agent',
          importance: Importance.defaultImportance,
          playSound: true,
          enableVibration: true,
        );

    const AndroidNotificationChannel strategistChannel =
        AndroidNotificationChannel(
          'strategist_recommendations',
          'Strategist Recommendations',
          description: 'Investment recommendations from Strategist agent',
          importance: Importance.defaultImportance,
          playSound: true,
          enableVibration: true,
        );

    const AndroidNotificationChannel oracleChannel = AndroidNotificationChannel(
      'oracle_insights',
      'Oracle Insights',
      description: 'Financial insights from Oracle agent',
      importance: Importance.low,
      playSound: false,
      enableVibration: false,
    );

    const AndroidNotificationChannel goalsChannel = AndroidNotificationChannel(
      'goal_updates',
      'Goal Updates',
      description: 'Updates about your financial goals',
      importance: Importance.defaultImportance,
      playSound: true,
      enableVibration: true,
    );

    const AndroidNotificationChannel securityChannel =
        AndroidNotificationChannel(
          'security_alerts',
          'Security Alerts',
          description: 'Critical security alerts',
          importance: Importance.high,
          playSound: true,
          enableVibration: true,
        );

    await _localNotifications
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(guardianChannel);

    await _localNotifications
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(catalystChannel);

    await _localNotifications
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(strategistChannel);

    await _localNotifications
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(oracleChannel);

    await _localNotifications
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(goalsChannel);

    await _localNotifications
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(securityChannel);
  }

  Future<void> _saveTokenToFirestore(String token) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user != null) {
        await _firestore.collection('users').doc(user.uid).update({
          'fcm_token': token,
          'last_token_update': FieldValue.serverTimestamp(),
        });
      }
    } catch (e) {
      print('❌ Error saving FCM token: $e');
    }
  }

  void _handleForegroundMessage(RemoteMessage message) {
    print('📱 Foreground message received: ${message.data}');

    // Show local notification
    _showLocalNotification(
      id: message.hashCode,
      title: message.notification?.title ?? 'Invested',
      body: message.notification?.body ?? 'New notification',
      payload: json.encode(message.data),
      channelId: message.data['category'] ?? 'general',
    );
  }

  void _handleNotificationTap(RemoteMessage message) {
    print('📱 Notification tapped: ${message.data}');
    // Navigate to appropriate screen based on notification type
    _navigateToScreen(message.data);
  }

  void _onLocalNotificationTap(NotificationResponse response) {
    print('📱 Local notification tapped: ${response.payload}');
    if (response.payload != null) {
      final data = json.decode(response.payload!);
      _navigateToScreen(data);
    }
  }

  void _navigateToScreen(Map<String, dynamic> data) {
    // This will be implemented in the main app to handle navigation
    // For now, we'll just print the intended navigation
    final category = data['category'];
    final screen = data['screen'];

    print('🧭 Navigate to: $category -> $screen');

    // You can implement navigation logic here or use a callback
    // Example: Navigator.pushNamed(context, '/$screen');
  }

  Future<void> _showLocalNotification({
    required int id,
    required String title,
    required String body,
    String? payload,
    required String channelId,
  }) async {
    const AndroidNotificationDetails androidDetails =
        AndroidNotificationDetails(
          'default_channel',
          'Default Channel',
          channelDescription: 'Default notification channel',
          importance: Importance.high,
          priority: Priority.high,
          showWhen: true,
        );

    const DarwinNotificationDetails iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const NotificationDetails details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _localNotifications.show(id, title, body, details, payload: payload);
  }

  // Send notification to specific user
  Future<void> sendNotificationToUser({
    required String userId,
    required String title,
    required String body,
    required String category,
    Map<String, dynamic>? data,
  }) async {
    try {
      // Get user's FCM token
      final userDoc = await _firestore.collection('users').doc(userId).get();
      final fcmToken = userDoc.data()?['fcm_token'];

      if (fcmToken == null) {
        print('❌ No FCM token found for user: $userId');
        return;
      }

      // Send notification via your backend
      await _sendNotificationViaBackend(
        token: fcmToken,
        title: title,
        body: body,
        category: category,
        data: data,
      );
    } catch (e) {
      print('❌ Error sending notification: $e');
    }
  }

  Future<void> _sendNotificationViaBackend({
    required String token,
    required String title,
    required String body,
    required String category,
    Map<String, dynamic>? data,
  }) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      final idToken = await user?.getIdToken();

      final response = await http.post(
        Uri.parse('http://10.0.2.2:8000/send-notification'),
        headers: {
          'Authorization': 'Bearer $idToken',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'token': token,
          'title': title,
          'body': body,
          'category': category,
          'data': data ?? {},
        }),
      );

      if (response.statusCode == 200) {
        print('✅ Notification sent successfully');
      } else {
        print('❌ Failed to send notification: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error sending notification via backend: $e');
    }
  }

  // Notification templates for different events
  Future<void> sendGuardianAlert({
    required String userId,
    required String alertType,
    required String description,
    String severity = 'medium',
  }) async {
    final title = '🛡️ Guardian Alert: $alertType';
    final body = description.length > 100
        ? '${description.substring(0, 100)}...'
        : description;

    await sendNotificationToUser(
      userId: userId,
      title: title,
      body: body,
      category: categoryGuardian,
      data: {
        'screen': 'guardian_alerts',
        'alert_type': alertType,
        'severity': severity,
      },
    );
  }

  Future<void> sendCatalystOpportunity({
    required String userId,
    required String opportunityTitle,
    required String description,
  }) async {
    final title = '🚀 New Opportunity: $opportunityTitle';
    final body = description.length > 100
        ? '${description.substring(0, 100)}...'
        : description;

    await sendNotificationToUser(
      userId: userId,
      title: title,
      body: body,
      category: categoryCatalyst,
      data: {
        'screen': 'catalyst_opportunities',
        'opportunity_title': opportunityTitle,
      },
    );
  }

  Future<void> sendStrategistRecommendation({
    required String userId,
    required String symbol,
    required String recommendation,
  }) async {
    final title = '📈 Strategist: $symbol';
    final body = recommendation.length > 100
        ? '${recommendation.substring(0, 100)}...'
        : recommendation;

    await sendNotificationToUser(
      userId: userId,
      title: title,
      body: body,
      category: categoryStrategist,
      data: {'screen': 'strategist', 'symbol': symbol},
    );
  }

  Future<void> sendOracleInsight({
    required String userId,
    required String insight,
  }) async {
    final title = '🔮 Oracle Insight';
    final body = insight.length > 100
        ? '${insight.substring(0, 100)}...'
        : insight;

    await sendNotificationToUser(
      userId: userId,
      title: title,
      body: body,
      category: categoryOracle,
      data: {'screen': 'oracle_chat'},
    );
  }

  Future<void> sendGoalUpdate({
    required String userId,
    required String goalTitle,
    required String update,
  }) async {
    final title = '🎯 Goal Update: $goalTitle';
    final body = update.length > 100
        ? '${update.substring(0, 100)}...'
        : update;

    await sendNotificationToUser(
      userId: userId,
      title: title,
      body: body,
      category: categoryGoals,
      data: {'screen': 'goals', 'goal_title': goalTitle},
    );
  }

  Future<void> sendSecurityAlert({
    required String userId,
    required String alertTitle,
    required String description,
  }) async {
    final title = '🚨 Security Alert: $alertTitle';
    final body = description.length > 100
        ? '${description.substring(0, 100)}...'
        : description;

    await sendNotificationToUser(
      userId: userId,
      title: title,
      body: body,
      category: categorySecurity,
      data: {'screen': 'guardian_alerts', 'alert_type': 'security'},
    );
  }

  Future<void> sendFinancialUpdate({
    required String userId,
    required String updateType,
    required String description,
  }) async {
    final title = '💰 Financial Update: $updateType';
    final body = description.length > 100
        ? '${description.substring(0, 100)}...'
        : description;

    await sendNotificationToUser(
      userId: userId,
      title: title,
      body: body,
      category: categoryFinancial,
      data: {'screen': 'dashboard', 'update_type': updateType},
    );
  }

  // Subscribe to topics for broadcast notifications
  Future<void> subscribeToTopic(String topic) async {
    await _firebaseMessaging.subscribeToTopic(topic);
    print('✅ Subscribed to topic: $topic');
  }

  Future<void> unsubscribeFromTopic(String topic) async {
    await _firebaseMessaging.unsubscribeFromTopic(topic);
    print('✅ Unsubscribed from topic: $topic');
  }

  // Get current notification settings
  Future<NotificationSettings> getNotificationSettings() async {
    return await _firebaseMessaging.getNotificationSettings();
  }

  // Check if notifications are enabled
  Future<bool> areNotificationsEnabled() async {
    final settings = await getNotificationSettings();
    return settings.authorizationStatus == AuthorizationStatus.authorized;
  }
}

// Background message handler
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  print('📱 Background message received: ${message.data}');
  // Handle background messages here
}
