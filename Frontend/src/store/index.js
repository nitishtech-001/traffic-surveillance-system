import { configureStore } from '@reduxjs/toolkit';
import cameraReducer from './cameraSlice';
import agentReducer from './agentSlice';
import resultReducer from './resultSlice';

export const store = configureStore({
    reducer: {
        camera: cameraReducer,
        agents: agentReducer,
        results: resultReducer
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                // Ignore these action types
                ignoredActions: ['camera/setCamera'],
                ignoredActionPaths: ['payload.frame'],
                ignoredPaths: ['camera.currentCamera']
            }
        })
});

export const RootState = typeof store
export const AppDispatch = typeof store.dispatch;