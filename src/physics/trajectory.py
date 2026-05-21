"""Physics calculations for parabolic trajectories and projectile motion."""

def calculate_parabola(
    start_x: float,
    start_y: float,
    vx: float,
    vy: float,
    gravity: float,
    ground_y: float,
    steps: int = 50,
) -> list[tuple[float, float]]:
    """Calculates points along a parabolic path until it hits the ground.

    Useful for projecting visual aiming guides or predicting paths.

    Args:
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        vx: Initial velocity in the X direction.
        vy: Initial velocity in the Y direction.
        gravity: Gravity constant (acceleration down).
        ground_y: Y coordinate representing the ground plane.
        steps: Maximum number of points to calculate.

    Returns:
        List of (x, y) coordinates representing points along the trajectory.
    """
    points: list[tuple[float, float]] = []
    curr_x = start_x
    curr_y = start_y
    curr_vy = vy

    # Approximate time step (dt) for projection.
    # At 60 FPS, dt = 1.
    dt = 1.0

    points.append((curr_x, curr_y))

    for _ in range(steps):
        curr_x += vx * dt
        curr_vy += gravity * dt
        curr_y += curr_vy * dt

        points.append((curr_x, curr_y))

        # Stop calculating if the trajectory goes past the ground level
        if curr_y >= ground_y:
            break

    return points
