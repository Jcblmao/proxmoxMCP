"""
Output templates for Proxmox MCP resource types.
"""
from typing import Dict, List, Any
from .formatters import ProxmoxFormatters
from .theme import ProxmoxTheme
from .colors import ProxmoxColors
from .components import ProxmoxComponents

class ProxmoxTemplates:
    """Output templates for different Proxmox resource types."""
    
    @staticmethod
    def node_list(nodes: List[Dict[str, Any]]) -> str:
        """Template for node list output.
        
        Args:
            nodes: List of node data dictionaries
            
        Returns:
            Formatted node list string
        """
        result = [f"{ProxmoxTheme.RESOURCES['node']} Proxmox Nodes"]
        
        for node in nodes:
            # Get node status
            status = node.get("status", "unknown")
            
            # Get memory info
            memory = node.get("memory", {})
            memory_used = memory.get("used", 0)
            memory_total = memory.get("total", 0)
            memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
            
            # Format node info
            result.extend([
                "",  # Empty line between nodes
                f"{ProxmoxTheme.RESOURCES['node']} {node['node']}",
                f"  - Status: {status.upper()}",
                f"  - Uptime: {ProxmoxFormatters.format_uptime(node.get('uptime', 0))}",
                f"  - CPU Cores: {node.get('maxcpu', 'N/A')}",
                f"  - Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
                f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
            ])
            
            # Add disk usage if available
            disk = node.get("disk", {})
            if disk:
                disk_used = disk.get("used", 0)
                disk_total = disk.get("total", 0)
                disk_percent = (disk_used / disk_total * 100) if disk_total > 0 else 0
                result.append(
                    f"  - Disk: {ProxmoxFormatters.format_bytes(disk_used)} / "
                    f"{ProxmoxFormatters.format_bytes(disk_total)} ({disk_percent:.1f}%)"
                )
            
        return "\n".join(result)
    
    @staticmethod
    def node_status(node: str, status: Dict[str, Any]) -> str:
        """Template for detailed node status output.
        
        Args:
            node: Node name
            status: Node status data
            
        Returns:
            Formatted node status string
        """
        memory = status.get("memory", {})
        memory_used = memory.get("used", 0)
        memory_total = memory.get("total", 0)
        memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
        
        result = [
            f"{ProxmoxTheme.RESOURCES['node']} Node: {node}",
            f"  - Status: {status.get('status', 'unknown').upper()}",
            f"  - Uptime: {ProxmoxFormatters.format_uptime(status.get('uptime', 0))}",
            f"  - CPU Cores: {status.get('maxcpu', 'N/A')}",
            f"  - Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
            f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
        ]
        
        # Add disk usage if available
        disk = status.get("disk", {})
        if disk:
            disk_used = disk.get("used", 0)
            disk_total = disk.get("total", 0)
            disk_percent = (disk_used / disk_total * 100) if disk_total > 0 else 0
            result.append(
                f"  - Disk: {ProxmoxFormatters.format_bytes(disk_used)} / "
                f"{ProxmoxFormatters.format_bytes(disk_total)} ({disk_percent:.1f}%)"
            )
        
        return "\n".join(result)
    
    @staticmethod
    def vm_list(vms: List[Dict[str, Any]]) -> str:
        """Template for VM list output.
        
        Args:
            vms: List of VM data dictionaries
            
        Returns:
            Formatted VM list string
        """
        result = [f"{ProxmoxTheme.RESOURCES['vm']} Virtual Machines"]
        
        for vm in vms:
            memory = vm.get("memory", {})
            memory_used = memory.get("used", 0)
            memory_total = memory.get("total", 0)
            memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
            
            result.extend([
                "",  # Empty line between VMs
                f"{ProxmoxTheme.RESOURCES['vm']} {vm['name']} (ID: {vm['vmid']})",
                f"  - Status: {vm['status'].upper()}",
                f"  - Node: {vm['node']}",
                f"  - CPU Cores: {vm.get('cpus', 'N/A')}",
                f"  - Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
                f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
            ])
            
        return "\n".join(result)
    
    @staticmethod
    def storage_list(storage: List[Dict[str, Any]]) -> str:
        """Template for storage list output.
        
        Args:
            storage: List of storage data dictionaries
            
        Returns:
            Formatted storage list string
        """
        result = [f"{ProxmoxTheme.RESOURCES['storage']} Storage Pools"]
        
        for store in storage:
            used = store.get("used", 0)
            total = store.get("total", 0)
            percent = (used / total * 100) if total > 0 else 0
            
            result.extend([
                "",  # Empty line between storage pools
                f"{ProxmoxTheme.RESOURCES['storage']} {store['storage']}",
                f"  - Status: {store.get('status', 'unknown').upper()}",
                f"  - Type: {store['type']}",
                f"  - Usage: {ProxmoxFormatters.format_bytes(used)} / "
                f"{ProxmoxFormatters.format_bytes(total)} ({percent:.1f}%)"
            ])
            
        return "\n".join(result)
    
    @staticmethod
    def container_list(containers: List[Dict[str, Any]]) -> str:
        """Template for container list output.
        
        Args:
            containers: List of container data dictionaries
            
        Returns:
            Formatted container list string
        """
        if not containers:
            return f"{ProxmoxTheme.RESOURCES['container']} No containers found"
            
        result = [f"{ProxmoxTheme.RESOURCES['container']} Containers"]
        
        for container in containers:
            memory = container.get("memory", {})
            memory_used = memory.get("used", 0)
            memory_total = memory.get("total", 0)
            memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
            
            result.extend([
                "",  # Empty line between containers
                f"{ProxmoxTheme.RESOURCES['container']} {container['name']} (ID: {container['vmid']})",
                f"  - Status: {container['status'].upper()}",
                f"  - Node: {container['node']}",
                f"  - CPU Cores: {container.get('cpus', 'N/A')}",
                f"  - Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
                f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
            ])
            
        return "\n".join(result)

    @staticmethod
    def cluster_status(status: Dict[str, Any]) -> str:
        """Template for cluster status output.
        
        Args:
            status: Cluster status data
            
        Returns:
            Formatted cluster status string
        """
        result = [f"{ProxmoxTheme.SECTIONS['configuration']} Proxmox Cluster"]
        
        # Basic cluster info
        result.extend([
            "",
            f"  - Name: {status.get('name', 'N/A')}",
            f"  - Quorum: {'OK' if status.get('quorum') else 'NOT OK'}",
            f"  - Nodes: {status.get('nodes', 0)}",
        ])
        
        # Add resource count if available
        resources = status.get('resources', [])
        if resources:
            result.append(f"  - Resources: {len(resources)}")

        return "\n".join(result)

    @staticmethod
    def zfs_pool_list(pools: List[Dict[str, Any]]) -> str:
        """Template for ZFS pool list output.

        Args:
            pools: List of ZFS pool data dictionaries

        Returns:
            Formatted ZFS pool list string
        """
        if not pools:
            return f"{ProxmoxTheme.RESOURCES['zfs']} No ZFS pools found"

        result = [f"{ProxmoxTheme.RESOURCES['zfs']} ZFS Storage Pools"]

        for pool in pools:
            health = pool.get("health", "UNKNOWN")
            health_icon = "🟢" if health == "ONLINE" else "🟡" if health == "DEGRADED" else "🔴"

            size = pool.get("size", 0)
            alloc = pool.get("alloc", 0)
            free = pool.get("free", 0)
            frag = pool.get("frag", 0)
            dedup = pool.get("dedup", 1.0)

            # Calculate percentage
            percent = (alloc / size * 100) if size > 0 else 0

            result.extend([
                "",
                f"{ProxmoxTheme.RESOURCES['zfs']} {pool['name']} ({pool.get('node', 'unknown')})",
                f"  - Health: {health_icon} {health}",
                f"  - Size: {ProxmoxFormatters.format_bytes(size)}",
                f"  - Used: {ProxmoxFormatters.format_bytes(alloc)} ({percent:.1f}%)",
                f"  - Free: {ProxmoxFormatters.format_bytes(free)}",
                f"  - Fragmentation: {frag}%",
            ])

            if dedup and dedup != 1.0:
                result.append(f"  - Dedup Ratio: {dedup:.2f}x")

        return "\n".join(result)

    @staticmethod
    def zfs_pool_detail(pool: Dict[str, Any]) -> str:
        """Template for detailed ZFS pool status output.

        Args:
            pool: ZFS pool detail data

        Returns:
            Formatted ZFS pool detail string
        """
        health = pool.get("health", "UNKNOWN")
        health_icon = "🟢" if health == "ONLINE" else "🟡" if health == "DEGRADED" else "🔴"

        result = [
            f"{ProxmoxTheme.RESOURCES['zfs']} ZFS Pool: {pool.get('name', 'unknown')}",
            f"  - Node: {pool.get('node', 'unknown')}",
            f"  - Health: {health_icon} {health}",
            f"  - State: {pool.get('state', 'UNKNOWN')}",
        ]

        # Add scan info if available
        scan = pool.get("scan", {})
        if scan:
            result.append(f"  - Last Scan: {scan.get('function', 'none')} - {scan.get('state', 'unknown')}")

        # Add errors
        errors = pool.get("errors", "No known data errors")
        result.append(f"  - Errors: {errors}")

        # Add disk layout
        children = pool.get("children", [])
        if children:
            result.append("")
            result.append("  Disk Layout:")
            for child in children:
                child_name = child.get("name", "unknown")
                child_state = child.get("state", "UNKNOWN")
                state_icon = "🟢" if child_state == "ONLINE" else "🟡" if child_state == "DEGRADED" else "🔴"
                result.append(f"    - {child_name}: {state_icon} {child_state}")

                # Nested children (for mirrors, raidz)
                for subchild in child.get("children", []):
                    sub_name = subchild.get("name", "unknown")
                    sub_state = subchild.get("state", "UNKNOWN")
                    sub_icon = "🟢" if sub_state == "ONLINE" else "🟡" if sub_state == "DEGRADED" else "🔴"
                    result.append(f"      - {sub_name}: {sub_icon} {sub_state}")

        # Add raw status output if available (fallback when structured data unavailable)
        raw_status = pool.get("raw_status")
        if raw_status:
            result.append("")
            result.append("  Raw Pool Status:")
            for line in raw_status.split('\n'):
                if line.strip():
                    result.append(f"    {line}")

        return "\n".join(result)

    @staticmethod
    def zfs_datasets(datasets: List[Dict[str, Any]]) -> str:
        """Template for ZFS datasets output.

        Args:
            datasets: List of ZFS dataset data dictionaries

        Returns:
            Formatted ZFS datasets string
        """
        if not datasets:
            return f"{ProxmoxTheme.RESOURCES['zfs']} No ZFS datasets found"

        result = [f"{ProxmoxTheme.RESOURCES['zfs']} ZFS Datasets"]

        for ds in datasets:
            used = ds.get("used", 0)
            avail = ds.get("avail", 0)

            result.extend([
                "",
                f"  {ProxmoxTheme.RESOURCES['storage']} {ds.get('name', 'unknown')}",
                f"     - Type: {ds.get('type', 'filesystem')}",
                f"     - Used: {ProxmoxFormatters.format_bytes(used)}",
                f"     - Available: {ProxmoxFormatters.format_bytes(avail)}",
                f"     - Mountpoint: {ds.get('mountpoint', 'N/A')}",
            ])

        return "\n".join(result)

    @staticmethod
    def disk_list(disks: List[Dict[str, Any]]) -> str:
        """Template for disk list output.

        Args:
            disks: List of disk data dictionaries

        Returns:
            Formatted disk list string
        """
        if not disks:
            return f"{ProxmoxTheme.RESOURCES['disk']} No disks found"

        result = [f"{ProxmoxTheme.RESOURCES['disk']} Disks"]

        for disk in disks:
            health = disk.get("health", "UNKNOWN")
            health_icon = "🟢" if health == "PASSED" or health == "OK" else "🟡" if health == "UNKNOWN" else "🔴"

            disk_type = disk.get("type", "unknown")
            type_icon = "⚡" if disk_type == "ssd" else "💿"

            size = disk.get("size", 0)
            used = disk.get("used", "unused")

            result.extend([
                "",
                f"  {type_icon} {disk.get('devpath', 'unknown')}",
                f"     - Size: {ProxmoxFormatters.format_bytes(size)}",
                f"     - Model: {disk.get('model', 'N/A')}",
                f"     - Serial: {disk.get('serial', 'N/A')}",
                f"     - Health: {health_icon} {health}",
                f"     - Usage: {used}",
            ])

            # Add wear level for SSDs
            wearout = disk.get("wearout", "N/A")
            if wearout != "N/A" and disk_type == "ssd":
                result.append(f"     - Wear Level: {wearout}%")

        return "\n".join(result)

    @staticmethod
    def storage_usage(storages: List[Dict[str, Any]]) -> str:
        """Template for detailed storage usage breakdown.

        Args:
            storages: List of storage usage data dictionaries

        Returns:
            Formatted storage usage string
        """
        if not storages:
            return f"{ProxmoxTheme.RESOURCES['storage']} No storage data found"

        result = [f"{ProxmoxTheme.RESOURCES['storage']} Storage Usage Breakdown"]

        for store in storages:
            total = store.get("total", 0)
            used = store.get("used", 0)
            avail = store.get("available", 0)
            percent = (used / total * 100) if total > 0 else 0

            result.extend([
                "",
                f"{ProxmoxTheme.RESOURCES['storage']} {store['storage']} ({store.get('type', 'unknown')})",
                f"  Total: {ProxmoxFormatters.format_bytes(total)}",
                f"  Used: {ProxmoxFormatters.format_bytes(used)} ({percent:.1f}%)",
                f"  Available: {ProxmoxFormatters.format_bytes(avail)}",
                f"  Volumes: {store.get('volume_count', 0)}",
            ])

            # List top volumes by size
            volumes = store.get("volumes", [])
            if volumes:
                result.append("")
                result.append("  Top Space Consumers:")
                # Show top 10 or fewer
                for vol in volumes[:10]:
                    size = vol.get("size", 0)
                    vmid = vol.get("vmid")
                    content = vol.get("content", "unknown")
                    volid = vol.get("volid", "unknown")

                    # Extract just the volume name from volid for cleaner display
                    vol_name = volid.split("/")[-1] if "/" in volid else volid.split(":")[-1]

                    vmid_str = f" (VM {vmid})" if vmid else ""
                    result.append(
                        f"    - {vol_name}{vmid_str}: {ProxmoxFormatters.format_bytes(size)} [{content}]"
                    )

                if len(volumes) > 10:
                    result.append(f"    ... and {len(volumes) - 10} more volumes")

        return "\n".join(result)
