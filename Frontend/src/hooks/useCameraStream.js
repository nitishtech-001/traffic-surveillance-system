import { toast } from 'react-toastify';
import { axiosInstance } from '../services/axiosInstance.js';
import { create } from 'zustand';

const useCameraStream = create((set) => ({
    processingInterval: 1000,
    confidenceThreshold: 50,
    realtimeAnalysis: false,
    saveResult: false,
    streamUrl: null,

    startStream: async (cameraId) => {
        try {
            const response = await axiosInstance.post(`/api/streams/${cameraId}/start`)
            if (response.data) {
                set({ streamUrl: response.data['ws_url'] })
                toast.success("Stream start successfully!!")
                console.log('camera start :: ws_url ::: ' + response.data['ws_url'])
            } else {
                toast.error("stream start response is empty!!")
            }
        } catch (error) {
            console.log(error)
            toast.error("Start stream problem occur....")
        }
    },

    stopStream: async (cameraId) => {
        try {
            const response = await axiosInstance.post(`/api/streams/${cameraId}/stop`)
            if (response.data) {
                toast.success("Camera stop succesfully!")
                console.log("camere stop response :::: " + response)
                set({ streamUrl: null })
            } else {
                toast.error("steam stop response is emtpy!")
            }
        } catch (error) {
            toast.error("Something went wrong when try to ")
        }
    },

    updateConfInterval: async (cameraId, conf, interval) => {
        try {
            const response = await axiosInstance.post(`/api/streams/${cameraId}/update/${conf}/${interval}`)
            if (response.data) {
                toast.success(response.data.message)
                set({ processingInterval: interval })
                set({ confidenceThreshold: conf })
            } else {
                toast.error("response data is Empty Something wrong..")
            }
        } catch (error) {
            toast.error("api error during conf and interval update")
            console.log(error)
        }
    },

    updateLocalprocess: (name, value) => {
        if (name === "realtimeAnalysis") {
            set({ realtimeAnalysis: value })
        } else if (name === "saveResults") {
            set({ saveResult: value })
        }
    }

}))
export { useCameraStream }