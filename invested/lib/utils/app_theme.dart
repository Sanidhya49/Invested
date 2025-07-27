import 'package:flutter/material.dart';

class AppTheme {
  // Primary Colors
  static const Color primaryBlue = Color(0xFF2563EB);
  static const Color primaryBlueDark = Color(0xFF1D4ED8);
  static const Color primaryBlueLight = Color(0xFF3B82F6);

  // Secondary Colors
  static const Color secondaryGreen = Color(0xFF10B981);
  static const Color secondaryGreenDark = Color(0xFF059669);
  static const Color secondaryGreenLight = Color(0xFF34D399);

  // Accent Colors
  static const Color accentOrange = Color(0xFFF59E0B);
  static const Color accentOrangeDark = Color(0xFFD97706);
  static const Color accentOrangeLight = Color(0xFFFBBF24);

  // Neutral Colors
  static const Color neutralWhite = Color(0xFFFFFFFF);
  static const Color neutralGray50 = Color(0xFFF9FAFB);
  static const Color neutralGray100 = Color(0xFFF3F4F6);
  static const Color neutralGray200 = Color(0xFFE5E7EB);
  static const Color neutralGray300 = Color(0xFFD1D5DB);
  static const Color neutralGray400 = Color(0xFF9CA3AF);
  static const Color neutralGray500 = Color(0xFF6B7280);
  static const Color neutralGray600 = Color(0xFF4B5563);
  static const Color neutralGray700 = Color(0xFF374151);
  static const Color neutralGray800 = Color(0xFF1F2937);
  static const Color neutralGray900 = Color(0xFF111827);
  static const Color neutralBlack = Color(0xFF000000);

  // Status Colors
  static const Color successGreen = Color(0xFF10B981);
  static const Color warningYellow = Color(0xFFF59E0B);
  static const Color errorRed = Color(0xFFEF4444);
  static const Color infoBlue = Color(0xFF3B82F6);

  // Severity Colors
  static const Color severityHigh = Color(0xFFDC2626);
  static const Color severityMedium = Color(0xFFF59E0B);
  static const Color severityLow = Color(0xFF10B981);
  static const Color severityInfo = Color(0xFF3B82F6);

