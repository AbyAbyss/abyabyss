"""
x, y, z in the real world: an explainer video built with 3Blue1Brown's manim (manimgl).

Render every scene (1080p) and stitch them together with:
    ./render.sh

Or render one scene while iterating (low quality, opens no window):
    manimgl xyz_axes.py ThreeDimensions -w -l
"""
from manimlib import *

# Standard convention in math, CAD and most 3D software: x = red, y = green, z = blue
X_COL = RED_C
Y_COL = GREEN_C
Z_COL = BLUE_C
ANS_COL = YELLOW
FONT = "Inter"


def T(text, **kwargs):
    kwargs.setdefault("font", FONT)
    return Text(text, **kwargs)


def caption(text, size=34, color=WHITE):
    cap = T(text, font_size=size, color=color)
    cap.set_backstroke(BLACK, 6)
    cap.set_max_width(FRAME_WIDTH - 0.8)
    cap.to_edge(DOWN, buff=0.45)
    cap.fix_in_frame()
    return cap


def heading(text, size=44):
    head = T(text, font_size=size, weight=BOLD)
    head.set_backstroke(BLACK, 6)
    head.set_max_width(FRAME_WIDTH - 0.8)
    head.to_edge(UP, buff=0.35)
    head.fix_in_frame()
    return head


def fixed_tex(tex, size=44, **kwargs):
    mob = Tex(tex, font_size=size, **kwargs)
    mob.set_backstroke(BLACK, 6)
    mob.fix_in_frame()
    return mob


def colored_xyz(mob):
    """Color every x, y and z glyph in a Tex mobject."""
    mob.set_color_by_tex_to_color_map({"x": X_COL, "y": Y_COL, "z": Z_COL})
    return mob


def make_axes(x_range=(0, 5, 1), y_range=(0, 5, 1), z_range=(0, 4, 1),
              width=None, height=None, depth=None, numbers=True):
    axes = ThreeDAxes(
        x_range=x_range, y_range=y_range, z_range=z_range,
        width=width, height=height, depth=depth,
        axis_config=dict(include_tip=True, tick_size=0.06),
    )
    axes.x_axis.set_color(X_COL)
    axes.y_axis.set_color(Y_COL)
    axes.z_axis.set_color(Z_COL)
    if numbers:
        axes.x_axis.add_numbers(font_size=20, excluding=[0])
        axes.y_axis.add_numbers(font_size=20, excluding=[0])
    return axes


def ball(point, color=ANS_COL, radius=0.09):
    return Sphere(radius=radius, color=color).move_to(point)


class XYZScene(Scene):
    """Shared helpers for labels that sit in 3D space but face the camera."""

    def face_camera(self, mob, point, offset=0.35 * UP):
        rot = self.frame.get_orientation().as_matrix()
        mob.move_to(ORIGIN + offset)
        mob.apply_matrix(rot, about_point=ORIGIN)
        mob.shift(point)
        return mob

    def label3d(self, tex, point, size=32, offset=0.35 * UP, color=WHITE):
        """A Tex label pinned to a 3D point that keeps facing the camera as it moves."""
        mob = Tex(tex, font_size=size).set_color(color)
        mob.set_backstroke(BLACK, 4)
        self.face_camera(mob, point, offset)
        mob.last_rot = self.frame.get_orientation().as_matrix()

        def keep_facing(m):
            rot = self.frame.get_orientation().as_matrix()
            if not np.allclose(rot, m.last_rot):
                # Undo the old camera rotation and apply the new one, keeping colors intact
                m.apply_matrix(rot @ m.last_rot.T, about_point=point)
                m.last_rot = rot

        mob.add_updater(keep_facing)
        return mob

    def axis_labels3d(self, axes, size=44, names=("x", "y", "z")):
        labels = VGroup()
        for name, axis, color in zip(names, axes.axes, (X_COL, Y_COL, Z_COL)):
            tip = axis.get_end() + 0.45 * normalize(axis.get_vector())
            labels.add(self.label3d(name, tip, size=size, offset=ORIGIN, color=color))
        return labels

    def z_numbers3d(self, axes, values, size=24):
        return VGroup(*(
            self.label3d(str(v), axes.c2p(0, 0, v), size=size, offset=0.3 * LEFT)
            for v in values
        ))

    def path_legs(self, axes, p, colors=(X_COL, Y_COL, Z_COL), dashed=True):
        """The three moves that reach p: along x, then y, then z."""
        x, y, z = p
        o = axes.c2p(0, 0, 0)
        a = axes.c2p(x, 0, 0)
        b = axes.c2p(x, y, 0)
        c = axes.c2p(x, y, z)
        line = DashedLine if dashed else Line
        return VGroup(
            line(o, a, color=colors[0], stroke_width=5),
            line(a, b, color=colors[1], stroke_width=5),
            line(b, c, color=colors[2], stroke_width=5),
        )


