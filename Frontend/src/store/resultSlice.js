import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    results: [],
    latestResult: null,
    isProcessing: false,
    error: null
};

const resultSlice = createSlice({
    name: 'results',
    initialState,
    reducers: {
        addResult: (state, action) => {
            const result = {
                id: Date.now(),
                timestamp: new Date().toISOString(),
                ...action.payload
            };
            state.results = [result, ...state.results].slice(0, 100);
            state.latestResult = result;
        },
        setProcessing: (state, action) => {
            state.isProcessing = action.payload;
        },
        clearResults: (state) => {
            state.results = [];
            state.latestResult = null;
        },
        setError: (state, action) => {
            state.error = action.payload;
        },
        clearError: (state) => {
            state.error = null;
        }
    }
});

export const {
    addResult,
    setProcessing,
    clearResults,
    setError,
    clearError
} = resultSlice.actions;

export default resultSlice.reducer;