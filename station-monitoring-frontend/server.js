// server.js
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8888 }); // 监听端口 8888

wss.on('connection', (ws) => {
    console.log('New client connected');
    
    // 监听客户端发送的消息
    ws.on('message', (message) => {
        console.log(`Received: ${message}`);
        // 给客户端发送消息
        ws.send('Hello, client!');
    });

    // 当客户端连接关闭时触发
    ws.on('close', () => {
        console.log('Client disconnected');
    });

    // 可以给客户端发送消息
    ws.send('Welcome to WebSocket server');
});

console.log('WebSocket server running on ws://localhost:8888');
