"""
Vertical Short (9:16) example. Render with:
    RES=1080x1920 bash render.sh example_short.py "ShortHook ShortPoint3D" -l short.mp4

Portrait rules this file follows:
- The frame is 4.5 units wide and 8 tall. Build for that width; don't shrink a 16:9 layout.
- Stack things vertically: heading (top), visual (middle), formula or number (below), caption (kit places it).
- Keep everything inside the middle ~65% of the height: apps cover the top and bottom.
- One idea per Short, a hook in the first 3 seconds, and big text (font size 40+).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manim_kit import *  # noqa: E402,F403


class ShortHook(KitScene):
    def construct(self):
        hook = T("1% a day\n= 37x", font_size=72, weight=BOLD).set_color(ANS_COL)
        hook.move_to(1.5 * UP)
        self.say("Get one percent better every day, and after a year you're thirty-seven times better.")
        self.play(Write(hook), run_time=1.2)
        self.wait_voice()

        # A growth curve sized for the narrow frame: width = frame width minus margins
        axes = Axes(x_range=(0, 365, 73), y_range=(0, 40, 10),
                    width=FRAME_WIDTH - 0.9, height=3.2,
                    axis_config=dict(include_tip=False, tick_size=0.05))
        axes.move_to(1.3 * DOWN)
        curve = axes.get_graph(lambda d: 1.01 ** d, color=ANS_COL, x_range=(0, 365))
        value = Tex(R"1.01^{365} \approx 37.8", font_size=44)
        fit(value).next_to(axes, UP, buff=0.3)
        self.say("Each day's one percent grows on top of yesterday's.")
        self.play(hook.animate.scale(0.6).to_edge(UP, buff=1.2), ShowCreation(axes))
        self.play(ShowCreation(curve), Write(value), run_time=2.5)
        self.wait_voice(0.5)
        self.play(*map(FadeOut, self.mobjects))


class ShortPoint3D(KitScene):
    def construct(self):
        axes = make_axes(x_range=(0, 4, 1), y_range=(0, 4, 1), z_range=(0, 3, 1),
                         width=4, height=4, depth=3, numbers=False)
        axes.center()
        # frame_on fits ~6.5 units of content across the narrow frame
        self.frame_on(-35, 68, center=axes.c2p(2, 2, 1.2), width=6.5)
        labels = self.axis_labels3d(axes)
        cap = caption("Every point in space is just three numbers: x, y and z.")
        self.say("Every point in space is just three numbers.")
        self.play(FadeIn(axes), FadeIn(labels), FadeIn(cap))
        self.wait_voice()

        pt = (3, 2, 2)
        legs = self.path_legs(axes, pt)
        marker = ball(axes.c2p(*pt), radius=0.14)
        lab = self.label3d(R"(3,\ 2,\ 2)", axes.c2p(*pt), size=44, offset=0.5 * UP)
        self.say("Three along x, two along y, two up.")
        for leg in legs:
            self.play(ShowCreation(leg), run_time=0.7)
        self.play(GrowFromCenter(marker), Write(lab))
        self.wait_voice()
        self.play(self.frame.animate.reorient(15, 72, 0), run_time=3)
