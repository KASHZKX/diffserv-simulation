import React, { useState, useEffect, useRef } from 'react';
import { runSimulation } from '../api';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const Dashboard = () => {
    const [patternsInput, setPatternsInput] = useState('E A B A E');
    const [isLoading, setIsLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [logs, setLogs] = useState([]);
    const logsEndRef = useRef(null);

    const scrollToBottom = () => {
        logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [logs]);

    const handleRun = async () => {
        setIsLoading(true);
        setLogs([]);
        setResults(null);
        try {
            // Split by space or comma
            const patterns = patternsInput.trim().split(/[\s,]+/);
            const data = await runSimulation(patterns);

            setLogs(data.logs);
            setResults(data.results);
        } catch (error) {
            setLogs((prev) => [...prev, `Error: ${error.message}`]);
        } finally {
            setIsLoading(false);
        }
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
        },
    };

    const getLogTagClass = (line) => {
        if (line.includes('[Edge')) return 'tag-edge';
        if (line.includes('[Core')) return 'tag-core';
        if (line.includes('[Dst')) return 'tag-dst';
        return '';
    };

    const getLogTagText = (line) => {
        if (line.includes('[Edge')) return 'EDGE';
        if (line.includes('[Core')) return 'CORE';
        if (line.includes('[Dst')) return 'DEST';
        return 'INFO';
    };

    return (
        <div className="dashboard-layout">
            <div className="main-panel">
                <div className="card">
                    <div className="config-panel">
                        <div className="input-group">
                            <input
                                type="text"
                                className="pattern-input"
                                value={patternsInput}
                                onChange={(e) => setPatternsInput(e.target.value)}
                                placeholder="Enter patterns (e.g., E A B)"
                            />
                        </div>
                        <button
                            className="btn btn-primary"
                            onClick={handleRun}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Running...' : 'Run Simulation'}
                        </button>
                    </div>
                </div>

                {results && (
                    <div className="card">
                        <h3>Detailed Statistics</h3>
                        <table className="stats-table">
                            <thead>
                                <tr>
                                    <th>Source ID</th>
                                    <th>Type</th>
                                    <th>Completion (ms)</th>
                                    <th>Drop Rate (%)</th>
                                    <th>Avg Latency (ms)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {results.map((r) => (
                                    <tr key={r.source_id}>
                                        <td>Source {r.source_id}</td>
                                        <td><span className={`badge badge-${r.type}`}>{r.type}</span></td>
                                        <td>{r.completion_time.toFixed(1)}</td>
                                        <td>{r.drop_rate.toFixed(1)}</td>
                                        <td>{r.avg_latency.toFixed(1)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {results && (
                    <div className="charts-section">
                        <div className="card">
                            <Bar
                                options={{
                                    ...chartOptions,
                                    plugins: { ...chartOptions.plugins, title: { display: true, text: 'Completion Time (ms)' } }
                                }}
                                data={{
                                    labels: results.map(r => `Src ${r.source_id}`),
                                    datasets: [{
                                        label: 'Time (ms)',
                                        data: results.map(r => r.completion_time),
                                        backgroundColor: 'rgba(59, 130, 246, 0.7)',
                                    }]
                                }}
                            />
                        </div>
                        <div className="card">
                            <Bar
                                options={{
                                    ...chartOptions,
                                    plugins: { ...chartOptions.plugins, title: { display: true, text: 'Drop Rate (%)' } }
                                }}
                                data={{
                                    labels: results.map(r => `Src ${r.source_id}`),
                                    datasets: [{
                                        label: 'Drop Rate (%)',
                                        data: results.map(r => r.drop_rate),
                                        backgroundColor: 'rgba(239, 68, 68, 0.7)',
                                    }]
                                }}
                            />
                        </div>
                        <div className="card">
                            <Bar
                                options={{
                                    ...chartOptions,
                                    plugins: { ...chartOptions.plugins, title: { display: true, text: 'Avg Latency (ms)' } }
                                }}
                                data={{
                                    labels: results.map(r => `Src ${r.source_id}`),
                                    datasets: [{
                                        label: 'Latency (ms)',
                                        data: results.map(r => r.avg_latency),
                                        backgroundColor: 'rgba(16, 185, 129, 0.7)',
                                    }]
                                }}
                            />
                        </div>
                    </div>
                )}
            </div>

            <div className="side-panel">
                <div className="card">
                    <h3>Simulation Logs</h3>
                    <div className="logs-container">
                        {logs.length === 0 && <div className="text-secondary">No logs generated yet.</div>}
                        {logs.map((log, index) => (
                            <div key={index} className="log-entry">
                                <span className={`log-tag ${getLogTagClass(log)}`}>{getLogTagText(log)}</span>
                                <span className="log-msg">{log}</span>
                            </div>
                        ))}
                        <div ref={logsEndRef} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
