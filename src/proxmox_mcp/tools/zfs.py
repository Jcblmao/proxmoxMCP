"""
ZFS storage pool tools for Proxmox MCP.

This module provides tools for managing and monitoring ZFS storage pools:
- Listing all ZFS pools across nodes
- Retrieving detailed pool information including:
  * Pool health status
  * Disk composition and layout
  * Usage statistics (used, available, fragmentation)
  * Dataset information
- Listing ZFS datasets with usage details

The tools implement fallback mechanisms for scenarios where
detailed ZFS information might be temporarily unavailable.
"""
from typing import List, Optional
from mcp.types import TextContent as Content
from .base import ProxmoxTool


class ZFSTools(ProxmoxTool):
    """Tools for managing Proxmox ZFS storage pools.

    Provides functionality for:
    - Retrieving ZFS pool information across cluster nodes
    - Monitoring pool health and status
    - Tracking pool utilization and capacity
    - Viewing ZFS datasets and their usage

    Implements fallback mechanisms for scenarios where detailed
    ZFS information might be temporarily unavailable.
    """

    def list_zfs_pools(self, node: Optional[str] = None) -> List[Content]:
        """List ZFS storage pools on Proxmox nodes.

        Retrieves comprehensive information for each ZFS pool including:
        - Pool name and health status
        - Size, allocated space, and free space
        - Fragmentation percentage
        - Deduplication ratio
        - Disk composition

        Args:
            node: Optional node name to filter. If not provided,
                  lists pools from all nodes.

        Returns:
            List of Content objects containing formatted ZFS pool information:
            {
                "name": "pool-name",
                "node": "node-name",
                "health": "ONLINE/DEGRADED/FAULTED",
                "size": bytes,
                "alloc": bytes,
                "free": bytes,
                "frag": percentage,
                "dedup": ratio
            }

        Raises:
            RuntimeError: If the ZFS pool query fails
        """
        try:
            pools = []

            # Get list of nodes to query
            if node:
                nodes_to_query = [{"node": node}]
            else:
                nodes_to_query = self.proxmox.nodes.get()

            for node_info in nodes_to_query:
                node_name = node_info["node"]
                try:
                    # Query ZFS pools on this node
                    zfs_pools = self.proxmox.nodes(node_name).disks.zfs.get()

                    for pool in zfs_pools:
                        pool_data = {
                            "name": pool.get("name", "unknown"),
                            "node": node_name,
                            "health": pool.get("health", "UNKNOWN"),
                            "size": pool.get("size", 0),
                            "alloc": pool.get("alloc", 0),
                            "free": pool.get("free", 0),
                            "frag": pool.get("frag", 0),
                            "dedup": pool.get("dedup", 1.0),
                        }
                        pools.append(pool_data)

                except Exception as node_error:
                    self.logger.warning(
                        "Could not query ZFS pools on node %s: %s",
                        node_name,
                        node_error,
                    )
                    continue

            return self._format_response(pools, "zfs_pools")
        except Exception as e:
            self._handle_error("list ZFS pools", e)

    def get_zfs_pool_status(self, node: str, pool_name: str) -> List[Content]:
        """Get detailed status of a specific ZFS pool.

        Retrieves detailed information for a ZFS pool including:
        - Health status and state
        - Disk layout (mirror, raidz, etc.)
        - Individual disk status
        - Scan/scrub status
        - Errors if any

        Args:
            node: Node name where the pool is located
            pool_name: Name of the ZFS pool

        Returns:
            List of Content objects containing detailed pool status

        Raises:
            RuntimeError: If the pool status query fails
            ValueError: If the pool is not found
        """
        try:
            pool_detail = self.proxmox.nodes(node).disks.zfs(pool_name).get()

            # Debug: Log the actual API response type and content
            self.logger.debug(
                "ZFS pool detail response - type: %s, value: %r",
                type(pool_detail).__name__,
                pool_detail,
            )

            # Handle None response
            if pool_detail is None:
                self.logger.warning(
                    "ZFS pool detail returned None for %s/%s", node, pool_name
                )
                result = {
                    "name": pool_name,
                    "node": node,
                    "health": "UNKNOWN",
                    "state": "API returned no data",
                    "scan": {},
                    "action": None,
                    "status": None,
                    "errors": "No data returned from API",
                    "children": [],
                }
            # Handle string response (raw zpool status output)
            elif isinstance(pool_detail, str):
                self.logger.debug("ZFS pool detail is string, parsing health...")
                # Parse health from raw output if possible
                health = "UNKNOWN"
                if "ONLINE" in pool_detail:
                    health = "ONLINE"
                elif "DEGRADED" in pool_detail:
                    health = "DEGRADED"
                elif "FAULTED" in pool_detail:
                    health = "FAULTED"

                result = {
                    "name": pool_name,
                    "node": node,
                    "health": health,
                    "state": "See raw output",
                    "scan": {},
                    "action": None,
                    "status": None,
                    "errors": "Check raw output",
                    "children": [],
                    "raw_status": pool_detail,
                }
            # Handle dict response (expected structured data)
            elif isinstance(pool_detail, dict):
                self.logger.debug("ZFS pool detail is dict, extracting fields...")
                result = {
                    "name": pool_name,
                    "node": node,
                    "health": pool_detail.get("health", "UNKNOWN"),
                    "state": pool_detail.get("state", "UNKNOWN"),
                    "scan": pool_detail.get("scan", {}),
                    "action": pool_detail.get("action", None),
                    "status": pool_detail.get("status", None),
                    "errors": pool_detail.get("errors", "No known data errors"),
                    "children": pool_detail.get("children", []),
                }
            # Handle unexpected types (list, etc.)
            else:
                self.logger.error(
                    "Unexpected ZFS pool detail type for %s/%s: %s - %r",
                    node,
                    pool_name,
                    type(pool_detail).__name__,
                    pool_detail,
                )
                result = {
                    "name": pool_name,
                    "node": node,
                    "health": "UNKNOWN",
                    "state": f"Unexpected type: {type(pool_detail).__name__}",
                    "scan": {},
                    "action": None,
                    "status": None,
                    "errors": f"API returned unexpected type: {type(pool_detail).__name__}",
                    "children": [],
                    "raw_status": str(pool_detail),
                }

            self.logger.debug("ZFS pool result: %r", result)
            return self._format_response(result, "zfs_pool_detail")
        except Exception as e:
            self._handle_error(f"get ZFS pool status for {pool_name}", e)

    def list_zfs_datasets(self, node: str, pool_name: Optional[str] = None) -> List[Content]:
        """List ZFS datasets on a node.

        Retrieves information about ZFS datasets including:
        - Dataset name and type
        - Used space and referenced space
        - Available space
        - Mount point
        - Compression ratio

        Args:
            node: Node name to query
            pool_name: Optional pool name to filter datasets

        Returns:
            List of Content objects containing ZFS dataset information

        Raises:
            RuntimeError: If the dataset query fails
        """
        try:
            # Use the Proxmox API to get dataset information
            # Note: Proxmox API may not expose all ZFS dataset info directly
            # We'll get what's available through the disks/zfs endpoint
            datasets = []

            zfs_pools = self.proxmox.nodes(node).disks.zfs.get()

            for pool in zfs_pools:
                if pool_name and pool.get("name") != pool_name:
                    continue

                pool_info = {
                    "name": pool.get("name", "unknown"),
                    "type": "filesystem",
                    "used": pool.get("alloc", 0),
                    "avail": pool.get("free", 0),
                    "refer": pool.get("alloc", 0),
                    "mountpoint": f"/{pool.get('name', 'unknown')}",
                }
                datasets.append(pool_info)

            return self._format_response(datasets, "zfs_datasets")
        except Exception as e:
            self._handle_error("list ZFS datasets", e)

    def get_disk_list(self, node: str, include_partitions: bool = False) -> List[Content]:
        """List all disks on a node.

        Retrieves information about all disks including:
        - Device path
        - Size
        - Serial number
        - Type (ssd/hdd)
        - Health status
        - Current usage (ZFS pool member, etc.)

        Args:
            node: Node name to query
            include_partitions: Whether to include partition information

        Returns:
            List of Content objects containing disk information

        Raises:
            RuntimeError: If the disk query fails
        """
        try:
            disk_list = self.proxmox.nodes(node).disks.list.get(
                **{"include-partitions": 1 if include_partitions else 0}
            )

            disks = []
            for disk in disk_list:
                disk_info = {
                    "devpath": disk.get("devpath", "unknown"),
                    "size": disk.get("size", 0),
                    "serial": disk.get("serial", "N/A"),
                    "type": disk.get("type", "unknown"),
                    "health": disk.get("health", "UNKNOWN"),
                    "model": disk.get("model", "N/A"),
                    "vendor": disk.get("vendor", "N/A"),
                    "rpm": disk.get("rpm", 0),
                    "wearout": disk.get("wearout", "N/A"),
                    "used": disk.get("used", "unused"),
                }
                disks.append(disk_info)

            return self._format_response(disks, "disks")
        except Exception as e:
            self._handle_error("list disks", e)

    def get_storage_usage(self, node: str, storage: Optional[str] = None) -> List[Content]:
        """Get detailed storage usage breakdown.

        Shows what's consuming space on storage pools, including:
        - VM/container disk images and their sizes
        - Snapshots and their space consumption
        - Available space per storage

        Args:
            node: Node name to query
            storage: Optional specific storage to query (all if not specified)

        Returns:
            List of Content objects with detailed space usage

        Raises:
            RuntimeError: If the storage query fails
        """
        try:
            usage_data = []

            # Get storage list for this node
            storages = self.proxmox.nodes(node).storage.get()

            for store in storages:
                if storage and store["storage"] != storage:
                    continue

                store_name = store["storage"]

                # Get content listing (shows all volumes/images)
                try:
                    content = self.proxmox.nodes(node).storage(store_name).content.get()

                    # Get storage status for total/used info
                    try:
                        status = self.proxmox.nodes(node).storage(store_name).status.get()
                        total = status.get("total", 0)
                        used = status.get("used", 0)
                        avail = status.get("avail", 0)
                    except Exception:
                        total = used = avail = 0

                    # Group by type and calculate sizes
                    volumes = []
                    for item in content:
                        volumes.append({
                            "volid": item.get("volid", "unknown"),
                            "format": item.get("format", "unknown"),
                            "size": item.get("size", 0),
                            "vmid": item.get("vmid"),
                            "content": item.get("content", "unknown"),
                            "ctime": item.get("ctime"),
                        })

                    # Sort by size descending
                    volumes.sort(key=lambda x: x["size"], reverse=True)

                    usage_data.append({
                        "storage": store_name,
                        "type": store.get("type", "unknown"),
                        "total": total,
                        "used": used,
                        "available": avail,
                        "volumes": volumes,
                        "volume_count": len(volumes),
                    })
                except Exception as e:
                    self.logger.warning(f"Could not get content for {store_name}: {e}")
                    continue

            return self._format_response(usage_data, "storage_usage")
        except Exception as e:
            self._handle_error("get storage usage", e)
