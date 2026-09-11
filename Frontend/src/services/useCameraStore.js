import { create } from "zustand";
import { axiosInstance as axios } from "./axiosInstance";
import { toast } from "react-toastify";

const useCameraStore = create((set)=>(
    {
        cameraList : null,
        currentCamera: null,

        getCameraList :async ()=>{
            try{
                const response = await axios.get("/api/cameras/list")
                console.log(response.data)                                
                set({cameraList:response.data});
                toast.success("camera list fetched..")
            }catch(err){
                console.log(err)
                toast.error("May be server is not running..")
            }
        },  
        addCamera : async (cameraInfo)=>{
            try{
                // TODO : add camera validationg function
                const response = await axios.post("/api/cameras/add",cameraInfo)
                if (response){
                    toast.success("Camera Added sucessfully!")
                }else{
                    toast.warning("camera does not added try again...")
                }
            }catch(err){
                console.log(err)
                toast.error("Something went wrong while adding camera..")
            }
        },
        setCurrentCamera: (camera)=>{
            try{
                set({currentCamera: camera})
                toast.success("current camera changed")
            }catch(err){
                toast.error(err)
            }
        }
    }
))
export {useCameraStore}





