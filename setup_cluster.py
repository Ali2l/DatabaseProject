#!/usr/bin/env python3
"""
Redis Cluster Setup - Creates 6-node Redis Cluster
"""

import os
import subprocess
import time
import shutil


class RedisClusterSetup:
    """Creates Redis Cluster with 3 masters + 3 replicas."""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.cluster_dir = os.path.join(self.base_dir, "redis-cluster")
        self.ports = [7001, 7002, 7003, 7004, 7005, 7006]
    
    def create_config_files(self):
        """Create config file for each node."""
        if os.path.exists(self.cluster_dir):
            shutil.rmtree(self.cluster_dir)
        os.makedirs(self.cluster_dir)
        
        for port in self.ports:
            node_dir = os.path.join(self.cluster_dir, str(port))
            os.makedirs(node_dir)
            
            config = f"""port {port}
                cluster-enabled yes
                cluster-config-file nodes.conf
                cluster-node-timeout 5000
                appendonly yes
                bind 127.0.0.1
                protected-mode no
                daemonize no
                dir {node_dir}
                logfile {node_dir}/redis.log
                """
            config_path = os.path.join(node_dir, "redis.conf")
            with open(config_path, 'w') as f:
                f.write(config)
    
    def start_nodes(self):
        """Start all 6 Redis nodes."""
        for port in self.ports:
            config_path = os.path.join(self.cluster_dir, str(port), "redis.conf")
            subprocess.Popen(
                ["redis-server", config_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        time.sleep(2)
        
        # Verify nodes are running
        for port in self.ports:
            result = subprocess.run(
                ["redis-cli", "-p", str(port), "ping"],
                capture_output=True, text=True
            )
            if "PONG" not in result.stdout:
                return False
        return True
    
    def create_cluster(self):
        """Initialize the cluster."""
        nodes = " ".join([f"127.0.0.1:{port}" for port in self.ports])
        cmd = f"redis-cli --cluster create {nodes} --cluster-replicas 1 --cluster-yes"
        
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        return result.returncode == 0
    
    def stop_existing(self):
        """Stop any existing Redis on our ports."""
        for port in self.ports:
            subprocess.run(
                ["redis-cli", "-p", str(port), "shutdown", "nosave"],
                capture_output=True
            )
        time.sleep(1)
    
    def setup(self):
        """Run full cluster setup."""
        print("\n=== Setting up Redis Cluster ===")
        print("Creating 6-node cluster:")
        print("  - 3 Master nodes (ports 7001, 7002, 7003) - store data")
        print("  - 3 Replica nodes (ports 7004, 7005, 7006) - backup copies")
        
        self.stop_existing()
        
        print("\n1. Creating config files...")
        self.create_config_files()
        
        print("2. Starting Redis nodes...")
        if not self.start_nodes():
            print("Failed to start nodes")
            return False
        
        print("3. Forming cluster with hash slot distribution...")
        print("   - Master 7001: slots 0-5460")
        print("   - Master 7002: slots 5461-10922")
        print("   - Master 7003: slots 10923-16383")
        if not self.create_cluster():
            print("Failed to create cluster")
            return False
        
        time.sleep(2)
        print("\n=== Cluster Ready ===")
        return True


if __name__ == "__main__":
    setup = RedisClusterSetup()
    if setup.setup():
        print("\nNext: python3 main.py")
    else:
        print("Setup failed")
