import { toast } from 'react-toastify';
import { axiosInstance } from '../services/axiosInstance.js';
import { create } from 'zustand';

const useCameraStream = create((set)=>({
    // isConnected : false,
    // error : null,
    // videoRef: null,
    // canvasRef: null,
    streamUrl: null,

    startStream: async (cameraId)=>{
        try{
            const response = await axiosInstance.post(`/api/streams/${cameraId}/start`)
            if(response.data){
                set({streamUrl: response.data['ws_url']})
                toast.success("Stream start successfully!!")
                console.log('camera start :: ws_url ::: '+response.data['ws_url'])
            }else{
                toast.error("stream start response is empty!!")
            }
        }catch(error){
            console.log(error)
            toast.error("Start stream problem occur....")
        }
    },

    stopStream: async(cameraId)=>{
        try{
            const response = await axiosInstance.post(`api/streams/${cameraId}/stop`)
            if(response.data){
                toast.success("Camera stop succesfully!")
                console.log("camere stop response :::: "+response)
                set({streamUrl: null})
            }else{
                toast.error("steam stop response is emtpy!")
            }
        }catch(error){
            toast.error("Something went wrong when try to ")
        }
    }

}))
export {useCameraStream}