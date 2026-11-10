import { useState, useEffect, useRef } from "react";
import "./App.css";

// Pi IP for the rover, "localhost" for laptop testing
// const ROVER_HOST = "192.168.1.175";
const ROVER_HOST = "localhost";

// Camera frame width from videos.py, used to find where an object is
const FRAME_WIDTH = 640;

// Milliseconds to wait before trying to reconnect
const RECONNECT_DELAY = 2000;

// Rover data now come from backend through WebSocket
function useRoverData() {
  const [data, setData] = useState({
    connected: false,
    controllerConnected: false,
    rgbCameraConnected: false,
    thermalCameraConnected: false,
    mode: "DRIVE",
    wheels: { FL: 0, FR: 0, RL: 0, RR: 0 },
    drivers: {
     MDD10A_1: "UNKNOWN",
     MDD10A_2: "UNKNOWN",
},
battery: 0,
detections: [],
  });
   // Connect frontend to backend through WebSocket
   useEffect(() => {
    let socket;
    let reconnectTimer;
    let stopped = false;

    function connect() {
      socket = new WebSocket(`ws://${ROVER_HOST}:8765`);

      socket.onopen = () => {
        console.log("Connected to rover backend");
      };

      socket.onmessage = (event) => {
        // Receive rover data from backend
        const roverData = JSON.parse(event.data);

        setData(roverData);
      };

      socket.onclose = () => {
        console.log("Disconnected from rover backend, reconnecting...");

        // Show everything as offline while disconnected
        setData((prev) => ({
          ...prev,
          connected: false,
          controllerConnected: false,
          rgbCameraConnected: false,
          thermalCameraConnected: false,
          detections: [],
        }));

        // Try again unless the dashboard was closed
        if (!stopped) {
          reconnectTimer = setTimeout(connect, RECONNECT_DELAY);
        }
      };
    }

    connect();

    return () => {
      stopped = true;
      clearTimeout(reconnectTimer);
      socket.close();
    };
  }, []);

  return data;
}

// 32x24 MLX90640 thermal feed from backend
function ThermalFeed({ thermal }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    // Thermal data arrives from backend
    if (!thermal || !thermal.pixels || thermal.pixels.length === 0) {
      return;
    }

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const COLS = thermal.width;
    const ROWS = thermal.height;

    // Avoid dividing by zero if every pixel is the same temperature
    const range = thermal.max - thermal.min || 1;

    const cellW = canvas.width / COLS;
    const cellH = canvas.height / ROWS;

    for (let y = 0; y < ROWS; y++) {
      for (let x = 0; x < COLS; x++) {
        const value = thermal.pixels[y * COLS + x];

        // Scale temperature to 0-1 for the color map
        const temp = (value - thermal.min) / range;

        ctx.fillStyle = thermalColor(temp);

        ctx.fillRect(
          x * cellW,
          y * cellH,
          cellW + 1,
          cellH + 1
        );
      }
    }
  }, [thermal]);

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

// Live camera stream from videos.py
function RgbFeed({ connected }) {
  if (!connected) {
    return (
      <div className="rgb-feed">
        <div className="feed-waiting">Waiting for camera...</div>
      </div>
    );
  }

  return (
    <div className="rgb-feed">
      <img
        src={`http://${ROVER_HOST}:5001/video_feed`}
        alt="Rover RGB Camera"
        className="rgb-video"
      />
    </div>
  );
}

// Which third of the frame the object is in
function objectPosition(box) {
  const centerX = (box[0] + box[2]) / 2;

  if (centerX < FRAME_WIDTH / 3) {
    return "left";
  }

  if (centerX < (FRAME_WIDTH * 2) / 3) {
    return "center";
  }

  return "right";
}

// List of objects YOLO currently sees
function DetectionList({ detections }) {
  if (!detections || detections.length === 0) {
    return <div className="detection-empty">No objects detected</div>;
  }

  return (
    <ul className="detection-list">
      {detections.map((det, i) => (
        <li className="detection-item" key={i}>
          <span className="detection-label">{det.label}</span>
          <span className="detection-info">
            {Math.round(det.confidence * 100)}% · {objectPosition(det.box)}
          </span>
        </li>
      ))}
    </ul>
  );
}

export default function RoverDashboard() {
  const data = useRoverData();

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
            <RgbFeed connected={data.rgbCameraConnected} />
          </div>

          <DetectionList detections={data.detections} />
        </section>

        <section className="panel">
          <div className="panel-header">
            Thermal - MLX90640
          </div>

          <div className="feed-content">
            <ThermalFeed thermal={data.thermal} />
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
              ok={data.rgbCameraConnected}
              text={`RGB Camera: ${
                data.rgbCameraConnected ? "Connected" : "Disconnected"
              }`}
            />

            <StatusRow
              ok={data.thermalCameraConnected}
              text={`Thermal Camera: ${
              data.thermalCameraConnected ? "Connected" : "Disconnected"
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