class Intro(XYZScene):
    def construct(self):
        title = Tex(R"x,\ y,\ z", font_size=120)
        colored_xyz(title)
        sub = T("How three letters describe every place in the real world", font_size=36)
        sub.next_to(title, DOWN, buff=0.5)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(sub, shift=0.3 * UP))
        self.wait(1.5)

        q = T(
            "Every x, y, z formula is really answering\n"
            "up to three questions about position:",
            font_size=36,
        )
        qs = VGroup(
            T("How far left or right?   →  x", font_size=36, t2c={"x": X_COL}),
            T("How far forward or back?   →  y", font_size=36, t2c={"y": Y_COL}),
            T("How far up or down?   →  z", font_size=36, t2c={"z": Z_COL}),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        group = VGroup(q, qs).arrange(DOWN, buff=0.6)
        self.play(FadeOut(VGroup(title, sub), shift=UP), FadeIn(q, shift=UP))
        for line in qs:
            self.play(FadeIn(line, shift=0.3 * RIGHT), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(group))


class OneDimension(XYZScene):
    def construct(self):
        head = heading("1D: one number, x")
        line = NumberLine((0, 8, 1), width=11, color=X_COL, include_tip=True)
        line.add_numbers(font_size=28)
        line.shift(0.3 * DOWN)
        x_lab = Tex("x", font_size=48).set_color(X_COL).next_to(line.get_end(), UR, buff=0.15)

        self.play(FadeIn(head))
        self.play(ShowCreation(line), Write(x_lab))

        # A little car on a straight road
        body = RoundedRectangle(width=1.0, height=0.38, corner_radius=0.12,
                                fill_color=TEAL, fill_opacity=1, stroke_width=0)
        roof = RoundedRectangle(width=0.55, height=0.3, corner_radius=0.1,
                                fill_color=TEAL_E, fill_opacity=1, stroke_width=0)
        roof.next_to(body, UP, buff=0).shift(0.05 * LEFT)
        wheels = VGroup(*(Circle(radius=0.11, fill_color=GREY_E, fill_opacity=1,
                                 stroke_color=WHITE, stroke_width=2) for _ in range(2)))
        wheels.arrange(RIGHT, buff=0.45).next_to(body, DOWN, buff=-0.08)
        car = VGroup(body, roof, wheels)
        car.next_to(line.n2p(0), UP, buff=0.05)

        cap = caption("A car on a straight road only needs ONE number: how far it has gone.")
        self.play(FadeIn(car), FadeIn(cap))
        x_tracker = ValueTracker(0)
        car.add_updater(lambda m: m.next_to(line.n2p(x_tracker.get_value()), UP, buff=0.05))
        readout = Tex(R"x = 0.0\text{ km}", font_size=48)
        readout.add_updater(lambda m: m.become(
            Tex(Rf"x = {x_tracker.get_value():.1f}\text{{ km}}", font_size=48)
            .set_color_by_tex("x", X_COL).move_to(1.8 * UP)
        ))
        self.add(readout)
        self.play(x_tracker.animate.set_value(6), run_time=3)
        self.wait()
        self.play(x_tracker.animate.set_value(2.5), run_time=1.5)
        car.clear_updaters()
        readout.clear_updaters()
        self.wait()

        new_cap = caption("Formulas with only x (like speed = distance / time) live on a single line.")
        self.play(FadeTransform(cap, new_cap))
        self.wait(2.5)
        self.play(*map(FadeOut, [head, line, x_lab, car, readout, new_cap]))


class TwoDimensions(XYZScene):
    def construct(self):
        head = heading("2D: add y, and you have a map")
        axes = make_axes(x_range=(0, 6, 1), y_range=(0, 5, 1), width=7, height=5.8)
        axes.z_axis.set_opacity(0)
        axes.center().shift(0.2 * DOWN)
        grid = NumberPlane(x_range=(0, 6, 1), y_range=(0, 5, 1), width=7, height=5.8,
                           background_line_style=dict(stroke_color=GREY_D, stroke_width=1))
        grid.axes.set_opacity(0)
        grid.shift(axes.get_origin() - grid.get_origin())
        x_lab = Tex("x", font_size=44).set_color(X_COL).next_to(axes.x_axis.get_end(), RIGHT)
        y_lab = Tex("y", font_size=44).set_color(Y_COL).next_to(axes.y_axis.get_end(), UP)
        east = T("east", font_size=24, color=X_COL).next_to(x_lab, DOWN, buff=0.1)
        north = T("north", font_size=24, color=Y_COL).next_to(y_lab, RIGHT, buff=0.15)

        self.play(FadeIn(head))
        self.play(ShowCreation(axes.x_axis), Write(x_lab), FadeIn(east))
        self.play(ShowCreation(axes.y_axis), Write(y_lab), FadeIn(north))
        self.play(FadeIn(grid))

        cap = caption("City streets: you're at (0, 0). The coffee shop is 4 blocks east, 3 blocks north.")
        self.play(FadeIn(cap))

        p = axes.c2p(4, 3, 0)
        legs = self.path_legs(axes, (4, 3, 0))[:2]
        self.play(ShowCreation(legs[0]))
        self.play(ShowCreation(legs[1]))
        dot = Dot(p, radius=0.12, color=ANS_COL)
        cup = T("coffee shop", font_size=26, color=ANS_COL).next_to(dot, UP, buff=0.15)
        coord = Tex("(4,\\ 3)", font_size=44).next_to(dot, RIGHT, buff=0.5)
        coord[1].set_color(X_COL)
        coord[3].set_color(Y_COL)
        self.play(GrowFromCenter(dot), FadeIn(cup), Write(coord))
        self.wait()

        new_cap = caption("Walking the streets: 4 + 3 = 7 blocks.  As the crow flies?")
        self.play(FadeTransform(cap, new_cap))
        hyp = Line(axes.get_origin(), p, color=ANS_COL, stroke_width=6)
        self.play(ShowCreation(hyp))

        formula = VGroup(
            Tex(R"d = \sqrt{x^2 + y^2}", font_size=48),
            Tex(R"= \sqrt{4^2 + 3^2}", font_size=48),
            Tex(R"= \sqrt{25} = 5 \text{ blocks}", font_size=48),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        formula.to_corner(UR).shift(0.9 * DOWN)
        colored_xyz(formula[0])
        box = BackgroundRectangle(formula, buff=0.25, fill_opacity=0.85)
        self.play(FadeIn(box), Write(formula[0]))
        self.wait(0.5)
        self.play(Write(formula[1]))
        self.play(Write(formula[2]))
        formula[2][-7:].set_color(ANS_COL)
        self.wait(1)
        cap3 = caption("That's Pythagoras: the x-move and y-move are the two short sides of a right triangle.", size=30)
        self.play(FadeTransform(new_cap, cap3))
        self.wait(3)
        self.play(*map(FadeOut, self.mobjects))


class ThreeDimensions(XYZScene):
    def construct(self):
        head = heading("3D: add z, and things can be above the ground")
        axes = make_axes(x_range=(0, 5, 1), y_range=(0, 4, 1), z_range=(0, 3, 1),
                         width=5, height=4, depth=3)
        floor = NumberPlane(x_range=(0, 5, 1), y_range=(0, 4, 1), width=5, height=4,
                            background_line_style=dict(stroke_color=GREY_D, stroke_width=1))
        floor.axes.set_opacity(0)
        floor.shift(axes.get_origin() - floor.get_origin())
        world = Group(floor, axes)
        world.center()

        z_axis = axes.z_axis
        self.add(head, floor, axes)
        self.remove(z_axis)
        self.frame.reorient(0, 0, 0, center=axes.c2p(2.5, 2, 0), height=6.8)
        x_lab, y_lab, _ = self.axis_labels3d(axes)
        z_lab = self.label3d(R"z\ (\text{up})", axes.z_axis.get_end(),
                             size=40, offset=0.8 * LEFT, color=Z_COL)
        self.add(x_lab, y_lab)
        self.wait(0.5)

        cap = caption("A flat map can't tell a drone from the ground below it. We need a third direction.")
        self.play(FadeIn(cap))
        self.play(
            self.frame.animate.reorient(-35, 68, 0, center=axes.c2p(2.4, 2, 1.1), height=6.8),
            run_time=3,
        )
        self.play(ShowCreation(z_axis), run_time=1.5)
        self.play(FadeIn(z_lab))

        cap2 = caption("A drone hovers 4 m east, 3 m north and 2 m up.  Its address is (4, 3, 2).")
        self.play(FadeTransform(cap, cap2))
        legs = self.path_legs(axes, (4, 3, 2))
        for leg in legs:
            self.play(ShowCreation(leg), run_time=1)
        drone = ball(axes.c2p(4, 3, 2), radius=0.12)
        shadow = Circle(radius=0.12, color=GREY_B, fill_opacity=0.6, stroke_width=0).move_to(axes.c2p(4, 3, 0))
        lab = self.label3d(R"(4,\ 3,\ 2)", axes.c2p(4, 3, 2), offset=0.85 * RIGHT)
        lab[1].set_color(X_COL)
        lab[3].set_color(Y_COL)
        lab[5].set_color(Z_COL)
        self.play(GrowFromCenter(drone), FadeIn(shadow), Write(lab))
        self.wait()

        cap3 = caption("Same idea as before, just one more term under the square root:")
        self.play(FadeTransform(cap2, cap3))
        diag = Line(axes.get_origin(), axes.c2p(4, 3, 2), color=ANS_COL, stroke_width=6)
        self.play(ShowCreation(diag))

        formula = VGroup(
            Tex(R"d = \sqrt{x^2 + y^2 + z^2}", font_size=44),
            Tex(R"= \sqrt{16 + 9 + 4}", font_size=44),
            Tex(R"= \sqrt{29} \approx 5.39 \text{ m}", font_size=44),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        colored_xyz(formula[0])
        formula.to_corner(UR).shift(0.9 * DOWN)
        formula.fix_in_frame()
        box = BackgroundRectangle(formula, buff=0.25, fill_opacity=0.85).fix_in_frame()
        self.play(FadeIn(box), Write(formula[0]))
        self.play(Write(formula[1]))
        self.play(Write(formula[2]))
        self.wait(1.5)

        cap4 = caption("Change any one number and the drone moves along exactly one axis.")
        self.play(FadeTransform(cap3, cap4))
        self.play(FadeOut(lab), FadeOut(diag), FadeOut(legs), FadeOut(head))
        z_t = ValueTracker(2)
        drone.add_updater(lambda m: m.move_to(axes.c2p(4, 3, z_t.get_value())))
        stalk = always_redraw(lambda: DashedLine(axes.c2p(4, 3, 0), axes.c2p(4, 3, z_t.get_value()),
                                                 color=Z_COL, stroke_width=4))
        self.add(stalk)
        self.play(z_t.animate.set_value(3), run_time=1.2)
        self.play(z_t.animate.set_value(0.6), run_time=1.5)
        self.play(z_t.animate.set_value(2), run_time=1)
        self.play(self.frame.animate.reorient(20, 72, 0), run_time=4)
        self.wait()
        self.play(*map(FadeOut, self.mobjects))


def question_card(number, lines, size=36):
    tag = T(f"Question {number}", font_size=44, weight=BOLD, color=ANS_COL)
    body = VGroup(*(T(l, font_size=size) for l in lines)).arrange(DOWN, buff=0.25)
    timer = T("Pause the video and try it!", font_size=28, color=GREY_B, slant=ITALIC)
    return VGroup(tag, body, timer).arrange(DOWN, buff=0.6)


class QuestionDrone(XYZScene):
    def construct(self):
        card = question_card(1, [
            "A delivery drone takes off from the roof point A(1, 2, 0)",
            "and flies in a straight line to a balcony at B(4, 6, 12).",
            "Distances are in metres. How far does it fly?",
        ])
        self.play(FadeIn(card, shift=UP))
        self.wait(4)
        self.play(FadeOut(card))

        axes = make_axes(x_range=(0, 5, 1), y_range=(0, 7, 1), z_range=(0, 12, 2),
                         width=4, height=5.6, depth=5.4, numbers=False)
        axes.center()
        self.frame.reorient(-50, 70, 0, center=axes.c2p(2.5, 3.5, 5.0), height=10.4)
        labels = VGroup(self.axis_labels3d(axes), self.z_numbers3d(axes, range(2, 13, 2)))
        self.play(FadeIn(axes), FadeIn(labels))

        A, B = (1, 2, 0), (4, 6, 12)
        pa, pb = axes.c2p(*A), axes.c2p(*B)
        dot_a, dot_b = ball(pa, color=WHITE), ball(pb, color=WHITE)
        lab_a = self.label3d(R"A(1,\ 2,\ 0)", pa, size=36, offset=0.45 * RIGHT + 0.2 * DOWN)
        lab_b = self.label3d(R"B(4,\ 6,\ 12)", pb, size=36, offset=0.4 * UP)
        self.play(GrowFromCenter(dot_a), GrowFromCenter(dot_b), Write(lab_a), Write(lab_b))

        # Break the flight into one move along each axis
        c1 = axes.c2p(4, 2, 0)
        c2 = axes.c2p(4, 6, 0)
        legs = VGroup(
            DashedLine(pa, c1, color=X_COL, stroke_width=5),
            DashedLine(c1, c2, color=Y_COL, stroke_width=5),
            DashedLine(c2, pb, color=Z_COL, stroke_width=5),
        )
        diffs = VGroup(
            Tex(R"\Delta x = 4 - 1 = 3", font_size=40),
            Tex(R"\Delta y = 6 - 2 = 4", font_size=40),
            Tex(R"\Delta z = 12 - 0 = 12", font_size=40),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        for d, col in zip(diffs, (X_COL, Y_COL, Z_COL)):
            d.set_color(col)
        diffs.to_corner(UL).shift(0.2 * DOWN)
        diffs.set_backstroke(BLACK, 5)
        diffs.fix_in_frame()

        cap = caption("Step 1: how much does each coordinate change?")
        self.play(FadeIn(cap))
        for leg, d in zip(legs, diffs):
            self.play(ShowCreation(leg), Write(d), run_time=1.2)
        self.wait()

        flight = Line(pa, pb, color=ANS_COL, stroke_width=6)
        cap2 = caption("Step 2: plug the changes into the 3D distance formula.")
        self.play(FadeTransform(cap, cap2), ShowCreation(flight))

        formula = VGroup(
            Tex(R"d = \sqrt{(\Delta x)^2 + (\Delta y)^2 + (\Delta z)^2}", font_size=40),
            Tex(R"= \sqrt{3^2 + 4^2 + 12^2}", font_size=40),
            Tex(R"= \sqrt{9 + 16 + 144} = \sqrt{169}", font_size=40),
            Tex(R"= 13 \text{ m}", font_size=52).set_color(ANS_COL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        colored_xyz(formula[0])
        formula.to_corner(UR).shift(0.2 * DOWN)
        formula.fix_in_frame()
        box = BackgroundRectangle(formula, buff=0.2, fill_opacity=0.85).fix_in_frame()
        self.play(FadeIn(box), Write(formula[0]))
        for part in formula[1:]:
            self.play(Write(part))
        self.wait()
        cap3 = caption("Answer: 13 m, even though the drone climbed 12 m and drifted only 5 m sideways.", size=30)
        self.play(FadeTransform(cap2, cap3))
        self.play(self.frame.animate.reorient(-38, 72, 0), run_time=3)
        self.wait(2)
        self.play(*map(FadeOut, self.mobjects))


class QuestionHill(XYZScene):
    def construct(self):
        card = question_card(2, [
            "A hill's height (in hundreds of metres) is",
            "z = 4 − (x² + y²) / 4",
            "How high is a hiker standing at x = 2, y = 2?",
        ])
        self.play(FadeIn(card, shift=UP))
        self.wait(4)
        self.play(FadeOut(card))

        axes = make_axes(x_range=(-4, 4, 1), y_range=(-4, 4, 1), z_range=(0, 4.5, 1),
                         width=6, height=6, depth=3.4, numbers=False)
        self.frame.reorient(-40, 66, 0, center=axes.c2p(0, 0, 1.6), height=7.4)
        labels = VGroup(self.axis_labels3d(axes), self.z_numbers3d(axes, range(1, 5)))
        self.play(FadeIn(axes), FadeIn(labels))

        def f(x, y):
            return 4 - (x * x + y * y) / 4

        # Parametrise by polar coordinates so the hill sits exactly on the ground (z = 0 at r = 4)
        hill = axes.get_parametric_surface(
            lambda r, t: [r * np.cos(t), r * np.sin(t), 4 - r * r / 4],
            u_range=(0, 4), v_range=(0, TAU), resolution=(41, 81),
            color=GREEN_E, opacity=0.5,
        )
        cap = caption("z = f(x, y): every spot (x, y) on the map gets its own height z.")
        self.play(FadeIn(cap), ShowCreation(hill), run_time=2.5)

        foot = axes.c2p(2, 2, 0)
        top = axes.c2p(2, 2, f(2, 2))
        ground_legs = VGroup(
            DashedLine(axes.c2p(0, 0, 0), axes.c2p(2, 0, 0), color=X_COL, stroke_width=5),
            DashedLine(axes.c2p(2, 0, 0), foot, color=Y_COL, stroke_width=5),
        )
        pole = Line(foot, top, color=Z_COL, stroke_width=6)
        hiker = ball(top, radius=0.16)
        # Draw the answer on top of the translucent hill so it never hides behind it
        for mob in (ground_legs, pole, hiker):
            mob.deactivate_depth_test()
        self.play(ShowCreation(ground_legs[0]), ShowCreation(ground_legs[1]))
        self.play(ShowCreation(pole), GrowFromCenter(hiker))

        formula = VGroup(
            Tex(R"z = 4 - \frac{x^2 + y^2}{4}", font_size=42),
            Tex(R"= 4 - \frac{2^2 + 2^2}{4}", font_size=42),
            Tex(R"= 4 - 2 = 2", font_size=42),
            Tex(R"\Rightarrow 200 \text{ m high}", font_size=46).set_color(ANS_COL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        colored_xyz(formula[0])
        formula.to_corner(UL).shift(0.3 * DOWN)
        formula.fix_in_frame()
        box = BackgroundRectangle(formula, buff=0.2, fill_opacity=0.85).fix_in_frame()
        self.play(FadeIn(box), Write(formula[0]))
        for part in formula[1:]:
            self.play(Write(part))
        cap2 = caption("x and y say WHERE on the map; the formula turns them into z, the height.")
        self.play(FadeTransform(cap, cap2))
        self.play(self.frame.animate.reorient(40, 70, 0), run_time=5)
        self.wait(1.5)
        self.play(*map(FadeOut, self.mobjects))


class QuestionWifi(XYZScene):
    def construct(self):
        card = question_card(3, [
            "A Wi-Fi router at (0, 0, 0) reaches 5 m in every direction.",
            "Your phone is at (3, 4, 1). Do you have signal?",
        ])
        self.play(FadeIn(card, shift=UP))
        self.wait(4)
        self.play(FadeOut(card))

        u = 0.55
        axes = make_axes(x_range=(-6, 6, 1), y_range=(-6, 6, 1), z_range=(-6, 6, 1),
                         width=12 * u, height=12 * u, depth=12 * u, numbers=False)
        self.frame.reorient(-35, 70, 0, center=ORIGIN, height=7.6)
        labels = self.axis_labels3d(axes)
        self.play(FadeIn(axes), FadeIn(labels))

        cap = caption("All points exactly 5 m away form a sphere:  x² + y² + z² = 5² = 25")
        sphere = Sphere(radius=5 * u, color=BLUE_E, opacity=0.18)
        mesh = SurfaceMesh(sphere, resolution=(13, 9))
        mesh.set_stroke(BLUE_B, 1, opacity=0.35)
        router = ball(axes.c2p(0, 0, 0), color=WHITE, radius=0.1)
        self.play(FadeIn(cap), GrowFromCenter(router))
        self.play(ShowCreation(sphere), ShowCreation(mesh), run_time=2)

        phone_p = axes.c2p(3, 4, 1)
        legs = self.path_legs(axes, (3, 4, 1))
        for leg in legs:
            self.play(ShowCreation(leg), run_time=0.7)
        phone = ball(phone_p, color=RED, radius=0.15)
        lab = self.label3d(R"\text{phone }(3,\ 4,\ 1)", phone_p, size=40, offset=0.45 * UP)
        for mob in (legs, phone, lab):
            mob.deactivate_depth_test()
        self.play(GrowFromCenter(phone), Write(lab))

        formula = VGroup(
            Tex(R"x^2 + y^2 + z^2", font_size=42),
            Tex(R"= 3^2 + 4^2 + 1^2", font_size=42),
            Tex(R"= 9 + 16 + 1 = 26", font_size=42),
            Tex(R"26 > 25", font_size=46).set_color(RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        colored_xyz(formula[0])
        formula.to_corner(UL).shift(0.3 * DOWN)
        formula.fix_in_frame()
        box = BackgroundRectangle(formula, buff=0.2, fill_opacity=0.85).fix_in_frame()
        cap2 = caption("Compare x² + y² + z² with 25: less means inside, more means outside.")
        self.play(FadeTransform(cap, cap2), FadeIn(box), Write(formula[0]))
        for part in formula[1:]:
            self.play(Write(part))
        cap3 = caption("Just outside! √26 ≈ 5.10 m. Step 0.1 m closer and the signal comes back.", size=32)
        self.play(FadeTransform(cap2, cap3))
        self.play(self.frame.animate.reorient(10, 80, 0), run_time=4)
        self.wait(2)
        self.play(*map(FadeOut, self.mobjects))


class Outro(XYZScene):
    def construct(self):
        head = T("Where x, y, z show up in real life", font_size=46, weight=BOLD)
        head.to_edge(UP)
        rows = VGroup(
            T("GPS & maps:  x, y = position, z = altitude", font_size=32),
            T("3D printers & CNC machines:  move the nozzle to (x, y, z)", font_size=32),
            T("Video games & animation:  every object has an (x, y, z)", font_size=32),
            T("Architecture & CAD:  walls, floors, heights", font_size=32),
            T("Physics:  a ball's position over time, (x(t), y(t), z(t))", font_size=32),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        rows.next_to(head, DOWN, buff=0.6)
        self.play(FadeIn(head))
        for row in rows:
            self.play(FadeIn(row, shift=0.3 * RIGHT), run_time=0.7)
        note = T(
            "Heads-up: some tools (Minecraft, Unity) call the up direction y instead of z.\n"
            "The math is the same, only the names change.",
            font_size=26, color=GREY_B,
        )
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note))
        self.wait(4)

        summary = VGroup(
            Tex(R"\text{2D distance: } d = \sqrt{x^2 + y^2}", font_size=44),
            Tex(R"\text{3D distance: } d = \sqrt{x^2 + y^2 + z^2}", font_size=44),
            Tex(R"\text{Surface: } z = f(x, y)", font_size=44),
            Tex(R"\text{Sphere: } x^2 + y^2 + z^2 = r^2", font_size=44),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        for s in summary:
            colored_xyz(s)
        recap = T("The four formulas from this video", font_size=40, weight=BOLD).to_edge(UP)
        self.play(FadeOut(VGroup(rows, note)), FadeTransform(head, recap))
        self.play(LaggedStartMap(FadeIn, summary, lag_ratio=0.3), run_time=2.5)
        self.wait(4)
        self.play(FadeOut(VGroup(recap, summary)))