  // Gradient Colors
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primaryBlue, primaryBlueDark],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient successGradient = LinearGradient(
    colors: [secondaryGreen, secondaryGreenDark],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient warningGradient = LinearGradient(
    colors: [accentOrange, accentOrangeDark],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Typography
  static const String fontFamily = 'Inter';

  static const TextStyle heading1 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.bold,
    color: neutralGray900,
    height: 1.2,
  );

  static const TextStyle heading2 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: neutralGray900,
    height: 1.3,
  );

  static const TextStyle heading3 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 20,
    fontWeight: FontWeight.w600,
    color: neutralGray900,
    height: 1.4,
  );

  static const TextStyle heading4 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: neutralGray900,
    height: 1.4,
  );

  static const TextStyle heading5 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: neutralGray900,
    height: 1.4,
  );

  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.normal,
    color: neutralGray700,
    height: 1.5,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: neutralGray700,
    height: 1.5,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.normal,
    color: neutralGray600,
    height: 1.5,
  );

  static const TextStyle caption = TextStyle(
    fontFamily: fontFamily,
    fontSize: 11,
    fontWeight: FontWeight.normal,
    color: neutralGray500,
    height: 1.4,
  );

  static const TextStyle captionText = TextStyle(
    fontFamily: fontFamily,
    fontSize: 11,
    fontWeight: FontWeight.normal,
    color: neutralGray500,
    height: 1.4,
  );

  static const TextStyle heading6 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w600,
    color: neutralGray900,
    height: 1.4,
  );

  static const TextStyle bodyText = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: neutralGray700,
    height: 1.5,
  );

  static const TextStyle buttonText = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w600,
    color: neutralWhite,
    height: 1.2,
  );

  static const TextStyle labelText = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w500,
    color: neutralGray700,
    height: 1.2,
  );

  // Spacing
  static const double spacing4 = 4.0;
  static const double spacing6 = 6.0;
  static const double spacing8 = 8.0;
  static const double spacing12 = 12.0;
  static const double spacing16 = 16.0;
  static const double spacing20 = 20.0;
  static const double spacing24 = 24.0;
  static const double spacing32 = 32.0;
  static const double spacing40 = 40.0;
  static const double spacing48 = 48.0;

  // Border Radius
  static const double radius4 = 4.0;
  static const double radius8 = 8.0;
  static const double radius12 = 12.0;
  static const double radius16 = 16.0;
  static const double radius20 = 20.0;
  static const double radius24 = 24.0;
  static const double radius32 = 32.0;

  // Shadows
  static const List<BoxShadow> shadowSmall = [
    BoxShadow(color: Color(0x0A000000), blurRadius: 4, offset: Offset(0, 2)),
  ];

  static const List<BoxShadow> shadowMedium = [
    BoxShadow(color: Color(0x1A000000), blurRadius: 8, offset: Offset(0, 4)),
  ];

  static const List<BoxShadow> shadowLarge = [
    BoxShadow(color: Color(0x2A000000), blurRadius: 16, offset: Offset(0, 8)),
  ];

  // Card Styles
  static BoxDecoration cardDecoration = BoxDecoration(
    color: neutralWhite,
    borderRadius: BorderRadius.circular(radius16),
    boxShadow: shadowSmall,
    border: Border.all(color: neutralGray200, width: 1),
  );

  static BoxDecoration cardDecorationElevated = BoxDecoration(
    color: neutralWhite,
    borderRadius: BorderRadius.circular(radius16),
    boxShadow: shadowMedium,
    border: Border.all(color: neutralGray200, width: 1),
  );

  // Button Styles
  static ButtonStyle primaryButtonStyle = ElevatedButton.styleFrom(
    backgroundColor: primaryBlue,
    foregroundColor: neutralWhite,
    elevation: 0,
    padding: const EdgeInsets.symmetric(
      horizontal: spacing24,
      vertical: spacing12,
    ),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(radius12),
    ),
    textStyle: buttonText,
  );

  static ButtonStyle secondaryButtonStyle = ElevatedButton.styleFrom(
    backgroundColor: neutralGray100,
    foregroundColor: neutralGray700,
    elevation: 0,
    padding: const EdgeInsets.symmetric(
      horizontal: spacing24,
      vertical: spacing12,
    ),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(radius12),
    ),
    textStyle: buttonText.copyWith(color: neutralGray700),
  );

  static ButtonStyle outlineButtonStyle = OutlinedButton.styleFrom(
    foregroundColor: primaryBlue,
    side: const BorderSide(color: primaryBlue, width: 1.5),
    padding: const EdgeInsets.symmetric(
      horizontal: spacing24,
      vertical: spacing12,
    ),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(radius12),
    ),
    textStyle: buttonText.copyWith(color: primaryBlue),
  );

  // Input Styles
  static InputDecoration inputDecoration = InputDecoration(
    filled: true,
    fillColor: neutralGray50,
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(radius12),
      borderSide: const BorderSide(color: neutralGray200),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(radius12),
      borderSide: const BorderSide(color: neutralGray200),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(radius12),
      borderSide: const BorderSide(color: primaryBlue, width: 2),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(radius12),
      borderSide: const BorderSide(color: errorRed, width: 2),
    ),
    contentPadding: const EdgeInsets.symmetric(
      horizontal: spacing16,
      vertical: spacing12,
    ),
    hintStyle: bodyMedium.copyWith(color: neutralGray400),
  );

  // Severity Badge Styles
  static BoxDecoration severityHighDecoration = BoxDecoration(
    color: severityHigh,
    borderRadius: BorderRadius.circular(radius20),
  );

  static BoxDecoration severityMediumDecoration = BoxDecoration(
    color: severityMedium,
    borderRadius: BorderRadius.circular(radius20),
  );

  static BoxDecoration severityLowDecoration = BoxDecoration(
    color: severityLow,
    borderRadius: BorderRadius.circular(radius20),
  );

  static BoxDecoration severityInfoDecoration = BoxDecoration(
    color: severityInfo,
    borderRadius: BorderRadius.circular(radius20),
  );

  // App Bar Style
  static AppBarTheme appBarTheme = const AppBarTheme(
    backgroundColor: primaryBlue,
    foregroundColor: neutralWhite,
    elevation: 0,
    centerTitle: true,
    titleTextStyle: TextStyle(
      fontFamily: fontFamily,
      fontSize: 18,
      fontWeight: FontWeight.w600,
      color: neutralWhite,
    ),
    iconTheme: IconThemeData(color: neutralWhite),
  );

  // Bottom Navigation Bar Style
  static BottomNavigationBarThemeData bottomNavigationBarTheme =
      const BottomNavigationBarThemeData(
        backgroundColor: neutralWhite,
        selectedItemColor: primaryBlue,
        unselectedItemColor: neutralGray500,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
        selectedLabelStyle: TextStyle(
          fontFamily: fontFamily,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: TextStyle(
          fontFamily: fontFamily,
          fontSize: 12,
          fontWeight: FontWeight.normal,
        ),
      );

  // Theme Data
  static ThemeData get lightTheme {
    return ThemeData(
      fontFamily: fontFamily,
      primaryColor: primaryBlue,
      scaffoldBackgroundColor: neutralGray50,
      appBarTheme: appBarTheme,
      bottomNavigationBarTheme: bottomNavigationBarTheme,
      elevatedButtonTheme: ElevatedButtonThemeData(style: primaryButtonStyle),
      outlinedButtonTheme: OutlinedButtonThemeData(style: outlineButtonStyle),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: neutralGray50,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radius12),
          borderSide: const BorderSide(color: neutralGray200),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radius12),
          borderSide: const BorderSide(color: neutralGray200),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radius12),
          borderSide: const BorderSide(color: primaryBlue, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radius12),
          borderSide: const BorderSide(color: errorRed, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: spacing16,
          vertical: spacing12,
        ),
        hintStyle: bodyMedium.copyWith(color: neutralGray400),
      ),
      cardTheme: CardThemeData(
        color: neutralWhite,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radius16),
        ),
      ),
      colorScheme: const ColorScheme.light(
        primary: primaryBlue,
        secondary: secondaryGreen,
        surface: neutralWhite,
        background: neutralGray50,
        error: errorRed,
        onPrimary: neutralWhite,
        onSecondary: neutralWhite,
        onSurface: neutralGray900,
        onBackground: neutralGray900,
        onError: neutralWhite,
      ),
    );
  }
}
