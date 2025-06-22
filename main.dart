import 'package:flutter/material.dart';
import 'package:web_socket_channel/io.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) =>
      MaterialApp(title: 'Deriv Bot', home: HomeScreen());
}

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  double balance = 0;
  List trades = [];
  late IOWebSocketChannel channel;

  @override
  void initState() {
    super.initState();
    fetchStatus();
    connectWebSocket();
  }

  void fetchStatus() async {
    final resp = await http.get(Uri.parse('http://YOUR_SERVER:8000/status'));
    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      setState(() {
        balance = data['balance'] / 10000;
        trades = data['last_trades'];
      });
    }
  }

  void connectWebSocket() {
    channel = IOWebSocketChannel.connect('ws://YOUR_SERVER:8000/ws');
    channel.stream.listen((msg) {
      final data = jsonDecode(msg);
      setState(() {
        if (data['balance'] != null) balance = data['balance'] / 10000;
        if (data['recent'] != null) trades = data['recent'];
      });
    });
  }

  @override
  void dispose() {
    channel.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext ctx) {
    return Scaffold(
      appBar: AppBar(title: Text('Deriv Bot Dashboard')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Text('Balance: \$${balance.toStringAsFixed(2)}', style: TextStyle(fontSize: 24)),
            SizedBox(height: 20),
            Text('Recent Trades:', style: TextStyle(fontSize: 18)),
            Expanded(
              child: ListView.builder(
                itemCount: trades.length,
                itemBuilder: (ctx, i) {
                  final t = trades[i];
                  return ListTile(
                    title: Text('${t['contract_type']} — \$${t['amount']}'),
                    subtitle: Text(DateTime.parse(t['time']).toLocal().toString()),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
