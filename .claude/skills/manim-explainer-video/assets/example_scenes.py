"""
Minimal working example of the three scene patterns an explainer usually needs.
Copy next to manim_kit.py and render a preview with:
    bash render.sh example_scenes.py "Concept2D Concept3D Question" -l
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # manimgl doesn't add the script dir
from manim_kit import *  # noqa: E402,F403


class Concept2D(KitScene):
    """Flat diagram: build it up piece by piece, one narration sentence per step."""

    def construct(self):
        head = heading("Distance on a map")
        axes = make_axes(x_range=(0, 5, 1), y_range=(0, 4, 1), width=6, height=4.8)
        axes.z_axis.set_opacity(0)
        axes.center().shift(0.3 * DOWN)

        self.say("Here is a map with an x axis going east and a y axis going north.")
        self.play(FadeIn(head), ShowCreation(axes))
        self.wait_voice()

        p = axes.c2p(4, 3, 0)
        legs = self.path_legs(axes, (4, 3, 0))[:2]
        dot = Dot(p, radius=0.12, color=ANS_COL)
        self.say("A shop four blocks east and three blocks north sits at the point four, three.")
        self.play(ShowCreation(legs[0]))
        self.play(ShowCreation(legs[1]), GrowFromCenter(dot))
        self.wait_voice()

        steps, box = formula_block([R"d = \sqrt{x^2 + y^2}", R"= \sqrt{16 + 9} = 5"], corner=UR, shift=DOWN)
        color_symbols(steps[0])
        self.say("By Pythagoras, the straight-line distance is the square root of sixteen plus nine, which is five.")
        self.play(ShowCreation(Line(axes.get_origin(), p, color=ANS_COL)), FadeIn(box), Write(steps[0]))
        self.play(Write(steps[1]))
        self.wait_voice(0.5)
        self.play(*map(FadeOut, self.mobjects))


class Concept3D(KitScene):
    """3D: set the camera FIRST, then create camera-facing labels, then animate."""

    def construct(self):
        axes = make_axes(x_range=(0, 5, 1), y_range=(0, 4, 1), z_range=(0, 3, 1),
                         width=5, height=4, depth=3, numbers=False)
        axes.center()
        # Frame on the content: center= a point in the middle of what you show, height= ~6-8 to fill the screen
        self.frame.reorient(-35, 68, 0, center=axes.c2p(2.4, 2, 1.1), height=6.8)
        labels = self.axis_labels3d(axes)
        cap = caption("A point in space needs three numbers.")

        self.say("In three dimensions, a point needs three numbers: east, north, and up.")
        self.play(FadeIn(axes), FadeIn(labels), FadeIn(cap))
        self.wait_voice()

        pt = axes.c2p(4, 3, 2)
        legs = self.path_legs(axes, (4, 3, 2))
        marker = ball(pt)
        lab = self.label3d(R"(4,\ 3,\ 2)", pt, offset=0.8 * RIGHT)
        self.say("Four along x, three along y, and two up.")
        for leg in legs:
            self.play(ShowCreation(leg), run_time=0.8)
        self.play(GrowFromCenter(marker), Write(lab))
        self.wait_voice()

        # Camera moves are fine: label3d keeps every label readable while the view rotates
        self.play(self.frame.animate.reorient(20, 72, 0), run_time=4)
        self.play(*map(FadeOut, self.mobjects))


class Question(KitScene):
    """Practice question: card + pause, then a worked solution with the visual and the algebra side by side."""

    def construct(self):
        card = question_card(1, ["A drone flies from (0, 0, 0) to (2, 3, 6).", "How far does it fly?"])
        self.say("Question one. A drone flies from the origin to the point two, three, six. "
                 "How far does it fly? Pause the video and give it a try.")
        self.play(FadeIn(card, shift=UP))
        self.wait_voice(2)          # extra seconds for the viewer to pause
        self.play(FadeOut(card))

        axes = make_axes(x_range=(0, 3, 1), y_range=(0, 4, 1), z_range=(0, 7, 1),
                         width=3, height=4, depth=4.5, numbers=False)
        axes.center()
        self.frame.reorient(-45, 70, 0, center=axes.c2p(1.5, 2, 3), height=8.5)
        steps, box = formula_block([
            R"d = \sqrt{x^2 + y^2 + z^2}",
            R"= \sqrt{4 + 9 + 36}",
            R"= \sqrt{49} = 7",
        ])
        color_symbols(steps[0])
        steps[2].set_color(ANS_COL)
        flight = Line(axes.c2p(0, 0, 0), axes.c2p(2, 3, 6), color=ANS_COL, stroke_width=6)

        self.say("Use the 3D distance formula.")
        self.play(FadeIn(axes), FadeIn(self.axis_labels3d(axes)), ShowCreation(flight))
        self.play(FadeIn(box), Write(steps[0]))
        self.wait_voice()
        self.say("Four plus nine plus thirty-six is forty-nine, and the square root of forty-nine is seven.")
        self.play(Write(steps[1]))
        self.play(Write(steps[2]))
        self.wait_voice(1)
        self.play(*map(FadeOut, self.mobjects))
