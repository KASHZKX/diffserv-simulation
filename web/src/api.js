import axios from 'axios';

// Dynamically determine the API base URL based on the current window location
// This allows access from localhost, local network IP (mobile), etc.
const API_URL = `http://${window.location.hostname}:8000`;

export const runSimulation = async (patterns) => {
    try {
        const response = await axios.post(`${API_URL}/run_simulation`, { patterns });
        return response.data;
    } catch (error) {
        console.error("Simulation failed:", error);
        throw error;
    }
};
