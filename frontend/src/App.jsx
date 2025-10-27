import React, { useState, useEffect, useMemo } from 'react';
import { Layers3, CloudRain, Zap, Map, Activity, BarChart3, Menu, X, LocateFixed, Sun } from 'lucide-react';

// --- Utility Functions ---

/**
 * Calculates the risk category and associated colors based on a 0-10 score.
 * Green (0-3.5): Low
 * Yellow (3.6-7.4): Medium
 * Red (7.5-10): High
 * @param {number} score
 */
const getRiskDetails = (score) => {
    if (score >= 7.5) {
        return {
            category: "High Risk",
            color: "text-red-400 border-red-400 bg-red-900/50",
            dotColor: "bg-red-500",
        };
    } else if (score >= 3.6) {
        return {
            category: "Medium Risk",
            color: "text-yellow-400 border-yellow-400 bg-yellow-900/50",
            dotColor: "bg-yellow-500",
        };
    } else {
        return {
            category: "Low Risk",
            color: "text-green-400 border-green-400 bg-green-900/50",
            dotColor: "bg-green-500",
        };
    }
};

// --- Mock Data Simulation (Replaces API Calls/ML Results for now) ---
const mockDashboardData = {
    location: "Kolkata, India",
    lastUpdated: new Date().toLocaleTimeString(),
    currentWeather: {
        temp: 28,
        humidity: 78,
        windSpeed: 15,
        pressure: 1012,
    },
    riskScores: {
        flooding: 8.2,
        mudslide: 6.5,
        cyclone: 2.1,
    },
    rainfallForecast: "Heavy rain (25mm/hr) expected within 3 hours."
};

const mockCycloneData = [
    { name: "Cyclone Amphan", year: 2020, severity: 9.5, path: "Bay of Bengal -> West Bengal" },
    { name: "Cyclone Fani", year: 2019, severity: 7.8, path: "Bay of Bengal -> Odisha" },
    { name: "Dummy Cyclone 2025", year: 2025, severity: 3.1, path: "Placeholder Path" },
];

// --- Sub-Components ---

const DashboardCard = ({ title, value, unit, icon: Icon, colorClass }) => (
    <div className="p-4 bg-gray-800/70 border border-gray-700 rounded-xl shadow-lg transition duration-300 hover:shadow-2xl hover:border-blue-500">
        <div className="flex items-center justify-between">
            <div className={`p-3 rounded-full ${colorClass || 'bg-blue-900/50 text-blue-400'}`}>
                <Icon size={20} />
            </div>
            <div className="text-right">
                <p className="text-3xl font-bold text-white">{value}</p>
                <p className="text-xs text-gray-400 uppercase">{unit}</p>
            </div>
        </div>
        <p className="mt-3 text-sm font-medium text-gray-300">{title}</p>
    </div>
);

const RiskScoreIndicator = ({ name, score }) => {
    const details = getRiskDetails(score);
    return (
        <div className={`p-4 rounded-xl border-l-4 ${details.color} font-mono flex justify-between items-center`}>
            <div>
                <p className="text-lg font-semibold text-white">{name}</p>
                <p className="text-sm text-gray-400">{details.category}</p>
            </div>
            <div className="flex items-center space-x-2">
                <span className={`w-3 h-3 rounded-full ${details.dotColor} animate-pulse`}></span>
                <span className="text-3xl font-extrabold">{score.toFixed(1)}</span>
            </div>
        </div>
    );
};

// --- Page Components ---

const Dashboard = ({ data }) => {
    const { flooding, mudslide, cyclone } = data.riskScores;

    return (
        <div className="p-6 space-y-8">
            <h1 className="text-3xl font-extrabold text-white flex items-center">
                <LocateFixed className="w-6 h-6 mr-3 text-blue-400" />
                Current Focus: {data.location}
            </h1>
            <p className="text-sm text-gray-500">Data Last Updated: {data.lastUpdated}</p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <DashboardCard title="Temperature" value={data.currentWeather.temp} unit="°C" icon={Sun} colorClass="bg-red-900/50 text-red-400" />
                <DashboardCard title="Humidity" value={data.currentWeather.humidity} unit="%" icon={Layers3} colorClass="bg-cyan-900/50 text-cyan-400" />
                <DashboardCard title="Wind Speed" value={data.currentWeather.windSpeed} unit="km/h" icon={Zap} colorClass="bg-green-900/50 text-green-400" />
                <DashboardCard title="Air Pressure" value={data.currentWeather.pressure} unit="hPa" icon={Activity} colorClass="bg-purple-900/50 text-purple-400" />
            </div>

            <div className="p-6 bg-gray-800 rounded-xl shadow-2xl border border-gray-700">
                <h2 className="text-2xl font-bold text-white mb-4">Risk Assessment Overview (0-10)</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <RiskScoreIndicator name="Flooding Risk" score={flooding} />
                    <RiskScoreIndicator name="Mudslide Risk" score={mudslide} />
                    <RiskScoreIndicator name="Cyclone Risk" score={cyclone} />
                </div>
            </div>

            <div className="p-6 bg-gray-800 rounded-xl shadow-2xl border border-gray-700">
                <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                    <CloudRain className="w-5 h-5 mr-2 text-blue-400" />
                    Short-Term Rainfall Forecast
                </h2>
                <p className="text-xl text-blue-300 font-medium">{data.rainfallForecast}</p>
                <div className="h-64 mt-4 bg-gray-700 rounded-lg flex items-center justify-center text-gray-400">
                    [Placeholder for Recharts Time-Series Graph]
                </div>
            </div>
        </div>
    );
};

