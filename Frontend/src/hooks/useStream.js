import { create } from 'zustand'
import { axiosInstance } from '../services/axiosInstance.js'
import { toast } from 'react-toastify'

const useStream = create((set) => ({
    currentStream: null,
    streamList: [],

    startStream: async (camera) => {
        try {
            // starting the current camera stream but make sure to stop the stream fo the previous stream
            const response = await axiosInstance.post(`/api/streams/${camera.id}/start`)
            console.log(response.data)
            set({ currentStream: response.data.ws_url })
            console.log("ws connection url is ::: ", response.data)
        } catch (err) {
            console.log(err)
            toast.error("Stream is failing....")
        }
    },

}))

export { useStream }
