#!/usr/bin/env python3
"""
Graph Cache Administration Tool

This script provides administrative functions for managing the graph cache,
including viewing statistics, clearing cache entries, and monitoring performance.

Usage:
    python graph_cache_admin.py stats              # View cache statistics
    python graph_cache_admin.py clear <viz_id>     # Clear cache for specific visualization
    python graph_cache_admin.py clear-all          # Clear all cached graphs
    python graph_cache_admin.py monitor            # Monitor cache performance
    python graph_cache_admin.py info               # Show cache configuration info
"""

import argparse
import json
import time
import sys
import os
from typing import Dict, Any

from .graph_cache_manager import GraphCacheManager
from .graph_cache_utils import get_cache_stats

class GraphCacheAdmin:
    """Administrative interface for graph cache management"""
    
    def __init__(self):
        self.cache_manager = GraphCacheManager()
    
    def show_stats(self, viz_id: str = None) -> None:
        """Display cache statistics"""
        print("📊 Graph Cache Statistics")
        print("=" * 40)
        
        stats = get_cache_stats(viz_id)
        
        if 'error' in stats:
            print(f"❌ Error getting stats: {stats['error']}")
            return
        
        print(f"Total cached graphs: {stats.get('total_graphs', 0)}")
        
        if viz_id:
            print(f"Visualization ID: {viz_id}")
        else:
            print("All visualizations")
        
        if stats.get('sample_keys'):
            print(f"\nSample cache keys:")
            for key in stats['sample_keys'][:5]:
                print(f"  - {key}")
        
        if 'avg_memory_per_graph' in stats:
            avg_memory = stats['avg_memory_per_graph']
            total_memory = stats.get('total_memory_estimate', 0)
            print(f"\nMemory usage:")
            print(f"  Average per graph: {avg_memory:,} bytes ({avg_memory/1024:.1f} KB)")
            print(f"  Total estimated: {total_memory:,} bytes ({total_memory/1024/1024:.2f} MB)")
        
        # Show compression effectiveness
        if stats.get('total_graphs', 0) > 0:
            print(f"\nCache pattern: {stats.get('pattern', 'N/A')}")
    
    def clear_cache(self, viz_id: str) -> None:
        """Clear cache for a specific visualization"""
        print(f"🗑️  Clearing cache for visualization: {viz_id}")
        
        deleted = self.cache_manager.invalidate_all_graphs(viz_id)
        
        if deleted > 0:
            print(f"✅ Cleared {deleted} cache entries")
        else:
            print("ℹ️  No cache entries found for this visualization")
    
    def clear_all_cache(self) -> None:
        """Clear all cached graphs"""
        print("🗑️  Clearing ALL cached graphs...")
        
        # Get all graph keys
        all_keys = self.cache_manager._redis.keys("graph:*")
        
        if not all_keys:
            print("ℹ️  No cached graphs found")
            return
        
        # Confirm destructive operation
        print(f"⚠️  This will delete {len(all_keys)} cached graphs!")
        confirm = input("Type 'yes' to confirm: ").strip().lower()
        
        if confirm != 'yes':
            print("❌ Operation cancelled")
            return
        
        deleted = self.cache_manager._redis.delete(*all_keys)
        print(f"✅ Cleared {deleted} cache entries")
    
    def show_info(self) -> None:
        """Show cache configuration information"""
        print("ℹ️  Graph Cache Configuration")
        print("=" * 35)
        
        # Redis connection info
        redis_host = os.getenv("REDIS_SERVICE_HOST", "redis-cache")
        redis_port = os.getenv("REDIS_SERVICE_PORT", "6379")
        
        print(f"Redis Host: {redis_host}")
        print(f"Redis Port: {redis_port}")
        
        # Test Redis connection
        try:
            info = self.cache_manager._redis.info()
            print(f"Redis Version: {info.get('redis_version', 'Unknown')}")
            print(f"Redis Memory: {info.get('used_memory_human', 'Unknown')}")
            print(f"Redis Uptime: {info.get('uptime_in_seconds', 0)} seconds")
            print("✅ Redis connection: OK")
        except Exception as e:
            print(f"❌ Redis connection failed: {str(e)}")
        
        # Cache settings
        print(f"\nCache Settings:")
        print(f"  Default expiry: 7 days")
        print(f"  Compression: gzip enabled")
        print(f"  Key pattern: graph:<viz_id>:<param_hash>")
    
    def monitor_performance(self, duration: int = 60) -> None:
        """Monitor cache performance over time"""
        print(f"📈 Monitoring cache performance for {duration} seconds...")
        print("Press Ctrl+C to stop early")
        
        try:
            start_time = time.time()
            initial_stats = get_cache_stats()
            initial_graphs = initial_stats.get('total_graphs', 0)
            
            print(f"Initial cached graphs: {initial_graphs}")
            print("\nMonitoring... (showing updates every 10 seconds)")
            
            last_check = initial_graphs
            
            while time.time() - start_time < duration:
                time.sleep(10)
                
                current_stats = get_cache_stats()
                current_graphs = current_stats.get('total_graphs', 0)
                
                if current_graphs != last_check:
                    elapsed = int(time.time() - start_time)
                    change = current_graphs - last_check
                    print(f"[{elapsed:3d}s] Cached graphs: {current_graphs} ({change:+d})")
                    last_check = current_graphs
            
            final_stats = get_cache_stats()
            final_graphs = final_stats.get('total_graphs', 0)
            total_change = final_graphs - initial_graphs
            
            print(f"\n📊 Monitoring complete:")
            print(f"  Duration: {duration} seconds")
            print(f"  Initial graphs: {initial_graphs}")
            print(f"  Final graphs: {final_graphs}")
            print(f"  Net change: {total_change:+d}")
            
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
    
    def list_visualizations(self) -> None:
        """List all visualization IDs that have cached graphs"""
        print("📋 Cached Visualizations")
        print("=" * 25)
        
        # Get all graph keys and extract viz IDs
        all_keys = self.cache_manager._redis.keys("graph:*")
        
        if not all_keys:
            print("ℹ️  No cached graphs found")
            return
        
        viz_ids = set()
        for key in all_keys:
            # Key format: graph:<viz_id>:<param_hash>
            parts = key.split(":", 2)
            if len(parts) >= 3:
                viz_ids.add(parts[1])
        
        for viz_id in sorted(viz_ids):
            viz_stats = get_cache_stats(viz_id)
            count = viz_stats.get('total_graphs', 0)
            print(f"  {viz_id}: {count} cached graphs")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Graph Cache Administration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s stats                    # Show overall cache statistics
  %(prog)s stats commits-over-time  # Show stats for specific visualization
  %(prog)s clear commits-over-time  # Clear cache for specific visualization
  %(prog)s clear-all               # Clear all cached graphs
  %(prog)s list                    # List all cached visualizations
  %(prog)s monitor 120             # Monitor for 2 minutes
  %(prog)s info                    # Show configuration info
        """
    )
    
    parser.add_argument(
        'command',
        choices=['stats', 'clear', 'clear-all', 'monitor', 'info', 'list'],
        help='Administrative command to execute'
    )
    
    parser.add_argument(
        'target',
        nargs='?',
        help='Target visualization ID (for stats/clear) or duration in seconds (for monitor)'
    )
    
    args = parser.parse_args()
    
    try:
        admin = GraphCacheAdmin()
        
        if args.command == 'stats':
            admin.show_stats(args.target)
        
        elif args.command == 'clear':
            if not args.target:
                print("❌ Error: Visualization ID required for clear command")
                print("Usage: clear <viz_id>")
                sys.exit(1)
            admin.clear_cache(args.target)
        
        elif args.command == 'clear-all':
            admin.clear_all_cache()
        
        elif args.command == 'monitor':
            duration = 60  # default
            if args.target:
                try:
                    duration = int(args.target)
                except ValueError:
                    print(f"❌ Error: Invalid duration '{args.target}'. Must be a number.")
                    sys.exit(1)
            admin.monitor_performance(duration)
        
        elif args.command == 'info':
            admin.show_info()
        
        elif args.command == 'list':
            admin.list_visualizations()
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 