import { useState, useEffect, useRef } from "react";
import "./App.css";

// Mock rover data
// Replace with backend/WebSocket data later

function useMockRoverData() {
  const [data, setData] = useState({
    connected: true,
    controllerConnected: true,
    mode: "DRIVE",
    wheels: { FL: 0, FR: 0, RL: 0, RR: 0 },
    drivers: { MDD10A_1: "OK", MDD10A_2: "OK" },
    battery: 12.8,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setData((prev) => {
        const jitter = () =>
          Math.max(
            0,
            Math.round(
              60 +
                Math.sin(Date.now() / 500) * 40 +
                (Math.random() * 20 - 10)
            )
          );

        return {
          ...prev,
          wheels: {
            FL: jitter(),
            FR: jitter(),
            RL: jitter(),
            RR: jitter(),
          },
          battery: +(12.4 + Math.random() * 0.4).toFixed(1),
        };
      });
    }, 400);

    return () => clearInterval(interval);
  }, []);

  return data;
}

// Simulated 32x24 MLX90640 thermal feed.
function ThermalFeed() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const COLS = 32;
    const ROWS = 24;

    let animationId;

    function render() {
      const t = Date.now() / 1000;

      const hotX = COLS / 2 + Math.sin(t) * 8;
      const hotY = ROWS / 2 + Math.cos(t * 0.7) * 5;

      const cellW = canvas.width / COLS;
      const cellH = canvas.height / ROWS;

      for (let y = 0; y < ROWS; y++) {
        for (let x = 0; x < COLS; x++) {
          const dist = Math.hypot(x - hotX, y - hotY);
          const temp = Math.max(0, 1 - dist / 12);

          ctx.fillStyle = thermalColor(temp);

          ctx.fillRect(
            x * cellW,
            y * cellH,
            cellW + 1,
            cellH + 1
          );
        }
      }

      animationId = requestAnimationFrame(render);
    }

    render();

    return () => cancelAnimationFrame(animationId);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      width={320}
      height={240}
      className="thermal-canvas"
    />
  );
}

function thermalColor(t) {
  if (t < 0.5) {
    const p = t / 0.5;

    return `rgb(
      ${Math.round(20 + p * 60)},
      ${Math.round(20 + p * 80)},
      ${Math.round(120 + p * 135)}
    )`;
  }

  const p = (t - 0.5) / 0.5;

  return `rgb(
    255,
    ${Math.round(80 + p * 175)},
    ${Math.round(60 * (1 - p) + p * 200)}
  )`;
}

// RGB placeholder until the real camera stream is connected
function RgbFeed() {
  return (
    <div className="rgb-feed">
      <span>RGB CAMERA - awaiting stream</span>

      <div className="detection-box">
        <span>person 0.87</span>
      </div>
    </div>
  );
}

export default function RoverDashboard() {
  const data = useMockRoverData();

  const wheels = [
    ["FL", "Front Left"],
    ["FR", "Front Right"],
    ["RL", "Rear Left"],
    ["RR", "Rear Right"],
  ];

  return (
    <div className="dashboard">
      <header className="header">
        <h1>ROVER CONTROL</h1>

        <div className={`mode ${data.mode.toLowerCase()}`}>
          MODE: {data.mode}
        </div>
      </header>

      <div className="feeds-row">
        <section className="panel">
          <div className="panel-header">RGB Camera</div>

          <div className="feed-content">
            <RgbFeed />
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            Thermal - MLX90640
          </div>

          <div className="feed-content">
            <ThermalFeed />
          </div>
        </section>
      </div>

      <div className="telemetry-row">
        <section className="panel">
          <div className="panel-header">
            Drivetrain - Encoder Feedback
          </div>

          <div className="wheel-grid">
            {wheels.map(([key, label]) => (
              <div className="wheel-card" key={key}>
                <span>{label}</span>

                <strong>
                  {data.wheels[key]}
                  <small> RPM</small>
                </strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            System Status
          </div>

          <div className="status-list">
            <StatusRow
              ok={data.connected}
              text={`Rover: ${
                data.connected ? "Ready" : "Offline"
              }`}
            />

            <StatusRow
              ok={data.controllerConnected}
              text={`Controller: ${
                data.controllerConnected
                  ? "Connected"
                  : "Disconnected"
              }`}
            />

            <StatusRow
              ok={data.drivers.MDD10A_1 === "OK"}
              text={`Driver 1: ${data.drivers.MDD10A_1}`}
            />

            <StatusRow
              ok={data.drivers.MDD10A_2 === "OK"}
              text={`Driver 2: ${data.drivers.MDD10A_2}`}
            />

            <div className="battery">
              Battery: {data.battery} V
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function StatusRow({ ok, text }) {
  return (
    <div className="status-row">
      <span
        className={`status-dot ${ok ? "ok" : "error"}`}
      />
      {text}
    </div>
  );
}