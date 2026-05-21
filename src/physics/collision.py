"""Collision detection helpers for AABB rectangles, circles, and ranges."""

import math

def check_rect_collision(
    x1: float, y1: float, w1: float, h1: float,
    x2: float, y2: float, w2: float, h2: float,
) -> bool:
    """Checks if two axis-aligned bounding boxes (AABBs) overlap.

    Coordinates represent top-left corners of the boxes.

    Args:
        x1: Left coordinate of first box.
        y1: Top coordinate of first box.
        w1: Width of first box.
        h1: Height of first box.
        x2: Left coordinate of second box.
        y2: Top coordinate of second box.
        w2: Width of second box.
        h2: Height of second box.

    Returns:
        True if the rectangles overlap, False otherwise.
    """
    return (
        x1 < x2 + w2 and
        x1 + w1 > x2 and
        y1 < y2 + h2 and
        y1 + h1 > y2
    )

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculates the Euclidean distance between two points.

    Args:
        x1: X coordinate of first point.
        y1: Y coordinate of first point.
        x2: X coordinate of second point.
        y2: Y coordinate of second point.

    Returns:
        The distance between the two points.
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def check_circle_collision(
    cx: float, cy: float, radius: float,
    rx: float, ry: float, rw: float, rh: float,
) -> bool:
    """Checks if a circle intersects with a rectangle (AABB).

    Useful for explosion/splash damage radius checks.

    Args:
        cx: Center X of circle.
        cy: Center Y of circle.
        radius: Circle radius.
        rx: Left coordinate of rectangle.
        ry: Top coordinate of rectangle.
        rw: Width of rectangle.
        rh: Height of rectangle.

    Returns:
        True if the circle and rectangle overlap, False otherwise.
    """
    # Find the closest point on the rectangle to the circle's center
    closest_x = max(rx, min(cx, rx + rw))
    closest_y = max(ry, min(cy, ry + rh))

    # Calculate distance between closest point and circle center
    dist = distance(cx, cy, closest_x, closest_y)

    # If the distance is less than the radius, there is a collision
    return dist < radius
