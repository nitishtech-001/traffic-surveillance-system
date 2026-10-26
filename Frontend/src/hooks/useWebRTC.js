import { useState } from 'react';
import { create } from 'zustand';

const useWebRTC = create((set, get) => {
    // Use private module-scoped variables for non-reactive references (replacing refs)
    let socket = null;
    let peerConnection = null;
    let pendingCandidates = [];

    return {
        connectionStatus: "Disconnected",
        streamObject: null,
        results: null,

        connectToLiveFeed: (wsUrl, cameraId) => {
            // 1. Clean up any existing connection first
            get().disconnectFeed();

            set({ connectionStatus: "Connecting..." });
            pendingCandidates = [];

            socket = new WebSocket(wsUrl);
        peerConnection = new RTCPeerConnection({
                // iceServers: [{ urls: "stun:://google.com" }]
                iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
            });

            // Handle incoming WebRTC video track
            peerConnection.ontrack = (event) => {
                if (event.streams && event.streams[0]) {
                    set({
                        streamObject: event.streams[0],
                        connectionStatus: "Live 🟢"
                    });
                }
            };

            // handling the incoming data
            peerConnection.ondatachannel = (event)=>{
                const channel = event.channel

                if (channel.label == "metadata_channel"){
                    channel.onmessage = (MessageEvent)=>{
                        try{
                            const dictionaryData = JSON.parse(MessageEvent.data)
                            set({results: dictionaryData})

                        }catch(err){
                            console.error("failed to parse metadata JSON", err)
                        }
                    }
                }
            }

            // Forward local network candidates to the backend
            peerConnection.onicecandidate = (event) => {
                if (event.candidate && socket?.readyState === WebSocket.OPEN) {
                    socket.send(JSON.stringify({
                        type: "candidate",
                        candidate: event.candidate,
                        cameraId: cameraId
                    }));
                }
            };

            socket.onopen = () => {
                socket.send(JSON.stringify({ type: "request_stream", cameraId }));
            };

            socket.onmessage = async (message) => {
                try {
                    const data = JSON.parse(message.data);

                    if (data.type === "offer") {
                        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.sdp));

                        const answer = await peerConnection.createAnswer();
                        await peerConnection.setLocalDescription(answer);

                        if (socket?.readyState === WebSocket.OPEN) {
                            socket.send(JSON.stringify({
                                type: "answer",
                                sdp: peerConnection.localDescription,
                                cameraId: cameraId
                            }));
                        }

                        // Flush out early-arriving ICE candidates
                        while (pendingCandidates.length > 0) {
                            const candidate = pendingCandidates.shift();
                            await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
                        }

                    } else if (data.type === "candidate" && data.candidate) {
                        // Guard: queue candidates if remote description isn't processed yet
                        if (peerConnection?.remoteDescription) {
                            await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
                        } else {
                            pendingCandidates.push(data.candidate);
                        }
                    }
                } catch (error) {
                    console.error("Error handling signaling message:", error);
                }
            };

            socket.onclose = () => set({ connectionStatus: "Disconnected 🔴", streamObject: null });
            socket.onerror = () => set({ connectionStatus: "Connection Error ⚠️" });
        },

        disconnectFeed: () => {
            if (peerConnection) {
                peerConnection.close();
                peerConnection = null;
            }
            if (socket) {
                socket.close();
                socket = null;
            }
            pendingCandidates = [];
            set({ connectionStatus: "Disconnected 🔴", streamObject: null });
            set({results: null})
        }
    };
});

export {useWebRTC}
