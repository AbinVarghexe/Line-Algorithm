# Code Explanation: Road Perspective with Animated Cars

This document explains the `road_perspective.py` (static) and `animated_road.py` (animated) scripts. Both use Python and `matplotlib` to create a scenic 3D road perspective using **Line Drawing Algorithms** and **Projection Techniques**.

---

## 1. The Core Logic: `project(x, y, z)`

The entire 3D perspective effect relies on a simple **perspective projection** function that converts 3D world coordinates (x, y, z) into 2D screen coordinates.

```python
def project(x, y, z):
    if z <= 0.1: return None, None  # Don't draw if behind camera
    f = FOCAL_LENGTH / z            # Calculate scaling factor
    return x * f, y * f             # Scale x and y by depth
```

- **High `z` (far away)** → Small `f` → Object appears small (converges to vanishing point).
- **Low `z` (close up)** → Large `f` → Object appears large (fills the screen).

This is a **one-point perspective projection** — all parallel lines converge to a single vanishing point at the center of the screen.

---

## 2. Bresenham's Line Drawing Algorithm

Instead of using matplotlib's built-in line drawing, we implement **Bresenham's Line Algorithm** — a fundamental computer graphics algorithm that determines which points on a discrete grid should be selected to approximate a straight line.

```python
def bresenham_line(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1: break
        e2 = 2 * err
        if e2 > -dy: err -= dy; x0 += sx
        if e2 < dx:  err += dx; y0 += sy
    return points
```

### How it works:
1. Uses **only integer arithmetic** (no floating point) — historically important for efficiency.
2. Maintains an **error accumulator** to decide whether to step in x, y, or both.
3. Produces a list of pixel coordinates that form the best discrete approximation of the line.

### Where it's used:
- **Road edge lines** (white boundary lines)
- **Center dashed line** (yellow)
- **Lane markings** (white dashed)

We scale coordinates to a 200x grid for Bresenham computation, then scale back for rendering.

---

## 3. Drawing Shapes: `create_quad()`

A helper function that takes a 3D rectangle (center, width, height, depth) and projects its 4 corners into 2D space, creating a `Polygon` that matplotlib can render.

```python
def create_quad(x, y, z, w, h, color):
    points = [
        project(x - w/2, y, z), project(x + w/2, y, z),
        project(x + w/2, y + h, z), project(x - w/2, y + h, z)
    ]
    return patches.Polygon(points, ...)
```

Used for: car bodies, cabins, wheels, lampposts, tree trunks, headlights, etc.

---

## 4. The Static World

### Road
- **Surface**: A filled polygon between left and right road edges, colored dark asphalt (`#424242`).
- **Edge lines**: White lines drawn with Bresenham's algorithm.
- **Center line**: Yellow dashed line (every 2 units of z-depth).
- **Lane markings**: White dashed lines at ±0.75x offset.

### Scenery
- **Sky & Ground**: `set_facecolor` for sky blue, `fill_between` for green grass.
- **Sun with glow**: Two concentric circles (solid + transparent halo).
- **Clouds**: Grouped ellipses for fluffy cloud shapes.
- **Mountains**: Semi-transparent triangles on the horizon.
- **Lampposts**: Thin poles with yellow light fixtures, placed at regular intervals.
- **Trees**: Trunk (rectangle) + canopy (overlapping circles) alongside the road.

---

## 5. The Animated Cars

### Car Structure
Each car is made of 11 parts defined in `car_parts_template`:
- **Body** — main colored rectangle
- **Cabin/Roof** — darker shade on top
- **Windshield** — light blue with colored edge
- **4 Wheels** — dark circles at corners
- **2 Headlights** — bright yellow at front
- **2 Taillights** — red at rear

### Color Schemes
5 different color schemes (Red, Blue, Yellow/Taxi, Green, Purple) give each car a unique look.

### Movement
Cars are configured with:
- `lane_x`: Which lane (-0.5 = left, 0.5 = right)
- `start_z`: Starting depth
- `speed`: How fast they move per frame
- `direction`: -1 (toward camera) or +1 (away from camera)

### Suspension Bounce
```python
bounce = abs(np.sin(frame * 0.8 + car_idx * 1.5)) * 0.03
```
A subtle sine-wave bounce is applied to car bodies (but not wheels) to simulate road suspension, giving the animation a lifelike feel.

---

## 6. The Animation Loop: `update(frame)`

For every frame:
1. **Calculate z-position** for each car based on speed and direction.
2. **Reset cars** that go off-screen (loop them back).
3. **Apply bounce** to non-wheel parts.
4. **Project and update** all polygon patches.

```python
ani = animation.FuncAnimation(fig, update, frames=300, interval=40, blit=True)
```
- **300 frames** at **40ms interval** = ~25 FPS, 12 seconds per loop.
- `blit=True` for efficient rendering (only redraws changed elements).

---

## 7. Running the Project

### Static image:
```bash
python3 road_perspective.py
# Saves road_perspective.png
```

### Animation:
```bash
python3 animated_road.py
# Opens interactive matplotlib window with moving cars
```

Or use the convenience script:
```bash
./start_animation.sh
```
