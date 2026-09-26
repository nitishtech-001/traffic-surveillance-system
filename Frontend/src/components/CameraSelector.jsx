import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { useCamera } from '../hooks/useCamera';


const input_custom_style = `rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-700 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:focus:border-sky-500 dark:focus:ring-sky-500/20`

export default function CameraSelector() {
    const currentCamera = useCamera((state) => state.currentCamera)
    const cameraList = useCamera((state) => state.cameraList)
    const getCameraList = useCamera((state) => state.getCameraList)
    const addCamera = useCamera((state) => state.addCamera)
    const setCurrentCamera = useCamera((state) => state.setCurrentCamera)

    const [addCameraPopup, setAddCameraPopup] = useState(false);
    const [newCamera, setNewCamera] = useState({
        id: '',
        name: '',
        model: '',
        ip_address: '',
        port: 8080,
        username: '',
        password: '',
        protocol: "http",
    });

    useEffect(() => {
        getCameraList();
    }, [currentCamera]);

    const handleChange = (e) => {
        const id = e.target.id
        const value = e.target.value
        setNewCamera(prevValue => ({ ...prevValue, [id]: value }))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            if (!newCamera.id || !newCamera.name || !newCamera.ip_address || !newCamera.port) {
                toast.error("camera id, name, ip address and port number is required!!")
            }
            await addCamera(newCamera)
            setAddCameraPopup(false);
            getCameraList();
            setNewCamera({
                id: '',
                name: '',
                model: '',
                ip_address: '',
                port: 8080,
                username: '',
                password: '',
                protocol: ''
            });
        } catch (error) {
            console.error('Error adding camera:', error);
        }
    }

    const changeCurrentCamera = (cameraIdx) => {
        const camera = cameraList[cameraIdx]
        setCurrentCamera(camera)
    }

    return (
        <div className="flex items-center gap-2">
            <div className="relative min-w-45 sm:min-w-55">
                <select
                    // Find the index of the current camera to match the option value
                    value={cameraList ? cameraList.findIndex(cam => cam.id === currentCamera?.id) : ""}
                    onChange={(e) => changeCurrentCamera(e.target.value)}
                    className="w-full appearance-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 pr-10 text-sm font-medium text-slate-700 shadow-sm outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-100 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:focus:border-sky-500 dark:focus:ring-sky-500/20"
                >
                    <option value="">Select Camera</option>
                    {cameraList && cameraList.map((camera, index) => (
                        <option key={camera.id || index} value={index}>
                            {camera.id} - {camera.name} - {camera.ip_address}
                            {camera.status === 'streaming' ? ' 🟢' : ' 🔴'}
                        </option>
                    ))}
                </select>
                <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-slate-500 dark:text-slate-400">
                    ▾
                </span>
            </div>

            <button
                type="button"
                className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 text-base text-slate-700 transition hover:border-sky-300 hover:bg-sky-50 hover:text-sky-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:border-sky-500/60 dark:hover:bg-sky-500/10 dark:hover:text-sky-300"
                onClick={() => setAddCameraPopup(true)}
                title="Add Camera"
            >
                ➕
            </button>

            <button
                type="button"
                className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 text-base text-slate-700 transition hover:border-sky-300 hover:bg-sky-50 hover:text-sky-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:border-sky-500/60 dark:hover:bg-sky-500/10 dark:hover:text-sky-300"
                onClick={getCameraList}
                title="Refresh"
            >
                🔄
            </button>

            {addCameraPopup && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div className="w-full max-w-lg rounded-3xl border border-slate-200 bg-white p-5 shadow-2xl dark:border-slate-700 dark:bg-slate-900">
                        <div className="mb-4 flex items-center justify-between">
                            <h3 className="text-xl font-semibold text-slate-900 dark:text-white">Add New Camera</h3>
                            <button
                                type="button"
                                className="rounded-full border border-slate-200 px-2.5 py-1 text-sm text-slate-500 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                                onClick={() => setAddCameraPopup(false)}
                            >
                                ✕
                            </button>
                        </div>


                        <form className='grid gap-5' onSubmit={handleSubmit}>
                            <input
                                type="text"
                                placeholder="Camera ID"
                                id='id'
                                value={newCamera.id}
                                onChange={(e) => handleChange(e)}
                                className={input_custom_style}
                            />
                            <input
                                type="text"
                                placeholder="Camera Name"
                                id='name'
                                value={newCamera.name}
                                onChange={handleChange}
                                className={input_custom_style}
                            />

                            <select
                                id='model'
                                value={newCamera.model}
                                onChange={handleChange}
                                className={`col-span-2 ${input_custom_style}`}
                                required
                            >
                                <option value="" >Select Camera Model</option>
                                <option value="axispve">Axis Communications P3818-PVE</option>
                                <option value="hikvision">Hikvision Pro DS-2DE7A225IW-AEB</option>
                                <option value="dahua">Dahua WizMind S Series 4K</option>
                                <option value="ipwebcam">IP-WebCam</option>
                                <option value="local">Local Camera</option>
                            </select>

                            <input
                                type="text"
                                placeholder="IP Address"
                                id='ip_address'
                                value={newCamera.ip_address}
                                onChange={handleChange}
                                className={`sm:col-span-2 ${input_custom_style}`}
                            />
                            <input
                                type="number"
                                placeholder="Port"
                                id='port'
                                value={newCamera.port}
                                onChange={handleChange}
                                className={input_custom_style}
                            />
                            <input
                                type="text"
                                placeholder="Username"
                                id='username'
                                value={newCamera.username}
                                onChange={handleChange}
                                className={input_custom_style}
                            />
                            <input
                                type="password"
                                placeholder="Password"
                                id='password'
                                value={newCamera.password}
                                onChange={handleChange}
                                className={input_custom_style}
                            />
                            <select
                                id='protocol'
                                value={newCamera.protocol}
                                onChange={handleChange}
                                className={input_custom_style}
                            >
                                <option value="http">HTTP</option>
                                <option value="rtsp">RTSP</option>
                            </select>

                            <div className="mt-5 col-span-2 flex justify-end gap-3">
                                <button
                                    type="reset"
                                    onClick={() => setAddCameraPopup(false)}
                                    className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700 cursor-pointer"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="rounded-xl bg-linear-to-r from-sky-600 to-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-sky-500/20 transition hover:from-sky-500 hover:to-indigo-500 cursor-pointer"
                                >
                                    Add Camera
                                </button>
                            </div>
                        </form>

                    </div>
                </div>
            )}
        </div>
    );
}

