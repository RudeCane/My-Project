import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export default function MarketMakerDashboard() {
    const [tradeLogs, setTradeLogs] = useState([]);
    const [stopLoss, setStopLoss] = useState(null);
    const [maxExposure, setMaxExposure] = useState(null);
    const [autoStopLoss, setAutoStopLoss] = useState(false);
    const [isRunning, setIsRunning] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetch("/api/trades")
            .then((res) => res.json())
            .then((data) => setTradeLogs(data));

        fetch("/api/bot-status")
            .then((res) => res.json())
            .then((data) => {
                setIsRunning(data.running);
                setAutoStopLoss(data.autoStopLoss);
                setStopLoss(data.stopLoss);
                setMaxExposure(data.maxExposure);
            });
    }, []);

    const toggleBot = () => {
        setLoading(true);
        fetch("/api/toggle-bot", { method: "POST" })
            .then((res) => res.json())
            .then((data) => setIsRunning(data.running))
            .finally(() => setLoading(false));
    };

    const updateStopLoss = () => {
        fetch("/api/set-stop-loss", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ stopLoss: parseFloat(stopLoss) }),
        });
    };

    const updateMaxExposure = () => {
        fetch("/api/set-max-exposure", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ maxExposure: parseFloat(maxExposure) }),
        });
    };

    const toggleAutoStopLoss = () => {
        const newValue = !autoStopLoss;
        setAutoStopLoss(newValue);
        fetch("/api/toggle-auto-stop-loss", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ autoStopLoss: newValue }),
        });
    };

    const formattedChartData = tradeLogs.map((log) => ({
        timestamp: log.timestamp || log.time || "N/A",
        price: log.price || 0,
    }));

    return (
        <div className="p-4 grid gap-4 grid-cols-1 md:grid-cols-2 bg-black text-white">
            <h1 className="text-3xl font-bold text-orange-500 text-center col-span-2">Blazin The Nation</h1>

            <Card className="bg-gray-900 border-orange-500">
                <CardContent>
                    <h2 className="text-xl font-semibold text-orange-400">Trade Execution Logs</h2>
                    <ul>
                        {tradeLogs.length === 0 ? (
                            <li className="text-gray-400">No trade logs available.</li>
                        ) : (
                            tradeLogs.map((log, index) => (
                                <li key={index} className="border-b py-2 border-orange-500">{log.message}</li>
                            ))
                        )}
                    </ul>
                </CardContent>
            </Card>

            <Card className="bg-gray-900 border-orange-500">
                <CardContent>
                    <h2 className="text-xl font-semibold text-orange-400">Bot Controls</h2>
                    <Button onClick={toggleBot} disabled={loading} className="mt-2 bg-orange-500 text-black">
                        {isRunning ? "Stop Bot" : "Start Bot"}
                    </Button>

                    <div className="mt-4">
                        <label className="block text-white">Stop-Loss:</label>
                        <input
                            type="number"
                            className="border p-2 w-full bg-gray-800 text-white"
                            value={stopLoss || ""}
                            onChange={(e) => setStopLoss(e.target.value)}
                        />
                        <Button onClick={updateStopLoss} className="mt-2 w-full bg-orange-500 text-black">
                            Set Stop-Loss
                        </Button>
                    </div>

                    <div className="mt-4">
                        <label className="block text-white">Max Exposure:</label>
                        <input
                            type="number"
                            className="border p-2 w-full bg-gray-800 text-white"
                            value={maxExposure || ""}
                            onChange={(e) => setMaxExposure(e.target.value)}
                        />
                        <Button onClick={updateMaxExposure} className="mt-2 w-full bg-orange-500 text-black">
                            Set Max Exposure
                        </Button>
                    </div>

                    <div className="mt-4">
                        <label className="block text-white">Auto Stop-Loss:</label>
                        <Button onClick={toggleAutoStopLoss} className="mt-2 w-full bg-orange-500 text-black">
                            {autoStopLoss ? "Disable" : "Enable"} Auto Stop-Loss
                        </Button>
                    </div>
                </CardContent>
            </Card>

            <Card className="col-span-2 bg-gray-900 border-orange-500">
                <CardContent>
                    <h2 className="text-xl font-semibold text-orange-400">Trade Volume Chart</h2>
                    <LineChart width={600} height={300} data={formattedChartData}>
                        <XAxis dataKey="timestamp" stroke="white" />
                        <YAxis stroke="white" />
                        <Tooltip wrapperStyle={{ color: "black" }} />
                        <CartesianGrid stroke="#444" strokeDasharray="5 5" />
                        <Line type="monotone" dataKey="price" stroke="orange" />
                    </LineChart>
                </CardContent>
            </Card>
        </div>
    );
}
