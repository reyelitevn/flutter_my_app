import 'package:flutter_dotenv/flutter_dotenv.dart';

final class EnvConfigs {
  static Future<void> load(String environment) async {
    return dotenv.load(fileName: "assets/env/.env.$environment");
  }

  static final String currentEnvironment = dotenv.get("ENVIRONMENT");
}
