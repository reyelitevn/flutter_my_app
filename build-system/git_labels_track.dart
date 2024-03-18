import 'output.dart';

const List<String> options = ["production", "staging", "develop"];
Future<void> main(List<String> labels) async {
  List<String> trackLabels = List.from(labels);
  trackLabels.removeWhere((e) => !options.contains(e));
  String track = "track=production";
  if (trackLabels.isNotEmpty) {
    track = "track=${trackLabels.first}";
  }
  await setOutput(track);
}
