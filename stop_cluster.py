#!/usr/bin/env python3
"""
Stop Redis Cluster
"""

import subprocess
import shutil
import os


def stop_cluster():
    """Stop all Redis cluster nodes."""
    print("Stopping Redis Cluster...")
    
    ports = [7001, 7002, 7003, 7004, 7005, 7006]
    
    for port in ports:
        subprocess.run(
            ["redis-cli", "-p", str(port), "shutdown", "nosave"],
            capture_output=True
        )
    
    # Clean up cluster directory
    cluster_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "redis-cluster")
    if os.path.exists(cluster_dir):
        shutil.rmtree(cluster_dir)
    
    print("Cluster stopped")


if __name__ == "__main__":
    stop_cluster()
