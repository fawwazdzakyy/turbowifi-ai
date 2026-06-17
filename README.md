# TurboWiFi AI 🚀

An autonomous, AI-driven network optimization toolkit engineered for Ubuntu Linux and Android Termux. 

TurboWiFi AI actively discovers network bottlenecks, predicts congestion, and safely applies optimizations to DNS, TCP, and MTU layers without requiring complex manual configurations.

## Features

- **Auto Orchestrator**: Just run `turbowifi auto` and let the AI find the optimal DNS, TCP Congestion Control, and MTU settings for your current network.
- **TUI Dashboard**: Gorgeous real-time terminal UI monitoring latency, jitter, packet loss, and CPU overhead (`turbowifi watch`).
- **MTU Optimizer**: Uses binary search to find the perfect Path MTU, preventing packet fragmentation. Includes a fail-safe Rollback Engine.
- **Segmented Download Engine**: Highly concurrent HTTP Range-request downloader for maximum throughput.
- **Background Daemon**: Continuously monitors the network with negligible battery impact (< 50MB RAM, < 5% CPU).

## Installation

### Ubuntu Linux
```bash
curl -fsSL https://raw.githubusercontent.com/fawwazdzakyy/turbowifi-ai/main/install.sh | bash
```

### Android Termux
```bash
curl -fsSL https://raw.githubusercontent.com/fawwazdzakyy/turbowifi-ai/main/install-termux.sh | bash
```

### Manual Install (pip)
```bash
pip install turbowifi-ai[all]
```

## Quick Start

1. **Check Environment Health:**
   ```bash
   turbowifi doctor
   ```

2. **Benchmark Your Network:**
   ```bash
   turbowifi benchmark
   ```

3. **Auto Optimize (Requires Root):**
   ```bash
   sudo turbowifi auto
   ```

4. **Monitor Real-Time Stats:**
   ```bash
   turbowifi watch
   ```

## Documentation
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development instructions.
- See [SECURITY.md](SECURITY.md) for vulnerability reporting.

## License
MIT License.
