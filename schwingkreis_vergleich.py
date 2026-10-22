"""Synchronous animation of an ideal LC circuit and a spring oscillator."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
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
        self.fig = plt.figure(figsize=(13.5, 7.5))
        self.fig.suptitle("Elektrischer Schwingkreis und Federschwinger", fontsize=16)
        gs = self.fig.add_gridspec(1, 3, left=.045, right=.98, top=.86,
                                   bottom=.25, width_ratios=[1.15, 1.6, 1.3], wspace=.26)
        self.ax_l = self.fig.add_subplot(gs[0, 0])
        self.ax_e = self.fig.add_subplot(gs[0, 1])
        self.ax_r = self.fig.add_subplot(gs[0, 2])
        for ax in (self.ax_l, self.ax_r):
            ax.set_xlim(0, 10)
            ax.set_ylim(-4, 4)
            ax.set_aspect("equal")
            ax.axis("off")
        self.ax_l.set_title("LC-Schwingkreis")
        self.ax_r.set_title("Federpendel")
        self.setup_circuit()
        self.setup_energy()
        self.setup_spring()
        self.status = self.fig.text(.5, .20, "", ha="center", fontsize=11)
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
        a.plot([1, 3], [2, 2], color="black", lw=2)
        a.plot([3, 3], [2, .45], color="black", lw=2)
        a.plot([2.4, 3.6], [.45, .45], color="black", lw=3)
        a.plot([2.4, 3.6], [-.45, -.45], color="black", lw=3)
        a.plot([3, 3], [-.45, -2], color="black", lw=2)
        a.plot([1, 3], [-2, -2], color="black", lw=2)
        a.plot([1, 1], [-2, 2], color="black", lw=2)
        a.plot([1, 6.3], [2, 2], color="black", lw=2, alpha=0)  # layout anchor
        a.plot([3, 7], [2, 2], color="black", lw=2)
        a.plot([3, 7], [-2, -2], color="black", lw=2)
        a.plot([7, 7], [2, 1.25], color="black", lw=2)
        a.plot([7, 7], [-1.25, -2], color="black", lw=2)
        yy = np.linspace(-1.25, 1.25, 350)
        a.plot(7 + .48 * np.sin(np.linspace(0, 12 * np.pi, len(yy))), yy,
               color="black", lw=2)
        self.plus = a.text(3.9, .75, "+", color=BLUE, fontsize=22, fontweight="bold")
        self.minus = a.text(3.9, -.95, "-", color=BLUE, fontsize=22, fontweight="bold")
        self.charge_text = a.text(3, -3.0, "", ha="center", color=BLUE, fontsize=11)
        self.current_text = a.text(7, -3.0, "", ha="center", color=RED, fontsize=11)
        self.flux = a.text(8, 0, "", ha="center", color=RED, fontsize=10)
        self.arrow = None

    def setup_energy(self):
        a = self.ax_e
        t = np.linspace(0, 2 * PERIOD, 500)
        a.plot(t, np.cos(OMEGA * t) ** 2, color=BLUE, lw=2,
               label=r"$E_{el}/E_{ges}$")
        a.plot(t, np.sin(OMEGA * t) ** 2, color=RED, lw=2,
               label=r"$E_{mag}/E_{ges}$")
        a.axhline(1, color=GREEN, lw=1, ls="--", label=r"$E_{ges}$")
        self.cursor = a.axvline(0, color="black", lw=1.5)
        self.el_point, = a.plot([0], [1], "o", color=BLUE)
        self.mag_point, = a.plot([0], [0], "o", color=RED)
        a.set(xlim=(0, 2 * PERIOD), ylim=(-.07, 1.12),
              xlabel="Zeit / eine Schwingungsdauer T = 8 s",
              ylabel="Relative Energie")
        a.set_xticks([0, PERIOD/4, PERIOD/2, 3*PERIOD/4, PERIOD,
                      5*PERIOD/4, 3*PERIOD/2, 7*PERIOD/4, 2*PERIOD])
        a.set_xticklabels(["0", "T/4", "T/2", "3T/4", "T",
                           "5T/4", "3T/2", "7T/4", "2T"])
        a.grid(alpha=.2)
        a.legend(fontsize=9, loc="upper right")

    def setup_spring(self):
        a = self.ax_r
        a.plot([.7, .7], [-1, 1], color="black", lw=5)
        for y in np.linspace(-1, 1, 10):
            a.plot([.5, .7], [y-.2, y], color="gray", lw=1)
        a.axvline(6, color="gray", ls="--", lw=1)
        a.text(6, -2.3, "Gleichgewicht", ha="center", fontsize=9)
        self.spring_line, = a.plot([], [], color="black", lw=2)
        self.mass = Circle((8, 0), .45, color="#333333", zorder=4)
        a.add_patch(self.mass)
        self.spring_text = a.text(5, 2.3, "", ha="center", fontsize=11)
        self.velocity = a.annotate("", xy=(8, 1), xytext=(8, 1),
                                   arrowprops=dict(arrowstyle="->", color=RED, lw=2))
        self.position = a.annotate("", xy=(6, -1), xytext=(6, -1),
                                   arrowprops=dict(arrowstyle="->", color=BLUE, lw=2))

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
        self.charge_text.set_text(f"Ladung q/qmax = {q:+.2f}")
        self.current_text.set_text(f"Strom I/Imax = {current:+.2f}")
        self.flux.set_text("B-Feld: " + ("stark" if abs(current) > .65 else "schwach"))
        if self.arrow is not None:
            self.arrow.remove()
        if abs(current) > .05:
            sign = 1 if current > 0 else -1
            self.arrow = FancyArrowPatch((5, 2.7), (5 + sign*1.2, 2.7),
                                          arrowstyle="-|>", color=RED, mutation_scale=15, lw=2)
            self.ax_l.add_patch(self.arrow)
        time = (p / OMEGA)
        self.cursor.set_xdata([time, time])
        self.el_point.set_data([time], [q*q])
        self.mag_point.set_data([time], [current*current])
        x = 6 + 2 * q
        xs = np.linspace(.7, x-.45, 180)
        ys = .4 * np.sin(np.linspace(0, 16*np.pi, len(xs)))
        ys[0], ys[-1] = 0, 0
        self.spring_line.set_data(xs, ys)
        self.mass.center = (x, 0)
        self.spring_text.set_text(f"s/A = {q:+.2f}     v/vmax = {-current:+.2f}")
        v = -current
        self.velocity.xy = (x + 1.5*v, 1)
        self.velocity.set_position((x, 1))
        self.position.xy = (x, -1.1)
        self.position.set_position((6, -1.1))
        self.status.set_text(
            f"Phase: {np.degrees(p):.0f} Grad     "
            f"Elektrische Energie: {100*q*q:.0f} %     "
            f"Magnetische Energie: {100*current*current:.0f} %")
        if abs(self.time_slider.val-p) > .002:
            self.dragging = True
            self.time_slider.set_val(p)
            self.dragging = False
        return ()

if __name__ == "__main__":
    Comparison()
