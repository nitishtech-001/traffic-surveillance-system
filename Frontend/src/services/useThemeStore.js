import { toast } from "react-toastify";
import { create } from "zustand";

const useTheme = create((set)=>({
    theme: 'light',
    toggleTheme: ()=>{
        set((state)=> ({theme:state.theme==="light"?"dark":"light"}) )
        toast.success("theme changed..")
    }
}))

export {useTheme}