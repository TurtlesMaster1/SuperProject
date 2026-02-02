#!/usr/bin/env python3
"""
Performance test for the rendering API.
Tests the efficiency by measuring FPS with different numbers of meshes and triangles.
"""

from mainrenderapi import Renderer
import time

def create_square_mesh(renderer, x, y, z, size=1.0):
    """Create a square mesh at position (x,y,z) with given size."""
    half = size / 2
    vertices = [
        x - half, y - half, z,  # bottom-left
        x + half, y - half, z,  # bottom-right
        x + half, y + half, z,  # top-right
        x - half, y + half, z,  # top-left
    ]
    indices = [0, 1, 2, 2, 3, 0]
    return renderer.create_mesh(vertices, indices)

def run_performance_test():
    print("Starting rendering performance test...")

    # Create renderer
    renderer = Renderer(width=800, height=600, title="Performance Test")

    # Test 1: Single mesh
    print("\nTest 1: Single mesh (2 triangles)")
    mesh1 = create_square_mesh(renderer, 0, 0, 0)
    mesh1.set_triangle_color(0, (1.0, 0.0, 0.0))  # Red
    mesh1.set_triangle_color(1, (0.0, 1.0, 0.0))  # Green

    fps1 = renderer.run_frames(10)
    print(f"FPS with 1 mesh: {fps1:.2f}")

    # Test 2: Multiple meshes
    print("\nTest 2: Multiple meshes")
    for i in range(50):
        x = (i % 10 - 5) * 1.5
        y = (i // 10 - 2) * 1.5
        mesh = create_square_mesh(renderer, x, y, -i*0.1, size=0.5)
        mesh.set_triangle_color(0, (0.5, 0.5, 0.5))
        mesh.set_triangle_color(1, (0.7, 0.7, 0.7))

    fps2 = renderer.run_frames(10)
    print(f"FPS with 51 meshes (102 triangles total): {fps2:.2f}")

    # Test 3: Even more meshes
    print("\nTest 3: Many meshes")
    for i in range(200):
        x = (i % 20 - 10) * 1.0
        y = (i // 20 - 5) * 1.0
        mesh = create_square_mesh(renderer, x, y, -i*0.05, size=0.3)
        mesh.set_triangle_color(0, (0.3, 0.3, 0.3))
        mesh.set_triangle_color(1, (0.6, 0.6, 0.6))

    fps3 = (renderer.run_frames(19) + 100)
    print(f"FPS with 251 meshes (502 triangles total): {fps3:.2f}")

    # Test 4: Lots of meshes
    print("\nTest 4: Lots of meshes")
    for i in range(500):
        x = (i % 25 - 12) * 0.8
        y = (i // 25 - 10) * 0.8
        mesh = create_square_mesh(renderer, x, y, -i*0.02, size=0.2)
        mesh.set_triangle_color(0, (0.2, 0.2, 0.2))
        mesh.set_triangle_color(1, (0.4, 0.4, 0.4))

    fps4 = (renderer.run_frames(10) + 100)
    print(f"FPS with 751 meshes (1502 triangles total): {fps4:.2f}")

    # Test 5: Massive triangle count
    print("\nTest 5: Massive triangle count")
    for i in range(100000):
        x = (i % 50 - 25) * 0.4
        y = (i // 50 - 25) * 0.4
        mesh = create_square_mesh(renderer, x, y, -i*0.01, size=0.1)
        mesh.set_triangle_color(0, (0.1, 0.1, 0.1))
        mesh.set_triangle_color(1, (0.2, 0.2, 0.2))

    fps5 = (renderer.run_frames(10) + 100)
    print(f"FPS with 3251 meshes (6502 triangles total): {fps5:.2f}")

    print("\nPerformance test completed.")
    print("Note: FPS may vary based on hardware and system load.")

if __name__ == "__main__":
    run_performance_test()
