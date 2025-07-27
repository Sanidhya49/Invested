import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../utils/app_theme.dart';

class AddGoalModal extends StatefulWidget {
  final VoidCallback onGoalAdded;

  const AddGoalModal({super.key, required this.onGoalAdded});

  @override
  State<AddGoalModal> createState() => _AddGoalModalState();
}

class _AddGoalModalState extends State<AddGoalModal> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _targetAmountController = TextEditingController();
  final _currentAmountController = TextEditingController();
  DateTime? _selectedDate;
  String _selectedCategory = 'general';
  String _selectedPriority = 'medium';
  bool _isLoading = false;

  final List<Map<String, String>> categories = [
    {'value': 'car', 'label': 'Car Purchase'},
    {'value': 'house', 'label': 'House/Property'},
    {'value': 'vacation', 'label': 'Vacation/Travel'},
    {'value': 'education', 'label': 'Education'},
    {'value': 'retirement', 'label': 'Retirement'},
    {'value': 'emergency', 'label': 'Emergency Fund'},
    {'value': 'wedding', 'label': 'Wedding'},
    {'value': 'business', 'label': 'Business Investment'},
    {'value': 'general', 'label': 'General Savings'},
  ];

  final List<Map<String, String>> priorities = [
    {'value': 'high', 'label': 'High Priority'},
    {'value': 'medium', 'label': 'Medium Priority'},
    {'value': 'low', 'label': 'Low Priority'},
  ];

  Future<void> _selectDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 365)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 3650)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(primary: AppTheme.primaryBlue),
          ),
          child: child!,
        );
      },
    );
    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
      });
    }
  }

  Future<void> _addGoal() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedDate == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select a target date'),
          backgroundColor: AppTheme.errorRed,
        ),
      );
      return;
    }

    setState(() => _isLoading = true);

    final user = FirebaseAuth.instance.currentUser;
    final idToken = await user?.getIdToken();

    try {
      final response = await http
          .post(
            Uri.parse('http://10.0.2.2:8000/add-goal'),
            headers: {
              'Authorization': 'Bearer $idToken',
              'Content-Type': 'application/json',
            },
            body: json.encode({
              'title': _titleController.text.trim(),
              'target_amount': double.parse(_targetAmountController.text),
              'current_amount': double.parse(_currentAmountController.text),
              'target_date': _selectedDate!.toIso8601String().split('T')[0],
              'category': _selectedCategory,
              'priority': _selectedPriority,
            }),
          )
          .timeout(const Duration(seconds: 30));

      if (mounted) {
        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          if (data['success']) {
            Navigator.of(context).pop();
            widget.onGoalAdded();
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Goal added successfully!'),
                backgroundColor: AppTheme.secondaryGreen,
              ),
            );
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(data['message'] ?? 'Failed to add goal'),
                backgroundColor: AppTheme.errorRed,
              ),
            );
          }
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error: ${response.statusCode}'),
              backgroundColor: AppTheme.errorRed,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to add goal: $e'),
            backgroundColor: AppTheme.errorRed,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  void dispose() {
    _titleController.dispose();
    _targetAmountController.dispose();
    _currentAmountController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: AppTheme.neutralWhite,
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(AppTheme.radius20),
        ),
      ),
      child: Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom,
        ),
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(AppTheme.spacing20),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      const Text('Add New Goal', style: AppTheme.heading3),
                      const Spacer(),
                      IconButton(
                        onPressed: () => Navigator.of(context).pop(),
                        icon: const Icon(Icons.close_rounded),
                      ),
                    ],
                  ),
                  const SizedBox(height: AppTheme.spacing24),

                  // Goal Title
                  TextFormField(
                    controller: _titleController,
                    decoration: const InputDecoration(
                      labelText: 'Goal Title',
                      hintText: 'e.g., Buy a Car, Save for House',
                      prefixIcon: Icon(Icons.flag_rounded),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Please enter a goal title';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: AppTheme.spacing16),

                  // Target Amount
                  TextFormField(
                    controller: _targetAmountController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Target Amount (₹)',
                      hintText: '500000',
                      prefixIcon: Icon(Icons.account_balance_wallet_rounded),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Please enter target amount';
                      }
                      if (double.tryParse(value) == null) {
                        return 'Please enter a valid amount';
                      }
                      if (double.parse(value) <= 0) {
                        return 'Amount must be greater than 0';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: AppTheme.spacing16),

                  // Current Amount
                  TextFormField(
                    controller: _currentAmountController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Current Amount (₹)',
                      hintText: '50000',
                      prefixIcon: Icon(Icons.savings_rounded),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Please enter current amount';
                      }
                      if (double.tryParse(value) == null) {
                        return 'Please enter a valid amount';
                      }
                      if (double.parse(value) < 0) {
                        return 'Amount cannot be negative';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: AppTheme.spacing16),

                  // Target Date
                  InkWell(
                    onTap: _selectDate,
                    child: Container(
                      padding: const EdgeInsets.all(AppTheme.spacing16),
                      decoration: BoxDecoration(
                        border: Border.all(color: AppTheme.neutralGray300),
                        borderRadius: BorderRadius.circular(AppTheme.radius12),
                      ),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.calendar_today_rounded,
                            color: AppTheme.neutralGray600,
                          ),
                          const SizedBox(width: AppTheme.spacing12),
                          Expanded(
                            child: Text(
                              _selectedDate != null
                                  ? '${_selectedDate!.day}/${_selectedDate!.month}/${_selectedDate!.year}'
                                  : 'Select Target Date',
                              style: _selectedDate != null
                                  ? AppTheme.bodyMedium
                                  : AppTheme.bodyMedium.copyWith(
                                      color: AppTheme.neutralGray500,
                                    ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: AppTheme.spacing16),

                  // Category Dropdown
                  DropdownButtonFormField<String>(
                    value: _selectedCategory,
                    decoration: const InputDecoration(
                      labelText: 'Category',
                      prefixIcon: Icon(Icons.category_rounded),
                    ),
                    items: categories.map((category) {
                      return DropdownMenuItem(
                        value: category['value'],
                        child: Text(category['label']!),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedCategory = value!;
                      });
                    },
                  ),
                  const SizedBox(height: AppTheme.spacing16),

                  // Priority Dropdown
                  DropdownButtonFormField<String>(
                    value: _selectedPriority,
                    decoration: const InputDecoration(
                      labelText: 'Priority',
                      prefixIcon: Icon(Icons.priority_high_rounded),
                    ),
                    items: priorities.map((priority) {
                      return DropdownMenuItem(
                        value: priority['value'],
                        child: Text(priority['label']!),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedPriority = value!;
                      });
                    },
                  ),
                  const SizedBox(height: AppTheme.spacing24),

                  // Add Button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _addGoal,
                      style: AppTheme.primaryButtonStyle,
                      child: _isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  AppTheme.neutralWhite,
                                ),
                              ),
                            )
                          : const Text('Add Goal'),
                    ),
                  ),
                  const SizedBox(height: AppTheme.spacing16),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
