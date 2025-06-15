# Kubernetes Cluster Setup

An automated Python script for setting up Kubernetes clusters using SSH connections. This tool bootstraps a complete Kubernetes cluster with one master node and multiple worker nodes.

## Features

- **Automated cluster setup**: One command to set up the entire cluster
- **Multi-node support**: Configure one master and multiple worker nodes
- **Parallel worker setup**: Workers are configured concurrently for faster deployment
- **Comprehensive logging**: Detailed logs saved to file and console
- **Flexible deployment**: Options for master-only, workers-only, or full cluster setup
- **Cleanup capabilities**: Reset and clean up existing clusters
- **Error handling**: Robust error handling with detailed feedback

## Prerequisites

- **Python 3.6+** on the control machine
- **Ubuntu/Debian** target nodes (tested on Ubuntu 18.04+)
- **SSH access** to all target nodes with sudo privileges
- **Internet connectivity** on all nodes for package downloads
- **Minimum 2GB RAM** per node (4GB+ recommended for master)

## Installation

1. Clone or download the project files
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Inventory File

Edit `inventory.ini` to define your cluster nodes:

```ini
[all:vars]
ansible_port=22
ansible_python_interpreter=/usr/bin/python3

[master]
master1 ansible_host=10.11.3.251 ansible_user=docker ansible_ssh_pass='your_password'

[workers]
worker1 ansible_host=10.11.4.88 ansible_user=test ansible_ssh_pass='your_password'
worker2 ansible_host=192.168.1.12 ansible_user=ubuntu ansible_ssh_pass='worker_password'
```

#### Inventory Parameters

- `ansible_host`: IP address of the node
- `ansible_user`: SSH username
- `ansible_ssh_pass`: SSH password
- `ansible_port`: SSH port (default: 22)
- `ansible_ssh_private_key_file`: SSH private key file (alternative to password)

## Usage

### Basic Cluster Setup

Set up the complete cluster (master + all workers):
```bash
python3 k8s_cluster_setup.py
```

### Advanced Options

```bash
# Use custom inventory file
python3 k8s_cluster_setup.py -i my_inventory.ini

# Set up master node only
python3 k8s_cluster_setup.py --master-only

# Set up worker nodes only (requires existing master)
python3 k8s_cluster_setup.py --workers-only

# Enable verbose logging
python3 k8s_cluster_setup.py -v

# Reset/cleanup existing cluster
python3 k8s_cluster_setup.py --reset
```

### Command Line Options

- `-i, --inventory`: Specify inventory file (default: `inventory.ini`)
- `--master-only`: Set up only the master node
- `--workers-only`: Set up only worker nodes
- `--reset`: Clean up and reset the cluster
- `-v, --verbose`: Enable debug logging

## What the Script Does

### Master Node Setup
1. **System preparation**: Updates packages, installs dependencies
2. **Container runtime**: Configures containerd with systemd cgroup driver
3. **Kubernetes packages**: Installs kubelet, kubeadm, kubectl
4. **Cluster initialization**: Runs `kubeadm init` with pod network CIDR
5. **Network plugin**: Installs Flannel CNI for pod networking
6. **Join command**: Generates and saves worker join command

### Worker Node Setup
1. **System preparation**: Same as master (packages, containerd, k8s packages)
2. **Cluster joining**: Joins the cluster using the generated join command
3. **Verification**: Ensures node appears in cluster and becomes Ready

### System Configuration
- Disables swap (required for Kubernetes)
- Loads required kernel modules (overlay, br_netfilter, bridge)
- Sets network sysctls for bridge networking
- Configures containerd with systemd cgroup driver
- Sets up Kubernetes package repositories

## Output Files

- `k8s_setup.log`: Detailed setup logs
- `join_command.yml`: Worker join command (for manual operations)

## Network Configuration

The script configures:
- **Pod network CIDR**: `10.244.0.0/16` (Flannel default)
- **Service network**: Kubernetes default (`10.96.0.0/12`)
- **CNI plugin**: Flannel for overlay networking

## Security Considerations

⚠️ **Important Security Notes:**
- SSH passwords are stored in plain text in the inventory file
- Consider using SSH keys instead of passwords for production
- Ensure proper firewall rules are in place
- Review and harden the cluster configuration for production use

### Recommended Security Improvements
```ini
# Use SSH keys instead of passwords
[master]
master1 ansible_host=10.11.3.251 ansible_user=docker ansible_ssh_private_key_file=~/.ssh/id_rsa
```

## Troubleshooting

### Common Issues

**SSH Connection Failed**
- Verify IP addresses and credentials in inventory
- Check network connectivity: `ping <node_ip>`
- Ensure SSH service is running on target nodes

**Kubeadm Init Failed**
- Check system requirements (RAM, disk space)
- Verify no existing Kubernetes installation
- Run with `--reset` first to clean up

**Worker Join Failed**
- Ensure master is fully initialized
- Check network connectivity between master and workers
- Verify join command is valid (check `join_command.yml`)

**Nodes Not Ready**
- Wait for CNI plugin to be fully deployed
- Check pod status: `kubectl get pods -n kube-system`
- Verify container runtime is working

### Debug Commands

```bash
# Check node status
kubectl get nodes -o wide

# Check system pods
kubectl get pods -n kube-system

# Check logs
tail -f k8s_setup.log

# Manual cleanup if needed
sudo kubeadm reset -f
sudo apt-get purge -y kubeadm kubelet kubectl
```

## Kubernetes Version

The script installs Kubernetes v1.29 (stable). To use a different version, modify the repository URL in the `_k8s_pkgs` method.

## Supported Operating Systems

- Ubuntu 18.04+
- Debian 9+
- Other systemd-based distributions (may require modifications)

## Contributing

Feel free to submit issues and pull requests. When contributing:
1. Test changes on multiple node configurations
2. Update documentation for new features
3. Follow existing code style and patterns

## License

This project is provided as-is for educational and development purposes. Use at your own risk in production environments.