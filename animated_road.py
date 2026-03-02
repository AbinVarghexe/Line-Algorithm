import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import numpy as np

# ============================================================
#  Road Perspective Animation with Cars
#  Uses: Line Drawing Algorithms (Bresenham's) & Projection
# ============================================================

FOCAL_LENGTH = 2.0
fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor('#87CEEB')
ax.set_xlim(-2.5, 2.5); ax.set_ylim(-1.2, 2.2); ax.set_aspect('equal')
ax.axis('off')

# ─── Projection Functions ───────────────────────────────────

def project(x, y, z):
    """3D to 2D perspective projection."""
    if z <= 0.1: return None, None
    f = FOCAL_LENGTH / z
    return x * f, y * f

def create_quad(x, y, z, w, h, color):
    """Create a projected quadrilateral polygon from 3D rect coords."""
    points = [
        project(x - w/2, y, z), project(x + w/2, y, z),
        project(x + w/2, y + h, z), project(x - w/2, y + h, z)
    ]
    if any(p[0] is None for p in points): return None
    return patches.Polygon(points, closed=True, color=color, ec='#333', lw=0.5)

def bresenham_line(x0, y0, x1, y1):
    """Bresenham's Line Drawing Algorithm — returns list of (x, y) integer points."""
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
    """Draw a line between two projected 2D points using Bresenham's algorithm."""
    if p1[0] is None or p2[0] is None:
        return
    scale = 200
    x0, y0 = int(p1[0] * scale), int(p1[1] * scale)
    x1, y1 = int(p2[0] * scale), int(p2[1] * scale)
    pts = bresenham_line(x0, y0, x1, y1)
    if pts:
        xs = [p[0] / scale for p in pts]
        ys = [p[1] / scale for p in pts]
        ax.plot(xs, ys, color=color, linewidth=linewidth, alpha=alpha, solid_capstyle='round')

# ─── Static Scenery ─────────────────────────────────────────

# Sky & Ground
ax.set_facecolor('#87CEEB')
ax.fill_between([-4, 4], -2, 0, color='#4CAF50')

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

# Mountains
mountain_data = [(-1.5, 1.8), (-0.3, 2.2), (0.8, 1.9), (2.0, 1.6)]
for mx, mh in mountain_data:
    tri = patches.Polygon(
        [(mx - 0.8, 0), (mx + 0.8, 0), (mx, mh * 0.4)],
        color='#78909C', alpha=0.5, ec='none'
    )
    ax.add_patch(tri)

# ─── Road Surface ───────────────────────────────────────────

road_z = np.linspace(1, 50, 80)
road_left_pts = [project(-1.5, -1, z) for z in road_z]
road_right_pts = [project(1.5, -1, z) for z in road_z]

left_valid = [(p, z) for p, z in zip(road_left_pts, road_z) if p[0] is not None]
right_valid = [(p, z) for p, z in zip(road_right_pts, road_z) if p[0] is not None]
if left_valid and right_valid:
    road_poly_pts = [p for p, z in left_valid] + [p for p, z in reversed(right_valid)]
    road = patches.Polygon(road_poly_pts, closed=True, color='#424242', ec='none')
    ax.add_patch(road)

# Road edges (Bresenham)
for i in range(len(road_z) - 1):
    pl1 = project(-1.5, -1, road_z[i])
    pl2 = project(-1.5, -1, road_z[i+1])
    pr1 = project(1.5, -1, road_z[i])
    pr2 = project(1.5, -1, road_z[i+1])
    draw_bresenham_line(ax, pl1, pl2, color='white', linewidth=2.5, alpha=0.9)
    draw_bresenham_line(ax, pr1, pr2, color='white', linewidth=2.5, alpha=0.9)

# ─── Dashed center & lane lines (static - will scroll via offset) ───
# These are drawn in static; the animation handles the car movement.
for z in np.arange(1, 50, 2):
    p1 = project(0, -1, z)
    p2 = project(0, -1, z + 1)
    if p1[0] is not None and p2[0] is not None:
        lw = max(1, 3 / z)
        draw_bresenham_line(ax, p1, p2, color='#FFD54F', linewidth=lw, alpha=0.9)

for lane_x in [-0.75, 0.75]:
    for z in np.arange(1, 50, 3):
        p1 = project(lane_x, -1, z)
        p2 = project(lane_x, -1, z + 1.2)
        if p1[0] is not None and p2[0] is not None:
            lw = max(0.8, 2 / z)
            draw_bresenham_line(ax, p1, p2, color='white', linewidth=lw, alpha=0.5)

# ─── Lampposts ──────────────────────────────────────────────

for z in range(4, 40, 8):
    for side_x in [-2.0, 2.0]:
        pole = create_quad(side_x, -1, z, 0.08, 1.8, '#616161')
        if pole: ax.add_patch(pole)
        light = create_quad(side_x, 0.8, z, 0.25, 0.1, '#FFF176')
        if light: ax.add_patch(light)

# ─── Trees alongside road ──────────────────────────────────

for z in range(6, 45, 7):
    for x in [-2.8, 2.8]:
        trunk = create_quad(x, -1, z, 0.15, 0.6, '#5D4037')
        if trunk: ax.add_patch(trunk)
        for dx_off, dy_off, r in [(-0.15, 0.1, 0.3), (0.15, 0.1, 0.3), (0, 0.3, 0.35)]:
            cp = project(x + dx_off, -0.4 + dy_off, z)
            if cp[0] is not None:
                size = r * FOCAL_LENGTH / z
                ax.add_patch(patches.Circle(cp, size, color='#2E7D32', ec='#1B5E20', lw=0.3, alpha=0.9))

