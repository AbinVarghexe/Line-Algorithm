import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def project(x, y, z, f=2.0):
    """3D to 2D perspective projection using simple focal length division."""
    if z <= 0.1: return None, None
    factor = f / z
    return x * factor, y * factor

def create_quad(ax, x, y, z, w, h, color, f=2.0):
    """Creates a 2D polygon from 3D rectangle coordinates on the given axes."""
    points = [
        project(x - w/2, y, z, f), project(x + w/2, y, z, f),
        project(x + w/2, y + h, z, f), project(x - w/2, y + h, z, f)
    ]
    if any(p[0] is None for p in points): return None
    poly = patches.Polygon(points, closed=True, color=color, ec='#333', lw=0.5)
    ax.add_patch(poly)
    return poly

def bresenham_line(x0, y0, x1, y1):
    """Bresenham's Line Drawing Algorithm — returns list of (x, y) pixel points."""
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return points

def draw_bresenham_line(ax, p1, p2, color='white', linewidth=2, alpha=1.0):
    """Draw a line between two 2D points using Bresenham's algorithm for visualization."""
    if p1[0] is None or p2[0] is None:
        return
    # Scale to pixel-like grid for Bresenham, then scale back
    scale = 200
    x0, y0 = int(p1[0] * scale), int(p1[1] * scale)
    x1, y1 = int(p2[0] * scale), int(p2[1] * scale)
    pts = bresenham_line(x0, y0, x1, y1)
    if pts:
        xs = [p[0] / scale for p in pts]
        ys = [p[1] / scale for p in pts]
        ax.plot(xs, ys, color=color, linewidth=linewidth, alpha=alpha, solid_capstyle='round')

