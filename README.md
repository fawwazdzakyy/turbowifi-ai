<h1 align="center">
  🚀 TurboWiFi AI
</h1>

<p align="center">
  <b>An autonomous, AI-driven network optimization toolkit engineered for Linux and Termux.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/Platform-Ubuntu%20%7C%20Debian%20%7C%20Termux-lightgrey.svg" alt="Platforms">
  <img src="https://img.shields.io/badge/Version-1.0.0-success.svg" alt="Version 1.0.0">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License MIT">
</p>

---

TurboWiFi AI actively discovers network bottlenecks, predicts congestion using heuristic AI, and safely applies optimizations to DNS, TCP, and MTU layers without requiring complex manual configurations. It brings enterprise-grade network tuning capabilities directly to your local terminal.

## ✨ Core Features

* 🧠 **Auto Orchestrator**: One-command AI heuristic optimization. Automatically finds the optimal DNS resolvers, TCP Congestion Control (e.g., BBR), and exact Path MTU settings for your current network state.
* 📊 **TUI Dashboard (`turbowifi watch`)**: Gorgeous real-time terminal UI monitoring latency, jitter, packet loss, and CPU overhead built on Textual.
* 🛡️ **MTU Optimizer**: Utilizes binary search with the `ping -M do` DF bit mechanism to find the perfect Path MTU, preventing silent packet fragmentation. Includes a fail-safe Rollback Engine.
* 🚀 **Segmented Download Engine**: Highly concurrent HTTP Range-request downloader designed for maximum network saturation and throughput, with automatic resuming and capability fallback.
* 👻 **Background Daemon**: Continuously monitors the network with negligible battery and resource impact (< 50MB RAM, < 5% CPU).

## 🚀 Installation

TurboWiFi AI is designed to be easily installable via secure one-liner scripts or standard Python package managers.

### Option 1: Automatic Installer (Ubuntu / Debian)
This script will safely install TurboWiFi AI globally using `pipx` (PEP 668 compliant).
```bash
curl -fsSL https://raw.githubusercontent.com/fawwazdzakyy/turbowifi-ai/main/install.sh | bash
```

### Option 2: Android Termux
Optimized specifically for limited privileges in Termux environments.
```bash
curl -fsSL https://raw.githubusercontent.com/fawwazdzakyy/turbowifi-ai/main/install-termux.sh | bash
```

### Option 3: Manual Install via pipx (Recommended)
```bash
pipx install git+https://github.com/fawwazdzakyy/turbowifi-ai.git
```

## 💻 Command Reference

TurboWiFi AI provides a rich CLI built with `click` and `rich` for stunning terminal outputs.

### 🏥 Diagnostics & Benchmarks
| Command | Description |
|---|---|
| `turbowifi doctor` | Validates system health, permissions, capabilities, and database integrity. |
| `turbowifi benchmark` | Runs a deep network benchmark (latency, jitter, loss, DNS response) and calculates a composite health score. |
| `turbowifi scan` | Performs a lightweight background scan of the current network stability. |

### ⚡ AI & Auto-Optimization
| Command | Description |
|---|---|
| `sudo turbowifi auto` | **[RECOMMENDED]** Let the AI scan the network and orchestrate all required optimizations automatically. |

### 🛠️ Subsystems Management
**MTU (Maximum Transmission Unit)**
| Command | Description |
|---|---|
| `turbowifi mtu status` | Shows current MTU of the active interface. |
| `turbowifi mtu recommend` | Runs a binary search algorithm to find the ideal MTU. |
| `sudo turbowifi mtu apply` | Applies the recommended MTU and verifies the performance gain. |
| `sudo turbowifi mtu rollback` | Reverts the MTU to the original safe state. |

**DNS (Domain Name System)**
| Command | Description |
|---|---|
| `turbowifi dns benchmark` | Benchmarks top public DNS providers (Cloudflare, Google, AdGuard, etc.) to find the fastest response time. |
| `sudo turbowifi dns optimize` | Applies the fastest DNS provider to `systemd-resolved` or NetworkManager. |

**TCP Tuning**
| Command | Description |
|---|---|
| `turbowifi tcp status` | Shows current TCP congestion control (e.g., cubic, bbr) and kernel sysctl parameters. |
| `sudo turbowifi tcp optimize` | Applies advanced sysctl parameters (BBR, window scaling, fastopen) for high throughput. |

### 📡 Real-time Monitoring & Daemon
| Command | Description |
|---|---|
| `turbowifi watch` | Launches the interactive Textual Dashboard. |
| `turbowifi daemon start` | Starts the background daemon to continuously monitor network health. |
| `turbowifi daemon status` | Checks if the background daemon is running. |
| `turbowifi daemon stop` | Stops the background daemon. |

### ⬇️ Segmented Downloader
| Command | Description |
|---|---|
| `turbowifi download <url>` | Downloads a file using intelligent concurrent threads and HTTP Range requests. |

## 🏗️ Architecture

TurboWiFi AI is built entirely in Python 3.12+ and strictly avoids heavy, unneeded dependencies. The core logic is structured into:
- **Rule Engine & ML Heuristics**: Lightweight decision-making trees that map network scan results to optimization capabilities.
- **SQLite Persistence**: Stores time-series data of network metrics to provide long-term pattern prediction without cloud telemetry.
- **Capability Probing**: Centralized hardware and OS probing to ensure features fail gracefully if privileges (like `sudo`) are unavailable.
- **Fail-Safe Mechanism**: Every optimization creates a state backup before applying changes, ensuring 100% safe rollbacks.

## 🤝 Contributing

We welcome pull requests! Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for setup instructions, coding guidelines, and testing procedures (using `pytest`).

## 🛡️ Security

Found a vulnerability? Please responsibly disclose it. See [SECURITY.md](SECURITY.md) for details.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
