"""
A lightweight, SVG-backed implementation of an NSBezierPath-like API.

This implements a minimal subset suitable for demos and as a kernel
primitive: move_to, line_to, curve_to (cubic), close_path, append_rect,
append_arc, set_line_width, stroke, fill, and to_svg().

It is intentionally small and suitable for extension into raster or
vector backends later (Adapters later).
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

@dataclass
class NSPoint:
    x: float
    y: float

@dataclass
class NSColor:
    r: int = 0
    g: int = 0
    b: int = 0
    a: float = 1.0

    def to_rgba(self) -> str:
        if self.a >= 1.0:
            return f"rgb({self.r},{self.g},{self.b})"
        return f"rgba({self.r},{self.g},{self.b},{self.a})"

class _Cmd:
    def __init__(self, name: str, args: Tuple):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"_Cmd({self.name}, {self.args})"


class NSBezierPath:
    """A minimal path class that can serialize to SVG path data.

    Extended with additional GNUStep-like methods:
    - element access (element_count, element_at_index)
    - bounding box (bounds)
    - hit testing (contains_point)
    - winding rule (even-odd vs nonzero)
    - affine transforms (transform)
    - line dash/cap/join/miter support
    - append_path
    """

    # Element constants compatible with GNUStep naming
    NSMoveToBezierPathElement = 0
    NSLineToBezierPathElement = 1
    NSCurveToBezierPathElement = 2
    NSClosePathBezierPathElement = 3
    NSArcBezierPathElement = 4

    def __init__(self):
        self._cmds: List[_Cmd] = []
        self._line_width: float = 1.0
        self._stroke_color: Optional[NSColor] = NSColor(0, 0, 0)
        self._fill_color: Optional[NSColor] = None
        self._fill_gradient = None
        self._shadow = None
        self._uses_even_odd_fill_rule: bool = False
        # stroke style
        self._line_cap: str = 'round'  # 'butt'|'round'|'square'
        self._line_join: str = 'round'  # 'miter'|'round'|'bevel'
        self._miter_limit: float = 10.0
        self._dash_pattern: Optional[List[float]] = None
        self._dash_phase: float = 0.0

    # Basic path construction (GNUStep-compatible names)
    def move_to_point(self, p: NSPoint):
        self._cmds.append(_Cmd('M', (p.x, p.y)))

    def line_to_point(self, p: NSPoint):
        self._cmds.append(_Cmd('L', (p.x, p.y)))

    def curve_to_point(self, control1: NSPoint, control2: NSPoint, end: NSPoint):
        # cubic bezier
        self._cmds.append(_Cmd('C', (control1.x, control1.y, control2.x, control2.y, end.x, end.y)))

    def close_path(self):
        self._cmds.append(_Cmd('Z', ()))

    def append_path(self, other: 'NSBezierPath'):
        self._cmds.extend([_Cmd(c.name, tuple(c.args)) for c in other._cmds])

    # Convenience shapes (re-introduced)
    def append_rect(self, x: float, y: float, w: float, h: float):
        self.move_to_point(NSPoint(x, y))
        self.line_to_point(NSPoint(x + w, y))
        self.line_to_point(NSPoint(x + w, y + h))
        self.line_to_point(NSPoint(x, y + h))
        self.close_path()

    def append_oval_in_rect(self, x: float, y: float, w: float, h: float):
        # Approximate ellipse with 4 cubic beziers
        rx = w / 2.0
        ry = h / 2.0
        cx = x + rx
        cy = y + ry
        k = 0.5522847498307936  # control point offset for approximating a circle
        self.move_to_point(NSPoint(cx + rx, cy))
        self.curve_to_point(NSPoint(cx + rx, cy + k * ry), NSPoint(cx + k * rx, cy + ry), NSPoint(cx, cy + ry))
        self.curve_to_point(NSPoint(cx - k * rx, cy + ry), NSPoint(cx - rx, cy + k * ry), NSPoint(cx - rx, cy))
        self.curve_to_point(NSPoint(cx - rx, cy - k * ry), NSPoint(cx - k * rx, cy - ry), NSPoint(cx, cy - ry))
        self.curve_to_point(NSPoint(cx + k * rx, cy - ry), NSPoint(cx + rx, cy - k * ry), NSPoint(cx + rx, cy))
        self.close_path()

    # Arc helpers
    def append_arc(self, center: NSPoint, radius: float, start_angle: float, end_angle: float, clockwise: bool = False):
        # Create an SVG arc command. Keep as A for serialization and store center/radius for element access
        start_x = center.x + math.cos(start_angle) * radius
        start_y = center.y + math.sin(start_angle) * radius
        end_x = center.x + math.cos(end_angle) * radius
        end_y = center.y + math.sin(end_angle) * radius
        large_arc = 1 if abs(end_angle - start_angle) > math.pi else 0
        sweep = 0 if clockwise else 1
        if not self._cmds:
            self.move_to_point(NSPoint(start_x, start_y))
        else:
            self.line_to_point(NSPoint(start_x, start_y))
        self._cmds.append(_Cmd('A', (radius, radius, 0, large_arc, sweep, end_x, end_y, center.x, center.y, start_angle, end_angle)))

    # Styles
    def set_line_width(self, w: float):
        self._line_width = w

    def set_stroke_color(self, color: NSColor):
        self._stroke_color = color

    def set_fill_color(self, color: Optional[NSColor]):
        self._fill_color = color

    def set_fill_gradient(self, gradient):
        """Set an `NSGradient`-like object to use as the fill. Must provide `to_svg_def(id, ...)`."""
        self._fill_gradient = gradient

    def set_shadow(self, shadow):
        """Set an `NSShadow`-like object to use for drop-shadow (should provide `to_svg_filter(id)`)."""
        self._shadow = shadow

    def set_uses_even_odd_fill_rule(self, v: bool):
        self._uses_even_odd_fill_rule = bool(v)

    def uses_even_odd_fill_rule(self) -> bool:
        return self._uses_even_odd_fill_rule

    def set_line_cap_style(self, style: str):
        self._line_cap = style

    def set_line_join_style(self, style: str):
        self._line_join = style

    def set_miter_limit(self, limit: float):
        self._miter_limit = limit

    def set_line_dash(self, pattern: Optional[List[float]], phase: float = 0.0):
        self._dash_pattern = pattern if pattern is None else list(pattern)
        self._dash_phase = phase

    def get_line_dash(self):
        return (self._dash_pattern, self._dash_phase)

    # Element access
    def element_count(self) -> int:
        return len(self._cmds)

    def element_at_index(self, i: int):
        if i < 0 or i >= len(self._cmds):
            raise IndexError('element index out of range')
        c = self._cmds[i]
        if c.name == 'M':
            return (self.NSMoveToBezierPathElement, [NSPoint(c.args[0], c.args[1])])
        if c.name == 'L':
            return (self.NSLineToBezierPathElement, [NSPoint(c.args[0], c.args[1])])
        if c.name == 'C':
            return (self.NSCurveToBezierPathElement, [NSPoint(c.args[0], c.args[1]), NSPoint(c.args[2], c.args[3]), NSPoint(c.args[4], c.args[5])])
        if c.name == 'Z':
            return (self.NSClosePathBezierPathElement, [])
        if c.name == 'A':
            # stored args: rx, ry, rot, laf, sf, x, y, cx, cy, start, end
            return (self.NSArcBezierPathElement, [NSPoint(c.args[6], c.args[7]), c.args[8], c.args[9]])
        return (None, [])

    # Bounds & hit testing
    def bounds(self):
        # Compute conservative bounding box over all points and control points. Approximate arcs by sampling.
        xs = []
        ys = []
        def add_point(x,y):
            xs.append(x); ys.append(y)
        for c in self._cmds:
            if c.name in ('M','L'):
                add_point(c.args[0], c.args[1])
            elif c.name == 'C':
                add_point(c.args[0], c.args[1]); add_point(c.args[2], c.args[3]); add_point(c.args[4], c.args[5])
            elif c.name == 'A':
                # sample arc
                rx, ry, rot, laf, sf, x, y, cx, cy, start, end = c.args
                steps = max(6, int(abs(end - start) / (math.pi/8)))
                for t in range(steps+1):
                    ang = start + (end - start) * (t/steps)
                    add_point(cx + math.cos(ang)*rx, cy + math.sin(ang)*ry)
            elif c.name == 'Z':
                pass
        if not xs:
            return (0,0,0,0)
        return (min(xs), min(ys), max(xs), max(ys))

    def contains_point(self, p: NSPoint) -> bool:
        # Use flattened segments and either even-odd (ray-casting) or nonzero winding number.
        segs = self._flattened_segments()
        if not segs:
            return False
        x = p.x; y = p.y
        if self._uses_even_odd_fill_rule:
            inside = False
            for (x1,y1),(x2,y2) in segs:
                if ((y1>y) != (y2>y)) and (x < (x2-x1)*(y-y1)/(y2-y1)+x1):
                    inside = not inside
            return inside
        else:
            # Nonzero winding rule
            wn = 0
            def is_left(x1,y1,x2,y2, xpt, ypt):
                return (x2-x1)*(ypt-y1) - (xpt-x1)*(y2-y1)
            for (x1,y1),(x2,y2) in segs:
                if y1 <= y:
                    if y2 > y and is_left(x1,y1,x2,y2, x, y) > 0:
                        wn += 1
                else:
                    if y2 <= y and is_left(x1,y1,x2,y2, x, y) < 0:
                        wn -= 1
            return wn != 0

    # Relative methods
    def relative_move_to_point(self, dx: float, dy: float):
        cur = self._current_point()
        if cur is None:
            self.move_to_point(NSPoint(dx, dy))
        else:
            self.move_to_point(NSPoint(cur[0] + dx, cur[1] + dy))

    def relative_line_to_point(self, dx: float, dy: float):
        cur = self._current_point()
        if cur is None:
            self.line_to_point(NSPoint(dx, dy))
        else:
            self.line_to_point(NSPoint(cur[0] + dx, cur[1] + dy))

    def relative_curve_to_point(self, control1_dx: float, control1_dy: float, control2_dx: float, control2_dy: float, end_dx: float, end_dy: float):
        cur = self._current_point()
        if cur is None:
            # interpret relative as absolute
            self.curve_to_point(NSPoint(control1_dx, control1_dy), NSPoint(control2_dx, control2_dy), NSPoint(end_dx, end_dy))
        else:
            x0,y0 = cur
            self.curve_to_point(NSPoint(x0 + control1_dx, y0 + control1_dy), NSPoint(x0 + control2_dx, y0 + control2_dy), NSPoint(x0 + end_dx, y0 + end_dy))

    def _current_point(self):
        # Return last endpoint (x,y) of the path or None
        for c in reversed(self._cmds):
            if c.name == 'M' or c.name == 'L':
                return (c.args[0], c.args[1])
            if c.name == 'C':
                return (c.args[4], c.args[5])
            if c.name == 'A':
                return (c.args[5], c.args[6])
            if c.name == 'Z':
                # continue searching for move
                continue
        return None

    def _previous_point(self):
        # Return the point before the last endpoint, if available
        last = None
        for c in self._cmds:
            if c.name == 'M' or c.name == 'L':
                last = (c.args[0], c.args[1])
            elif c.name == 'C':
                last = (c.args[4], c.args[5])
            elif c.name == 'A':
                last = (c.args[5], c.args[6])
            elif c.name == 'Z':
                # ignore
                pass
        # now find the last two
        pts = []
        for c in self._cmds:
            if c.name == 'M' or c.name == 'L':
                pts.append((c.args[0], c.args[1]))
            elif c.name == 'C':
                pts.append((c.args[4], c.args[5]))
            elif c.name == 'A':
                pts.append((c.args[5], c.args[6]))
        if len(pts) >= 2:
            return pts[-2]
        return None

    # Rounded rectangle
    def append_rounded_rect(self, x: float, y: float, w: float, h: float, r: float):
        if r <= 0:
            self.append_rect(x, y, w, h)
            return
        r = min(r, w/2.0, h/2.0)
        k = 0.5522847498307936
        # Start at left-center of bottom edge
        self.move_to_point(NSPoint(x + r, y))
        # bottom edge to right minus corner
        self.line_to_point(NSPoint(x + w - r, y))
        # bottom-right corner
        cx = x + w - r
        cy = y + r
        self.curve_to_point(NSPoint(cx + k*r, cy - r), NSPoint(cx + r, cy - k*r), NSPoint(cx + r, cy))
        # right edge
        self.line_to_point(NSPoint(x + w, y + h - r))
        # top-right corner
        cx = x + w - r
        cy = y + h - r
        self.curve_to_point(NSPoint(cx + r, cy + k*r), NSPoint(cx + k*r, cy + r), NSPoint(cx, cy + r))
        # top edge
        self.line_to_point(NSPoint(x + r, y + h))
        # top-left corner
        cx = x + r
        cy = y + h - r
        self.curve_to_point(NSPoint(cx - k*r, cy + r), NSPoint(cx - r, cy + k*r), NSPoint(cx - r, cy))
        # left edge
        self.line_to_point(NSPoint(x, y + r))
        # bottom-left corner
        cx = x + r
        cy = y + r
        self.curve_to_point(NSPoint(cx - r, cy - k*r), NSPoint(cx - k*r, cy - r), NSPoint(x + r, y))
        self.close_path()

    def _flattened_segments(self, curve_steps=12, tolerance: float = 0.5):
        # return list of line segments approximating the path: [((x1,y1),(x2,y2)), ...]
        # Uses adaptive subdivision for cubics when tolerance is small.
        segs = []
        cur = None
        last_move = None

        def subdivide_cubic(p0, p1, p2, p3, tol):
            # recursively subdivide until flat enough
            def flat_enough(p0,p1,p2,p3, tol):
                # use distance from control points to chord as flatness metric
                def dist_point_to_line(px,py, x1,y1,x2,y2):
                    num = abs((y2-y1)*px - (x2-x1)*py + x2*y1 - y2*x1)
                    den = math.hypot(y2-y1, x2-x1)
                    return num/den if den != 0 else 0
                d1 = dist_point_to_line(p1[0],p1[1], p0[0],p0[1], p3[0],p3[1])
                d2 = dist_point_to_line(p2[0],p2[1], p0[0],p0[1], p3[0],p3[1])
                return max(d1,d2) <= tol

            segments = []
            stack = [(p0,p1,p2,p3)]
            while stack:
                a,b,c,d = stack.pop()
                if flat_enough(a,b,c,d, tolerance):
                    segments.append((a,d))
                else:
                    # subdivide
                    ab = ((a[0]+b[0])/2.0,(a[1]+b[1])/2.0)
                    bc = ((b[0]+c[0])/2.0,(b[1]+c[1])/2.0)
                    cd = ((c[0]+d[0])/2.0,(c[1]+d[1])/2.0)
                    abbc = ((ab[0]+bc[0])/2.0,(ab[1]+bc[1])/2.0)
                    bccd = ((bc[0]+cd[0])/2.0,(bc[1]+cd[1])/2.0)
                    mid = ((abbc[0]+bccd[0])/2.0,(abbc[1]+bccd[1])/2.0)
                    stack.append((mid,bccd,cd,d))
                    stack.append((a,ab,abbc,mid))
            return segments

        for c in self._cmds:
            if c.name == 'M':
                cur = (c.args[0], c.args[1])
                last_move = cur
            elif c.name == 'L':
                nxt = (c.args[0], c.args[1])
                segs.append((cur, nxt))
                cur = nxt
            elif c.name == 'C':
                x0,y0 = cur
                x1,y1,x2,y2,x3,y3 = c.args
                segs.extend(subdivide_cubic((x0,y0),(x1,y1),(x2,y2),(x3,y3), tolerance))
                cur = (x3,y3)
            elif c.name == 'A':
                rx, ry, rot, laf, sf, x, y, cx, cy, start, end = c.args
                steps = max(6, int(abs(end - start) / (math.pi/16)))
                prev = (cx + math.cos(start)*rx, cy + math.sin(start)*ry)
                for t_step in range(1, steps+1):
                    ang = start + (end-start)*(t_step/steps)
                    pt = (cx + math.cos(ang)*rx, cy + math.sin(ang)*ry)
                    segs.append((prev, pt))
                    prev = pt
                cur = (x,y)
            elif c.name == 'Z':
                if last_move and cur and (cur != last_move):
                    segs.append((cur, last_move))
                cur = last_move
        return segs

    # Transforms
    def transform(self, a: float, b: float, c: float, d: float, tx: float=0.0, ty: float=0.0):
        def apply(x,y):
            return (a*x + c*y + tx, b*x + d*y + ty)
        new_cmds: List[_Cmd] = []
        for cmd in self._cmds:
            if cmd.name in ('M','L'):
                x,y = apply(cmd.args[0], cmd.args[1])
                new_cmds.append(_Cmd(cmd.name, (x,y)))
            elif cmd.name == 'C':
                pts = list(cmd.args)
                for i in range(0,6,2):
                    pts[i],pts[i+1] = apply(pts[i], pts[i+1])
                new_cmds.append(_Cmd('C', tuple(pts)))
            elif cmd.name == 'A':
                # rx,ry,rot,laf,sf,x,y,cx,cy,start,end
                rx, ry, rot, laf, sf, x, y, cx, cy, s,e = cmd.args
                x,y = apply(x,y); cx,cy = apply(cx,cy)
                new_cmds.append(_Cmd('A', (rx,ry,rot,laf,sf,x,y,cx,cy,s,e)))
            elif cmd.name == 'Z':
                new_cmds.append(_Cmd('Z', ()))
        self._cmds = new_cmds

    # Additional GNUStep helpers
    def append_arc_through_points(self, p1: NSPoint, p2: NSPoint, p3: NSPoint):
        """Append an arc that passes through three points (circumcircle arc).

        If points are collinear or nearly, falls back to line segments.
        """
        ax,ay = p1.x, p1.y
        bx,by = p2.x, p2.y
        cx,cy = p3.x, p3.y
        # compute circumcenter
        d = 2*(ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
        if abs(d) < 1e-9:
            # nearly collinear -> just line to p2 and p3
            self.line_to_point(NSPoint(bx,by))
            self.line_to_point(NSPoint(cx,cy))
            return
        ux = ((ax*ax+ay*ay)*(by-cy) + (bx*bx+by*by)*(cy-ay) + (cx*cx+cy*cy)*(ay-by))/d
        uy = ((ax*ax+ay*ay)*(cx-bx) + (bx*bx+by*by)*(ax-cx) + (cx*cx+cy*cy)*(bx-ax))/d
        center = NSPoint(ux, uy)
        r = math.hypot(ax-ux, ay-uy)
        start = math.atan2(ay-uy, ax-ux)
        end = math.atan2(cy-uy, cx-ux)
        # choose sweep based on orientation of points (sign of cross product)
        cross = (bx-ax)*(cy-ay) - (by-ay)*(cx-ax)
        clockwise = cross < 0
        # move to p1 if needed
        if not self._cmds:
            self.move_to_point(p1)
        else:
            self.line_to_point(p1)
        self._cmds.append(_Cmd('A', (r, r, 0, 1 if abs(end-start)>math.pi else 0, 0 if clockwise else 1, cx, cy, ux, uy, start, end)))

    def append_arc_from_point_to_point_radius(self, from_pt: NSPoint, to_pt: NSPoint, radius: float):
        """Append an arc of given radius tangent to the incoming segment at from_pt
        and tangent to the outgoing segment toward to_pt.

        Behavior mirrors GNUStep/Cocoa `appendBezierPathWithArcFromPoint:toPoint:radius:`
        in a practical, numerically stable way. If geometry is degenerate or the
        radius is too large for the corner, falls back to connecting the points
        with straight lines.
        """
        cur = self._current_point()
        if cur is None:
            # nothing to tangent from; just line between
            self.move_to_point(from_pt)
            self.line_to_point(to_pt)
            return
        sx,sy = cur
        fx,fy = from_pt.x, from_pt.y
        tx,ty = to_pt.x, to_pt.y
        # incoming vector at the corner: from corner to start
        u = (sx - fx, sy - fy)
        v = (tx - fx, ty - fy)  # outgoing vector from corner
        nu = math.hypot(u[0], u[1])
        nv = math.hypot(v[0], v[1])
        # If incoming vector is zero (from_pt equals current point), try to use previous point
        if nu == 0:
            prev = self._previous_point()
            if prev is not None:
                u = (prev[0] - fx, prev[1] - fy)
                nu = math.hypot(u[0], u[1])
        if nu == 0 or nv == 0:
            # degenerate, just line
            self.line_to_point(from_pt)
            self.line_to_point(to_pt)
            return
        u = (u[0]/nu, u[1]/nu)
        v = (v[0]/nv, v[1]/nv)
        # angle between the rays
        dot = max(-1.0, min(1.0, u[0]*v[0] + u[1]*v[1]))
        angle = math.acos(dot)
        if angle <= 1e-6 or abs(math.pi - angle) <= 1e-6:
            # straight or opposite; can't form a clean tangent arc
            self.line_to_point(from_pt)
            self.line_to_point(to_pt)
            return
        # distance from corner along each segment to tangent points
        tangent_dist = radius / math.tan(angle/2.0)
        if tangent_dist > nu or tangent_dist > nv:
            # radius too big to fit, fallback
            self.line_to_point(from_pt)
            self.line_to_point(to_pt)
            return
        t1 = (fx + u[0]*tangent_dist, fy + u[1]*tangent_dist)
        t2 = (fx + v[0]*tangent_dist, fy + v[1]*tangent_dist)
        # bisector direction
        bis = (u[0] + v[0], u[1] + v[1])
        bis_len = math.hypot(bis[0], bis[1])
        if bis_len == 0:
            # opposite directions, fallback
            self.line_to_point(from_pt)
            self.line_to_point(to_pt)
            return
        bis = (bis[0]/bis_len, bis[1]/bis_len)
        center_dist = radius / math.sin(angle/2.0)
        cx = fx + bis[0]*center_dist
        cy = fy + bis[1]*center_dist
        # angles for the arc
        start_ang = math.atan2(t1[1]-cy, t1[0]-cx)
        end_ang = math.atan2(t2[1]-cy, t2[0]-cx)
        # determine clockwise based on cross product sign (u x v)
        cross = u[0]*v[1] - u[1]*v[0]
        clockwise = cross < 0
        # emit: line to tangent start, arc, line to to_pt endpoint
        self.line_to_point(NSPoint(t1[0], t1[1]))
        self._cmds.append(_Cmd('A', (radius, radius, 0, 1 if abs(end_ang-start_ang) > math.pi else 0, 0 if clockwise else 1, t2[0], t2[1], cx, cy, start_ang, end_ang)))
        # ensure ending at to_pt
        self.line_to_point(to_pt)

    # Convenience alias matching Cocoa/GNUstep API name
    def append_bezier_path_with_arc_from_point_to_point_radius(self, from_pt: NSPoint, to_pt: NSPoint, radius: float):
        return self.append_arc_from_point_to_point_radius(from_pt, to_pt, radius)

    # Center-based arc variant normalized: accepts angles in radians and a clockwise flag.
    def append_arc_with_center(self, center: NSPoint, radius: float, start_angle: float, end_angle: float, clockwise: bool = False):
        # Normalize angles to a canonical representation and append as an 'A' cmd
        sa = start_angle
        ea = end_angle
        # ensure we pick the intended sweep: if clockwise True, we will make sweep flag accordingly
        large_arc = 1 if abs(ea - sa) > math.pi else 0
        sweep = 0 if clockwise else 1
        start_x = center.x + math.cos(sa) * radius
        start_y = center.y + math.sin(sa) * radius
        end_x = center.x + math.cos(ea) * radius
        end_y = center.y + math.sin(ea) * radius
        if not self._cmds:
            self.move_to_point(NSPoint(start_x, start_y))
        else:
            self.line_to_point(NSPoint(start_x, start_y))
        self._cmds.append(_Cmd('A', (radius, radius, 0, large_arc, sweep, end_x, end_y, center.x, center.y, sa, ea)))

    # Degrees-friendly helper
    def append_arc_with_center_degrees(self, center: NSPoint, radius: float, start_deg: float, end_deg: float, clockwise: bool = False):
        return self.append_arc_with_center(center, radius, math.radians(start_deg), math.radians(end_deg), clockwise)

    def reversed(self) -> 'NSBezierPath':
        """Return a new NSBezierPath that reverses subpaths and segments."""
        new = NSBezierPath()
        # Break into subpaths
        subpaths = []
        cur = []
        for c in self._cmds:
            if c.name == 'M':
                if cur:
                    subpaths.append(cur)
                cur = [c]
            else:
                cur.append(c)
        if cur:
            subpaths.append(cur)
        # reverse each subpath
        for sp in subpaths:
            # find points for reconstruction
            pts = []
            for e in sp:
                if e.name == 'M':
                    pts.append((e.args[0], e.args[1]))
                elif e.name == 'L':
                    pts.append((e.args[0], e.args[1]))
                elif e.name == 'C':
                    pts.append((e.args[4], e.args[5]))
                elif e.name == 'A':
                    pts.append((e.args[5], e.args[6]))
                elif e.name == 'Z':
                    # closes; do nothing
                    pass
            if not pts:
                continue
            # start new subpath at last point
            last = pts[-1]
            new.move_to_point(NSPoint(last[0], last[1]))

            # Walk backwards through elements and append reversed geometry
            rev_iter = list(sp)[::-1]
            # keep a pointer to points list for popping
            pts_rev = pts[::-1]
            for e in rev_iter:
                if e.name == 'M':
                    break
                if e.name == 'L':
                    # pop current endpoint and line to next
                    pts_rev.pop(0)
                    if pts_rev:
                        target = pts_rev[0]
                        new.line_to_point(NSPoint(target[0], target[1]))
                elif e.name == 'C':
                    # original: C c1 c2 end (absolute). For reverse, controls swap and we create cubic to previous point
                    # e.args = (c1x,c1y,c2x,c2y, endx, endy)
                    end = pts_rev.pop(0)
                    if pts_rev:
                        start = pts_rev[0]
                        # reversed controls: c1' = original c2, c2' = original c1, both absolute
                        c1 = NSPoint(e.args[2], e.args[3])
                        c2 = NSPoint(e.args[0], e.args[1])
                        new.curve_to_point(c1, c2, NSPoint(start[0], start[1]))
                elif e.name == 'A':
                    # reverse arc: swap start/end and flip sweep
                    # args stored as: rx,ry,rot,laf,sf,x,y,cx,cy,start,end
                    rx,ry,rot,laf,sf,x,y,cx,cy,s,eang = e.args
                    # flip sweep flag
                    new_sweep = 0 if sf else 1
                    # new arc from current position to previous point; we swap start/end angles
                    new._cmds.append(_Cmd('A', (rx,ry,rot,laf,new_sweep,x,y,cx,cy,eang,s)))
                elif e.name == 'Z':
                    new.close_path()
        return new

    def reverse_in_place(self):
        """Reverse this path in place (mutates path) by replacing contents with reversed()."""
        rev = self.reversed()
        self._cmds = rev._cmds

    # GNUStep/Cocoa alias
    def reverseInPlace(self):
        return self.reverse_in_place()

    # Serialization
    def _to_path_d(self) -> str:
        parts: List[str] = []
        for c in self._cmds:
            if c.name == 'M' or c.name == 'L':
                parts.append(f"{c.name} {c.args[0]} {c.args[1]}")
            elif c.name == 'C':
                parts.append(f"C {c.args[0]} {c.args[1]} {c.args[2]} {c.args[3]} {c.args[4]} {c.args[5]}")
            elif c.name == 'Z':
                parts.append('Z')
            elif c.name == 'A':
                rx, ry, rot, laf, sf, x, y = c.args[:7]
                parts.append(f"A {rx} {ry} {rot} {int(laf)} {int(sf)} {x} {y}")
            else:
                # unknown, ignore
                pass
        return ' '.join(parts)

    def to_svg(self, width: float = 400, height: float = 400) -> str:
        import uuid
        d = self._to_path_d()
        stroke = self._stroke_color.to_rgba() if self._stroke_color else 'none'
        fill = 'none'
        # build defs
        defs = []
        fill_attr = ''
        if self._fill_gradient is not None:
            gid = f"grad-{uuid.uuid4().hex[:8]}"
            # gradient should provide an SVG def via to_svg_def
            try:
                defs.append(self._fill_gradient.to_svg_def(id=gid))
                fill_attr = f' fill="url(#{gid})"'
            except Exception:
                # fallback to color if gradient fails
                if self._fill_color:
                    fill_attr = f' fill="{self._fill_color.to_rgba()}"'
        else:
            if self._fill_color:
                fill_attr = f' fill="{self._fill_color.to_rgba()}"'

        fill_rule = 'evenodd' if self._uses_even_odd_fill_rule else 'nonzero'
        dash_attr = ''
        dash_offset = ''
        if self._dash_pattern:
            dash_attr = f' stroke-dasharray="{" ".join(str(x) for x in self._dash_pattern)}"'
            dash_offset = f' stroke-dashoffset="{self._dash_phase}"'

        filter_attr = ''
        if self._shadow is not None:
            fid = f"sh-{uuid.uuid4().hex[:8]}"
            try:
                defs.append(self._shadow.to_svg_filter(id=fid))
                filter_attr = f' filter="url(#{fid})"'
            except Exception:
                filter_attr = ''

        defs_block = ''
        if defs:
            defs_block = '<defs>\n' + '\n'.join(defs) + '\n</defs>\n'

        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
               f'{defs_block}  <path d="{d}" stroke="{stroke}" stroke-width="{self._line_width}"{fill_attr} fill-rule="{fill_rule}" stroke-linecap="{self._line_cap}" stroke-linejoin="{self._line_join}" stroke-miterlimit="{self._miter_limit}"{dash_attr}{dash_offset}{filter_attr} />\n'
               f'</svg>')
        return svg

    # Convenience renderers
    def stroke(self, width: float = None, color: Optional[NSColor] = None):
        if width is not None:
            self.set_line_width(width)
        if color is not None:
            self.set_stroke_color(color)

    def fill(self, color: NSColor):
        self.set_fill_color(color)

    def clear(self):
        self._cmds.clear()


# Small helper for quick demos
def sample_star(cx=200, cy=200, r1=80, r2=30, points=5):
    p = NSBezierPath()
    angle = -math.pi / 2
    step = math.pi * 2 / (points * 2)
    p.move_to_point(NSPoint(cx + math.cos(angle) * r1, cy + math.sin(angle) * r1))
    for i in range(points * 2 - 1):
        angle += step
        r = r2 if i % 2 == 0 else r1
        p.line_to_point(NSPoint(cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    p.close_path()
    return p