def main():
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('#87CEEB')
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-1.2, 2.2); ax.set_aspect('equal')
    ax.axis('off')

    # Sky and Ground
    ax.set_facecolor('#87CEEB')
    ax.fill_between([-4, 4], -2, 0, color='#4CAF50')  # Green grass

    # Sun with glow
    ax.add_patch(patches.Circle((1.5, 1.7), 0.35, color='#FFD700', alpha=0.9))
    ax.add_patch(patches.Circle((1.5, 1.7), 0.5, color='#FFD700', alpha=0.2))

    # Clouds
    cloud_data = [
        (-1.2, 1.4, 0.45, 0.2), (-0.9, 1.5, 0.35, 0.17), (-1.5, 1.5, 0.35, 0.17),
        (0.3, 1.1, 0.5, 0.22), (0.0, 1.2, 0.35, 0.16), (0.6, 1.2, 0.35, 0.16),
    ]
    for cx, cy, rx, ry in cloud_data:
        ax.add_patch(patches.Ellipse((cx, cy), rx*2, ry*2, color='white', alpha=0.85))

    # Mountains in background
    mountain_data = [(-1.5, 1.8), (-0.3, 2.2), (0.8, 1.9), (2.0, 1.6)]
    for mx, mh in mountain_data:
        tri = patches.Polygon(
            [(mx - 0.8, 0), (mx + 0.8, 0), (mx, mh * 0.4)],
            color='#78909C', alpha=0.5, ec='none'
        )
        ax.add_patch(tri)

    focal_length = 2.0

    # --- Road surface (dark asphalt) ---
    road_z = np.linspace(1, 50, 80)
    road_left_pts = [project(-1.5, -1, z, focal_length) for z in road_z]
    road_right_pts = [project(1.5, -1, z, focal_length) for z in road_z]

    # Draw filled road polygon
    left_valid = [(p, z) for p, z in zip(road_left_pts, road_z) if p[0] is not None]
    right_valid = [(p, z) for p, z in zip(road_right_pts, road_z) if p[0] is not None]
    if left_valid and right_valid:
        road_poly_pts = [p for p, z in left_valid] + [p for p, z in reversed(right_valid)]
        road = patches.Polygon(road_poly_pts, closed=True, color='#424242', ec='none')
        ax.add_patch(road)

    # --- Road edges using Bresenham's Line Algorithm ---
    for i in range(len(road_z) - 1):
        pl1 = project(-1.5, -1, road_z[i], focal_length)
        pl2 = project(-1.5, -1, road_z[i+1], focal_length)
        pr1 = project(1.5, -1, road_z[i], focal_length)
        pr2 = project(1.5, -1, road_z[i+1], focal_length)
        draw_bresenham_line(ax, pl1, pl2, color='white', linewidth=2.5, alpha=0.9)
        draw_bresenham_line(ax, pr1, pr2, color='white', linewidth=2.5, alpha=0.9)

    # --- Dashed center line using Bresenham ---
    for z in np.arange(1, 50, 2):
        p1 = project(0, -1, z, focal_length)
        p2 = project(0, -1, z + 1, focal_length)
        if p1[0] is not None and p2[0] is not None:
            lw = max(1, 3 / z)
            draw_bresenham_line(ax, p1, p2, color='#FFD54F', linewidth=lw, alpha=0.9)

    # --- Lane markings (dashed) ---
    for lane_x in [-0.75, 0.75]:
        for z in np.arange(1, 50, 3):
            p1 = project(lane_x, -1, z, focal_length)
            p2 = project(lane_x, -1, z + 1.2, focal_length)
            if p1[0] is not None and p2[0] is not None:
                lw = max(0.8, 2 / z)
                draw_bresenham_line(ax, p1, p2, color='white', linewidth=lw, alpha=0.5)

    # --- Lampposts along the road ---
    for z in range(4, 40, 8):
        for side_x in [-2.0, 2.0]:
            # Pole
            create_quad(ax, side_x, -1, z, 0.08, 1.8, '#616161', f=focal_length)
            # Light fixture
            create_quad(ax, side_x, 0.8, z, 0.25, 0.1, '#FFF176', f=focal_length)

    # --- Trees alongside road ---
    for z in range(6, 45, 7):
        for x in [-2.8, 2.8]:
            # Trunk
            create_quad(ax, x, -1, z, 0.15, 0.6, '#5D4037', f=focal_length)
            # Round canopy (multiple ellipses)
            for dx_off, dy_off, r in [(-0.15, 0.1, 0.3), (0.15, 0.1, 0.3), (0, 0.3, 0.35)]:
                cp = project(x + dx_off, -0.4 + dy_off, z, focal_length)
                if cp[0] is not None:
                    size = r * focal_length / z
                    ax.add_patch(patches.Circle(cp, size, color='#2E7D32', ec='#1B5E20', lw=0.3, alpha=0.9))

    # --- Static parked car for reference ---
    def draw_car(ax, cx, cy, z, body_color='#E53935', f=2.0):
        """Draw a simple car at position (cx, cy) at depth z."""
        # Body
        create_quad(ax, cx, cy, z, 0.6, 0.3, body_color, f=f)
        # Roof / cabin
        create_quad(ax, cx, cy + 0.3, z, 0.4, 0.2, '#1565C0', f=f)
        # Windshield
        create_quad(ax, cx, cy + 0.3, z - 0.1, 0.38, 0.18, '#81D4FA', f=f)
        # Wheels
        for wx in [-0.25, 0.25]:
            create_quad(ax, cx + wx, cy - 0.05, z, 0.12, 0.12, '#212121', f=f)
        # Headlights
        create_quad(ax, cx - 0.22, cy + 0.15, z - 0.15, 0.08, 0.08, '#FFF176', f=f)
        create_quad(ax, cx + 0.22, cy + 0.15, z - 0.15, 0.08, 0.08, '#FFF176', f=f)

    # A few static cars at different depths
    draw_car(ax, -0.5, -1, 8, body_color='#E53935')
    draw_car(ax, 0.5, -1, 14, body_color='#1976D2')
    draw_car(ax, -0.4, -1, 22, body_color='#FFC107')

    # Save
    output_file = 'road_perspective.png'
    plt.savefig(output_file, facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.1, dpi=150)
    print(f"Visualization saved to {output_file}")

if __name__ == "__main__":
    main()