# ─── Dynamic Cars ───────────────────────────────────────────

# Car definition: each car has parts relative to its center
# (name, dx, dy, dz, width, height, color_key)
car_parts_template = [
    ('body',       0,    0,    0,    0.6,  0.3,  'body'),
    ('cabin',      0,    0.3,  0,    0.4,  0.2,  'cabin'),
    ('windshield', 0,    0.3, -0.08, 0.36, 0.17, 'windshield'),
    ('wheel_fl',  -0.25, -0.05, -0.05, 0.11, 0.11, 'wheel'),
    ('wheel_fr',   0.25, -0.05, -0.05, 0.11, 0.11, 'wheel'),
    ('wheel_bl',  -0.25, -0.05,  0.1,  0.11, 0.11, 'wheel'),
    ('wheel_br',   0.25, -0.05,  0.1,  0.11, 0.11, 'wheel'),
    ('light_l',   -0.22, 0.12, -0.12, 0.07, 0.07, 'light'),
    ('light_r',    0.22, 0.12, -0.12, 0.07, 0.07, 'light'),
    ('tail_l',    -0.22, 0.12,  0.12, 0.07, 0.07, 'tail'),
    ('tail_r',     0.22, 0.12,  0.12, 0.07, 0.07, 'tail'),
]

# Color schemes for different cars
car_colors = [
    {'body': '#E53935', 'cabin': '#C62828', 'windshield': '#81D4FA', 'wheel': '#212121', 'light': '#FFF176', 'tail': '#FF5252'},  # Red
    {'body': '#1976D2', 'cabin': '#1565C0', 'windshield': '#B3E5FC', 'wheel': '#212121', 'light': '#FFF176', 'tail': '#FF5252'},  # Blue
    {'body': '#FFC107', 'cabin': '#FFA000', 'windshield': '#81D4FA', 'wheel': '#212121', 'light': '#FFF9C4', 'tail': '#FF5252'},  # Yellow/Taxi
    {'body': '#4CAF50', 'cabin': '#388E3C', 'windshield': '#B3E5FC', 'wheel': '#212121', 'light': '#FFF176', 'tail': '#FF5252'},  # Green
    {'body': '#9C27B0', 'cabin': '#7B1FA2', 'windshield': '#CE93D8', 'wheel': '#212121', 'light': '#FFF176', 'tail': '#FF5252'},  # Purple
]

# Car instances: (lane_x, start_z, speed, color_index, direction)
# direction: -1 = coming toward camera, +1 = going away
cars_config = [
    (-0.5,  25.0, 0.30, 0, -1),   # Red car, left lane, coming toward us
    ( 0.5,  35.0, 0.20, 1,  1),   # Blue car, right lane, going away
    (-0.5,  10.0, 0.35, 2, -1),   # Yellow car, left lane, coming
    ( 0.5,  18.0, 0.25, 3,  1),   # Green car, right lane, going away
    (-0.5,  42.0, 0.28, 4, -1),   # Purple car, left lane, coming
]

# Create patches for each car
all_car_patches = []
for car_idx, (lane_x, start_z, speed, color_idx, direction) in enumerate(cars_config):
    car_patches = {}
    for name, *_ in car_parts_template:
        p = patches.Polygon([[0,0]], color='white', visible=False)
        ax.add_patch(p)
        car_patches[name] = p
    all_car_patches.append(car_patches)

def update(frame):
    """Animation update: move all cars along the road."""
    artists = []

    for car_idx, (lane_x, start_z, speed, color_idx, direction) in enumerate(cars_config):
        colors = car_colors[color_idx]
        car_patches = all_car_patches[car_idx]

        # Calculate z position
        if direction == -1:  # Coming toward camera
            z_pos = start_z - (frame * speed) % (start_z - 1.5)
            if z_pos < 2.0:
                z_pos = start_z  # Reset to far away
        else:  # Going away
            z_pos = 3.0 + (frame * speed) % (45.0 - 3.0)

        # Subtle bounce for suspension effect
        bounce = abs(np.sin(frame * 0.8 + car_idx * 1.5)) * 0.03

        for name, dx, dy, dz, w, h, color_key in car_parts_template:
            actual_dy = dy + (bounce if 'wheel' not in name else 0)
            color = colors[color_key]

            poly = create_quad(lane_x + dx, -1 + actual_dy, z_pos + dz, w, h, color)
            patch = car_patches[name]

            if poly:
                patch.set_visible(True)
                patch.set_xy(poly.get_xy())
                patch.set_color(color)
                if color_key == 'light':
                    patch.set_edgecolor('none')
                elif color_key == 'windshield':
                    patch.set_edgecolor('#4FC3F7')
                    patch.set_linewidth(0.3)
                else:
                    patch.set_edgecolor('#222')
                    patch.set_linewidth(0.5)
            else:
                patch.set_visible(False)

            artists.append(patch)

    return artists

ani = animation.FuncAnimation(fig, update, frames=300, interval=40, blit=True)
print("🚗 Road animation running... Close window to exit.")
plt.show(block=True)
