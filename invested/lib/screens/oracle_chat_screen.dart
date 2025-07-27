import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class OracleChatScreen extends StatefulWidget {
  const OracleChatScreen({super.key});
  @override
  State<OracleChatScreen> createState() => _OracleChatScreenState();
}

class _OracleChatScreenState extends State<OracleChatScreen> {
  final TextEditingController _textController = TextEditingController();
  bool isOracleLoading = false;
  List<Map<String, String>> oracleChat = [];
  final ScrollController _scrollController = ScrollController();
  bool _showSuggestions = true;

  final List<String> suggestions = [
    "How can I save more money this month?",
    "What are the biggest expenses this week?",
    "How do I create a budget?",
    "Give me tips to reduce dining expenses.",
    "How much did I spend on travel last month?",
  ];

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> askOracle([String? prefilled]) async {
    final question = prefilled ?? _textController.text.trim();
    if (question.isEmpty) return;
    _textController.clear();
    FocusScope.of(context).unfocus();
    setState(() {
      isOracleLoading = true;
      _showSuggestions = false;
      oracleChat.add({'role': 'user', 'text': question});
    });
    _scrollToBottom();
    final user = FirebaseAuth.instance.currentUser;
    final idToken = await user?.getIdToken();
    try {
      final response = await http.post(
        Uri.parse('http://10.0.2.2:8000/ask-oracle'),
        headers: {
          'Authorization': 'Bearer $idToken',
          'Content-Type': 'application/json',
        },
        body: json.encode({'question': question}),
      );
      if (mounted) {
        final data = json.decode(response.body);
        setState(() {
          oracleChat.add({
            'role': 'oracle',
            'text': data['answer'] ?? 'Error: No answer received.',
          });
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          oracleChat.add({'role': 'oracle', 'text': 'Error: $e'});
        });
      }
    } finally {
      if (mounted) setState(() => isOracleLoading = false);
      _scrollToBottom();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        backgroundColor: Colors.green.shade700,
        title: const Text(
          'Oracle',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        elevation: 2,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          // Header section
          Container(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                const Text(
                  "Ask anything related to your finances 👇",
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.green,
                  ),
                ),
                if (_showSuggestions) ...[
                  const SizedBox(height: 12),
                  SizedBox(
                    height: 100,
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: suggestions
                          .map(
                            (q) => GestureDetector(
                              onTap: () => askOracle(q),
                              child: Container(
                                margin: const EdgeInsets.only(right: 10),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 14,
                                  vertical: 10,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.green.shade100,
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(
                                    color: Colors.green.shade400,
                                  ),
                                ),
                                child: Text(
                                  q,
                                  style: const TextStyle(fontSize: 14),
                                ),
                              ),
                            ),
                          )
                          .toList(),
                    ),
                  ),
                ],
              ],
            ),
          ),

          // Chat messages
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: oracleChat.length,
              itemBuilder: (context, index) {
                final msg = oracleChat[index];
                final isUser = msg['role'] == 'user';
                return Container(
                  margin: const EdgeInsets.symmetric(vertical: 6),
                  child: Row(
                    mainAxisAlignment: isUser
                        ? MainAxisAlignment.end
                        : MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      if (!isUser)
                        const CircleAvatar(
                          backgroundColor: Colors.green,
                          child: Icon(
                            Icons.smart_toy,
                            color: Colors.white,
                            size: 20,
                          ),
                        ),
                      if (!isUser) const SizedBox(width: 8),
                      Flexible(
                        child: Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: isUser
                                ? Colors.green.shade100
                                : Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.05),
                                blurRadius: 4,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: SelectableText(
                            msg['text'] ?? '',
                            style: const TextStyle(fontSize: 15),
                          ),
                        ),
                      ),
                      if (isUser) const SizedBox(width: 8),
                      if (isUser)
                        CircleAvatar(
                          backgroundColor: Colors.green.shade400,
                          child: const Icon(Icons.person, color: Colors.white),
                        ),
                    ],
                  ),
                );
              },
            ),
          ),

          // Input section
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    onChanged: (val) {
                      if (_showSuggestions && val.isNotEmpty) {
                        setState(() => _showSuggestions = false);
                      }
                    },
                    onSubmitted: (_) => askOracle(),
                    decoration: InputDecoration(
                      hintText: 'Type your question...',
                      fillColor: Colors.grey.shade50,
                      filled: true,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide.none,
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide(color: Colors.green.shade400),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                isOracleLoading
                    ? const Padding(
                        padding: EdgeInsets.all(8.0),
                        child: CircularProgressIndicator(),
                      )
                    : FloatingActionButton(
                        onPressed: askOracle,
                        backgroundColor: Colors.green,
                        mini: true,
                        child: const Icon(Icons.send, color: Colors.white),
                      ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
