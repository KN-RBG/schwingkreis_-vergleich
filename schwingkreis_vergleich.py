"""Synchronous animation of an ideal LC circuit and a spring oscillator."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.widgets import Button, Slider

# The models are scaled to the same angular frequency.
PERIOD = 8.0
OMEGA = 2 * np.pi / PERIOD
BLUE = "#2473d4"
RED = "#dc5046"
GREEN = "#248866"

class Comparison:
    def __init__(self):
        self.phase = 0.0
        self.playing = True
        self.speed = 1.0
        self.dragging = False
        self.fig = plt.figure(figsize=(15, 8.2))
        self.fig.suptitle("Elektrischer Schwingkreis und Federschwinger", fontsize=16)
        gs = self.fig.add_gridspec(1, 3, left=.045, right=.98, top=.87,
                                   bottom=.28, width_ratios=[1.15, 1.6, 1.3], wspace=.3)
        self.ax_l = self.fig.add_subplot(gs[0, 0])
        self.ax_e = self.fig.add_subplot(gs[0, 1])
        self.ax_r = self.fig.add_subplot(gs[0, 2])
        for ax in (self.ax_l, self.ax_r):
            ax.set_xlim(0, 10)
            ax.set_ylim(-4, 4)
            ax.set_aspect("equal")
            ax.axis("off")
        self.ax_l.set_title("LC-Schwingkreis")
        self.ax_r.set_title("Horizontaler Federschwinger")
        self.setup_circuit()
        self.setup_energy()
        self.setup_spring()
        play_ax = self.fig.add_axes([.09, .09, .13, .055])
        self.btn = Button(play_ax, "Pause")
        self.btn.on_clicked(self.toggle)
        step_l = Button(self.fig.add_axes([.24, .09, .075, .055]), "<")
        step_r = Button(self.fig.add_axes([.325, .09, .075, .055]), ">")
        step_l.on_clicked(lambda event: self.step(-1))
        step_r.on_clicked(lambda event: self.step(1))
        self.time_slider = Slider(self.fig.add_axes([.49, .115, .37, .024]),
                                  "Phase", 0, 2 * np.pi, valinit=0)
        self.time_slider.on_changed(self.seek)
        self.speed_slider = Slider(self.fig.add_axes([.49, .061, .37, .024]),
                                   "Tempo", .1, 3, valinit=1)
        self.speed_slider.on_changed(lambda v: setattr(self, "speed", v))
        self.animate(None)
        self.anim = FuncAnimation(self.fig, self.animate, interval=35,
                                  blit=False, cache_frame_data=False)
        plt.show()

    def setup_circuit(self):
        a = self.ax_l
        # Wires and capacitor (upper and lower nodes, no wire across gap).
        a.plot([3, 3], [2, .45], color="black", lw=2)
        a.plot([2.4, 3.6], [.45, .45], color="black", lw=3)
        a.plot([2.4, 3.6], [-.45, -.45], color="black", lw=3)
        a.plot([3, 3], [-.45, -2], color="black", lw=2)
        a.plot([3, 7], [2, 2], color="black", lw=2)
        a.plot([3, 7], [-2, -2], color="black", lw=2)
        a.plot([7, 7], [2, 1.25], color="black", lw=2)
        a.plot([7, 7], [-1.25, -2], color="black", lw=2)
        yy = np.linspace(-1.25, 1.25, 350)
        a.plot(7 + .48 * np.sin(np.linspace(0, 12 * np.pi, len(yy))), yy,
               color="black", lw=2)
        self.plus = a.text(3.9, .75, "+", color=BLUE, fontsize=22, fontweight="bold")
        self.minus = a.text(3.9, -.95, "-", color=BLUE, fontsize=22, fontweight="bold")
        self.charge_text = a.text(0.8, -3.0, "", ha="left", color=BLUE, fontsize=9)
        self.current_text = a.text(9.2, -3.5, "", ha="right", color=RED, fontsize=9)
        self.cap_field_arrows = []
        self.coil_field_arrows = []
        self.arrow = None
        self.current_arrow_label = a.text(
            5.0, 3.0, r"$I$", ha="center", va="bottom",
            color=RED, fontsize=11, visible=False
        )

    def setup_energy(self):
        a = self.ax_e
        t = np.linspace(0, 2 * PERIOD, 500)
        a.plot(t, np.cos(OMEGA * t) ** 2, color=BLUE, lw=2,
               label=r"$E_{\mathrm{el}}/E_{\mathrm{ges}}$")
        a.plot(t, np.sin(OMEGA * t) ** 2, color=RED, lw=2,
               label=r"$E_{\mathrm{mag}}/E_{\mathrm{ges}}$")
        a.axhline(1, color=GREEN, lw=1, ls="--", label=r"$E_{\mathrm{ges}}$")
        self.cursor = a.axvline(0, color="black", lw=1.5)
        self.el_point, = a.plot([0], [1], "o", color=BLUE)
        self.mag_point, = a.plot([0], [0], "o", color=RED)
        a.set(xlim=(0, 2 * PERIOD), ylim=(-.07, 1.12),
              xlabel=r"Zeit / Schwingungsdauer $T = 8\,\mathrm{s}$",
              ylabel="Relative Energie")
        a.set_xticks([0, PERIOD/4, PERIOD/2, 3*PERIOD/4, PERIOD,
                      5*PERIOD/4, 3*PERIOD/2, 7*PERIOD/4, 2*PERIOD])
        a.set_xticklabels(["0", r"$T/4$", r"$T/2$", r"$3T/4$", r"$T$",
                           r"$5T/4$", r"$3T/2$", r"$7T/4$", r"$2T$"])
        a.grid(alpha=.2)
        # Mechanical and electrical energy pairs follow identical curves.
        legend_handles = [
            Line2D([0], [0], color=BLUE, lw=2,
                   label=r"$E_{\mathrm{el}}$ (Kondensator)"),
            Line2D([0], [0], color=BLUE, lw=2, ls="--",
                   label=r"$E_{\mathrm{Spann}}$ (Federn)"),
            Line2D([0], [0], color=RED, lw=2,
                   label=r"$E_{\mathrm{mag}}$ (Spule)"),
            Line2D([0], [0], color=RED, lw=2, ls="--",
                   label=r"$E_{\mathrm{kin}}$ (Masse)"),
            Line2D([0], [0], color=GREEN, lw=1, ls="--",
                   label=r"$E_{\mathrm{ges}}$"),
        ]
        a.legend(handles=legend_handles, fontsize=9, loc="upper right")

    def setup_spring(self):
        a = self.ax_r
        for wall in (.8, 9.2):
            a.plot([wall, wall], [-1, 1], color="black", lw=4)
        a.axvline(5, color="gray", ls="--", lw=1)
        a.text(5, -2.35, "Gleichgewichtslage", ha="center", fontsize=9)
        self.left_spring, = a.plot([], [], color="black", lw=2)
        self.right_spring, = a.plot([], [], color="black", lw=2)
        self.mass = Circle((7, 0), .42, color="#333333", zorder=4)
        a.add_patch(self.mass)
        self.spring_text = a.text(5, 2.3, "", ha="center", fontsize=10)
        self.velocity = a.annotate("", xy=(7, 1), xytext=(7, 1),
                                   arrowprops=dict(arrowstyle="->", color=RED, lw=2))
        self.position = a.annotate("", xy=(5, -1.1), xytext=(5, -1.1),
                                   arrowprops=dict(arrowstyle="->", color=BLUE, lw=2))

    @staticmethod
    def spring_shape(start, end):
        xs = np.linspace(start, end, 180)
        ys = .3 * np.sin(np.linspace(0, 16*np.pi, len(xs)))
        ys[0] = ys[-1] = 0
        return xs, ys

    def draw_fields(self, charge, current):
        for arrow in self.cap_field_arrows + self.coil_field_arrows:
            arrow.remove()
        self.cap_field_arrows.clear()
        self.coil_field_arrows.clear()
        n_e = round(6 * abs(charge))
        if n_e:
            for x in np.linspace(2.55, 3.45, n_e):
                start, end = ((x, .32), (x, -.32)) if charge > 0 else ((x, -.32), (x, .32))
                arr = FancyArrowPatch(start, end, arrowstyle="->", color=BLUE,
                                      mutation_scale=9, lw=1.3)
                self.ax_l.add_patch(arr)
                self.cap_field_arrows.append(arr)
        # Curved, closed magnetic field lines surrounding the coil.
        # Their number represents field strength; arrows indicate direction.
        n_b = round(4 * abs(current))
        for i in range(n_b):
            width = 1.4 + .37 * i
            height = 2.85 + .31 * i
            curve = Ellipse((7, 0), width, height, fill=False,
                            edgecolor=RED, lw=1.35, alpha=.85, zorder=1)
            self.ax_l.add_patch(curve)
            self.coil_field_arrows.append(curve)
            # Tangential arrow at the top of each ellipse.
            theta = np.pi / 2
            delta = .14 * (1 if current > 0 else -1)
            start = (7 + width/2 * np.cos(theta - delta),
                     height/2 * np.sin(theta - delta))
            end = (7 + width/2 * np.cos(theta + delta),
                   height/2 * np.sin(theta + delta))
            arrow = FancyArrowPatch(start, end, arrowstyle="-|>",
                                     color=RED, lw=1.35, mutation_scale=10,
                                     zorder=3)
            self.ax_l.add_patch(arrow)
            self.coil_field_arrows.append(arrow)

    def toggle(self, event):
        self.playing = not self.playing
        self.btn.label.set_text("Pause" if self.playing else "Start")

    def step(self, direction):
        self.playing = False
        self.btn.label.set_text("Start")
        self.phase = (self.phase + direction * np.pi/2) % (2*np.pi)
        self.animate(None)

    def seek(self, value):
        if not self.dragging:
            self.phase = value
            self.playing = False
            self.btn.label.set_text("Start")
            self.animate(None)

    def animate(self, frame):
        if self.playing and frame is not None:
            self.phase = (self.phase + OMEGA * .035 * self.speed) % (2*np.pi)
        p = self.phase
        q = np.cos(p)
        current = np.sin(p)  # Current magnitude, with reference direction chosen.
        self.plus.set_text("+" if q >= 0 else "-")
        self.minus.set_text("-" if q >= 0 else "+")
        self.charge_text.set_text(rf"$q/q_{{\mathrm{{max}}}} = {q:+.2f}$")
        self.current_text.set_text(rf"$I/I_{{\mathrm{{max}}}} = {current:+.2f}$")
        self.draw_fields(q, current)
        if self.arrow is not None:
            if self.arrow.axes is not None:
                self.arrow.remove()
            self.arrow = None
        # Current arrow scales continuously with current magnitude.
        # No arrow is drawn at zero current.
        if abs(current) > 0.02:
            center_x = 5.0
            y_arrow = 2.7
            arrow_len = 1.8 * abs(current)
            direction = 1 if current > 0 else -1
            start = (center_x - direction * arrow_len / 2, y_arrow)
            end = (center_x + direction * arrow_len / 2, y_arrow)
            self.arrow = FancyArrowPatch(
                start, end, arrowstyle="-|>", color=RED,
                mutation_scale=13, lw=2
            )
            self.ax_l.add_patch(self.arrow)
            self.current_arrow_label.set_visible(True)
        else:
            self.current_arrow_label.set_visible(False)
        time = (p / OMEGA)
        self.cursor.set_xdata([time, time])
        self.el_point.set_data([time], [q*q])
        self.mag_point.set_data([time], [current*current])
        x = 5 + 2 * q
        self.left_spring.set_data(*self.spring_shape(.8, x-.42))
        self.right_spring.set_data(*self.spring_shape(x+.42, 9.2))
        self.mass.center = (x, 0)
        self.spring_text.set_text(rf"$s/A = {q:+.2f} \qquad v/v_{{\mathrm{{max}}}} = {-current:+.2f}$")
        self.velocity.xy = (x - 1.5*current, 1)
        self.velocity.set_position((x, 1))
        self.position.xy = (x, -1.1)
        self.position.set_position((5, -1.1))
        if abs(self.time_slider.val-p) > .002:
            self.dragging = True
            self.time_slider.set_val(p)
            self.dragging = False
        return ()

if __name__ == "__main__":
    Comparison()
