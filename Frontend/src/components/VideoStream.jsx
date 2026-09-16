// import React, { useEffect, useRef, useState } from 'react';
// import axios from 'axios';

// const BACKEND_URL = 'http://localhost:8000'; // Update with your backend address

// export default function LiveStream({ cameraId }) {
//     const videoRef = useRef(null);
//     const pcRef = useRef(null);
//     const [status, setStatus] = useState('Disconnected');

//     useEffect(() => {
//         // Cleanup previous connection if cameraId changes
//         return () => stopStream();
//     }, [cameraId]);

//     const startStream = async () => {
//         try {
//             setStatus('Connecting...');

//             // 1. Initialize PeerConnection with Google's public STUN server
//             const pc = new RTCPeerConnection({
//                 iceServers: [{ urls: 'stun:://google.com' }]
//             });
//             pcRef.current = pc;

//             // 2. Define track behavior (what to do when the backend sends the video stream)
//             pc.ontrack = (event) => {
//                 if (event.track.kind === 'video' && videoRef.current) {
//                     videoRef.current.srcObject = event.streams[0];
//                     setStatus('Streaming Live');
//                 }
//             };

//             // Handle connection states for debugging/UI feedback
//             pc.onconnectionstatechange = () => {
//                 setStatus(`Connection: ${pc.connectionState}`);
//             };

//             // 3. Inform WebRTC we only want to receive video (unidirectional)
//             pc.addTransceiver('video', { direction: 'recvonly' });

//             // 4. Generate local SDP Offer
//             const offer = await pc.createOffer();
//             await pc.setLocalDescription(offer);

//             // 5. Send Offer to FastAPI backend matching your Pydantic schema
//             const response = await axios.post(`${BACKEND_URL}/stream`, {
//                 sdp: pc.localDescription.sdp,
//                 type: pc.localDescription.type,
//                 camera_id: cameraId
//             }, {
//                 headers: {
//                     'Content-Type': 'application/json'
//                 }
//             });

//             // 6. Apply the backend's SDP Answer to establish the P2P connection
//             const answer = response.data;
//             await pc.setRemoteDescription(new RTCSessionDescription(answer));

//         } catch (error) {
//             console.error('WebRTC Handshake failed:', error);
//             setStatus('Connection Failed');
//             stopStream();
//         }
//     };

//     const stopStream = () => {
//         if (pcRef.current) {
//             pcRef.current.close();
//             pcRef.current = null;
//         }
//         if (videoRef.current) {
//             videoRef.current.srcObject = null;
//         }
//         setStatus('Disconnected');
//     };

//     return (
//         <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
//             <h3>Camera ID: {cameraId}</h3>
//             <p>Status: <strong>{status}</strong></p>

//             <div style={{ marginBottom: '15px' }}>
//                 <button onClick={startStream} style={buttonStyle}>Start Feed</button>
//                 <button onClick={stopStream} style={{ ...buttonStyle, backgroundColor: '#dc3545' }}>Stop Feed</button>
//             </div>

//             <video
//                 ref={videoRef}
//                 autoPlay
//                 playsInline
//                 controls
//                 style={{
//                     width: '100%',
//                     maxWidth: '720px',
//                     backgroundColor: '#000',
//                     borderRadius: '8px'
//                 }}
//             />
//         </div>
//     );
// }

