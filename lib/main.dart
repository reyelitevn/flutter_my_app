import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:my_app/app.dart';
import 'package:my_app/configs/env_configs.dart';

void main() async {
  await _loadEnvConfigs();
  Firebase.initializeApp();
  runApp(const MyApp());
}

Future<void> _loadEnvConfigs() async {
  const environment = String.fromEnvironment("FLAVOR", defaultValue: "develop");
  await EnvConfigs.load(environment.toLowerCase());
}