const CyclonePredictionPage = () => {
    const [filterYear, setFilterYear] = useState('2025');
    const filteredData = mockCycloneData.filter(c => filterYear === '' || c.year.toString() === filterYear);

    return (
        <div className="p-6 space-y-6">
            <h1 className="text-3xl font-extrabold text-white">Cyclone Path Tracking</h1>

            <div className="flex flex-col md:flex-row gap-4 items-center">
                <select
                    value={filterYear}
                    onChange={(e) => setFilterYear(e.target.value)}
                    className="p-2 border border-gray-600 bg-gray-800 text-white rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full md:w-auto"
                >
                    <option value="">All Years</option>
                    <option value="2025">2025 (Predicted)</option>
                    <option value="2020">2020 (Historical)</option>
                    <option value="2019">2019 (Historical)</option>
                </select>
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-200 w-full md:w-auto flex items-center justify-center">
                    <Map size={18} className="mr-2" />
                    Load Map Visualization
                </button>
            </div>

            <div className="h-[60vh] bg-gray-700 rounded-xl shadow-xl flex items-center justify-center text-gray-400 border border-gray-600">
                [Placeholder for Leaflet Map: Cyclone Path Visualization]
            </div>

            <div className="overflow-x-auto bg-gray-800 rounded-xl shadow-inner border border-gray-700">
                <table className="min-w-full divide-y divide-gray-700">
                    <thead className="bg-gray-700">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Year</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Name</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Severity (0-10)</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Affected Areas/Path</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                        {filteredData.map((cyclone, index) => (
                            <tr key={index} className="hover:bg-gray-700/50 transition duration-150">
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{cyclone.year}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">{cyclone.name}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRiskDetails(cyclone.severity).dotColor.replace('bg-', 'bg-')}`}>{cyclone.severity.toFixed(1)}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{cyclone.path}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const FloodingPredictionPage = () => {
    const [soilType, setSoilType] = useState('clay');
    const [infrastructure, setInfrastructure] = useState(5);
    const [predictedRisk, setPredictedRisk] = useState(0);

    const calculateCustomRisk = (e) => {
        e.preventDefault();
        let baseRisk = 5.0;
        if (soilType === 'sand') baseRisk -= 1.5;
        if (soilType === 'silt') baseRisk += 1.0;
        baseRisk += (10 - infrastructure) * 0.3;

        const finalRisk = Math.min(10.0, Math.max(0.0, baseRisk + (Math.random() * 2 - 1)));
        setPredictedRisk(finalRisk);
    };

    const riskDetails = getRiskDetails(predictedRisk);

    return (
        <div className="p-6 space-y-6">
            <h1 className="text-3xl font-extrabold text-white">Flooding & Mudslide Risk Assessment</h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                <div className="lg:col-span-1 p-6 bg-gray-800 rounded-xl shadow-2xl border border-gray-700 h-full">
                    <h2 className="text-xl font-bold text-white mb-4">Custom Scenario Calculator</h2>
                    <p className="text-gray-400 text-sm mb-4">Input infrastructure and soil conditions to simulate flood risk.</p>
                    <form onSubmit={calculateCustomRisk} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">Infrastructure Strength (1-10)</label>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                value={infrastructure}
                                onChange={(e) => setInfrastructure(parseFloat(e.target.value))}
                                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer range-lg"
                            />
                            <div className="text-sm text-gray-500 flex justify-between"><span>1 (Weak)</span><span>{infrastructure}</span><span>10 (Strong)</span></div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">Soil Type</label>
                            <select
                                value={soilType}
                                onChange={(e) => setSoilType(e.target.value)}
                                className="p-2 border border-gray-600 bg-gray-700 text-white rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full"
                            >
                                <option value="clay">Clay (High Retention)</option>
                                <option value="silt">Silt (Medium Retention)</option>
                                <option value="sand">Sand (Low Retention)</option>
                                <option value="loam">Loam (Mixed)</option>
                            </select>
                        </div>

                        <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded-lg transition duration-200 mt-4">
                            Calculate Risk
                        </button>
                    </form>

                    {predictedRisk > 0 && (
                        <div className={`mt-6 p-4 rounded-xl text-center border-2 ${riskDetails.color}`}>
                            <p className="text-2xl font-extrabold">Predicted Risk Score: {predictedRisk.toFixed(1)}</p>
                            <p className="text-lg font-medium">{riskDetails.category}</p>
                        </div>
                    )}
                </div>

                <div className="lg:col-span-2 h-[70vh] bg-gray-700 rounded-xl shadow-xl flex items-center justify-center text-gray-400 border border-gray-600">
                    [Placeholder for Leaflet Map: Affected Areas & Risk Layers]
                </div>
            </div>
        </div>
    );
};

const RainfallDataPage = () => {
    return (
        <div className="p-6 space-y-6">
            <h1 className="text-3xl font-extrabold text-white">Historical & Predicted Rainfall Data</h1>

            <div className="p-4 bg-gray-800 rounded-xl flex flex-wrap gap-4 items-center border border-gray-700">
                <input type="text" placeholder="Location" className="p-2 border border-gray-600 bg-gray-700 text-white rounded-lg" />
                <input type="date" className="p-2 border border-gray-600 bg-gray-700 text-white rounded-lg" />
                <input type="number" placeholder="Min Intensity (mm/hr)" className="p-2 border border-gray-600 bg-gray-700 text-white rounded-lg w-48" />
                <select className="p-2 border border-gray-600 bg-gray-700 text-white rounded-lg">
                    <option>View: Map</option>
                    <option>View: Table</option>
                </select>
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-200">
                    Apply Filters
                </button>
            </div>

            <div className="h-[65vh] bg-gray-700 rounded-xl shadow-xl flex items-center justify-center text-gray-400 border border-gray-600">
                [Placeholder for Map/Recharts: Visualize Historical & Predicted Rainfall over Time/Area]
            </div>

            <div className="text-sm text-gray-400 mt-4">
                *Data will include rainfall occurrence, intensity, humidity, wind speed, and air pressure.
            </div>
        </div>
    );
};

// --- Main Application Component ---

const App = () => {
    const [currentPage, setCurrentPage] = useState('dashboard');
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    const navItems = [
        { id: 'dashboard', name: 'Dashboard', icon: BarChart3 },
        { id: 'cyclone', name: 'Cyclone Tracking', icon: Zap },
        { id: 'flooding', name: 'Flooding Assessment', icon: Layers3 },
        { id: 'rainfall', name: 'Rainfall Data', icon: CloudRain },
    ];

    const renderPage = useMemo(() => {
        switch (currentPage) {
            case 'cyclone':
                return <CyclonePredictionPage />;
            case 'flooding':
                return <FloodingPredictionPage />;
            case 'rainfall':
                return <RainfallDataPage />;
            case 'dashboard':
            default:
                return <Dashboard data={mockDashboardData} />;
        }
    }, [currentPage]);

    const Sidebar = () => (
        <div className={`fixed inset-y-0 left-0 transform ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:relative lg:translate-x-0 transition duration-200 ease-in-out w-64 bg-gray-900 border-r border-gray-700 z-30 flex flex-col`}>
            <div className="p-6 border-b border-gray-700 flex items-center justify-between">
                <h2 className="text-xl font-extrabold text-blue-400">Weather Predictor</h2>
                <button className="lg:hidden text-gray-400 hover:text-white" onClick={() => setIsSidebarOpen(false)}>
                    <X size={24} />
                </button>
            </div>
            <nav className="flex-grow p-4 space-y-2">
                {navItems.map(item => (
                    <button
                        key={item.id}
                        onClick={() => {
                            setCurrentPage(item.id);
                            setIsSidebarOpen(false);
                        }}
                        className={`w-full flex items-center p-3 rounded-xl transition-colors duration-150 ${
                            currentPage === item.id
                                ? 'bg-blue-600 text-white shadow-lg'
                                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                        }`}
                    >
                        <item.icon size={20} className="mr-3" />
                        {item.name}
                    </button>
                ))}
            </nav>
            <div className="p-4 border-t border-gray-700 text-xs text-gray-500">
                <p>Status: Offline/Mock Data</p>
                <p>Tech Stack: React/Tailwind</p>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen flex bg-gray-950 text-gray-100 font-sans">
            <Sidebar />

            <div className="flex-1 flex flex-col overflow-hidden">
                <header className="flex items-center justify-between p-4 bg-gray-900 border-b border-gray-700 lg:hidden">
                    <h1 className="text-xl font-bold text-blue-400">WPP</h1>
                    <button className="text-gray-400 hover:text-white" onClick={() => setIsSidebarOpen(true)}>
                        <Menu size={24} />
                    </button>
                </header>

                <main className="flex-1 overflow-x-hidden overflow-y-auto">
                    {renderPage}
                </main>
            </div>
        </div>
    );
};

export default App;
