import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

export const fetchAgents = createAsyncThunk(
    'agents/fetchAgents',
    async () => {
        const response = await api.get('/api/agents/list');
        return response.data;
    }
);

export const activateAgent = createAsyncThunk(
    'agents/activateAgent',
    async (agentId) => {
        await api.post(`/api/agents/${agentId}/activate`);
        return agentId;
    }
);

export const deactivateAgent = createAsyncThunk(
    'agents/deactivateAgent',
    async (agentId) => {
        await api.post(`/api/agents/${agentId}/deactivate`);
        return agentId;
    }
);

const initialState = {
    agents: [],
    activeAgents: [],
    status: {},
    loading: false,
    error: null
};

const agentSlice = createSlice({
    name: 'agents',
    initialState,
    reducers: {
        toggleAgent: (state, action) => {
            const agentId = action.payload;
            if (state.activeAgents.includes(agentId)) {
                state.activeAgents = state.activeAgents.filter(id => id !== agentId);
            } else {
                state.activeAgents.push(agentId);
            }
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchAgents.pending, (state) => {
                state.loading = true;
            })
            .addCase(fetchAgents.fulfilled, (state, action) => {
                state.loading = false;
                state.agents = action.payload;
                state.activeAgents = action.payload
                    .filter(a => a.active)
                    .map(a => a.agent_id);
            })
            .addCase(fetchAgents.rejected, (state, action) => {
                state.loading = false;
                state.error = action.error.message;
            })
            .addCase(activateAgent.fulfilled, (state, action) => {
                if (!state.activeAgents.includes(action.payload)) {
                    state.activeAgents.push(action.payload);
                }
            })
            .addCase(deactivateAgent.fulfilled, (state, action) => {
                state.activeAgents = state.activeAgents.filter(id => id !== action.payload);
            });
    }
});

export const { toggleAgent } = agentSlice.actions;
export default agentSlice.reducer;