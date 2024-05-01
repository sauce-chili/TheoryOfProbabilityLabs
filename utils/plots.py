from PyQt5.Qt import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import arange


class BasicGraph(FigureCanvas):
    def __init__(self, parent=None, name=None, w=5, h=4, dpi=100, nrc=111):
        fig = Figure(figsize=(w, h), dpi=dpi)
        self.axes = fig.add_subplot(nrc)
        self.axes.grid(True)

        self.name = [name]
        self.axes.set_title(name)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def redo(self, ax, sub, name, xl, yl):
        ax.cla()
        ax.grid(True)

        if name is None:
            ax.set_title(self.name[sub])
        else:
            ax.set_title(name)

        ax.set_xlabel(xl)
        ax.set_ylabel(yl)


class Function(BasicGraph):
    def __init__(self, parent=None, name=None, w=4, h=3, dpi=100):
        BasicGraph.__init__(self, parent, name, w, h, dpi)

    def display(self, func, xl='x', yl='y', color='b', name=None):
        self.redo(self.axes, 0, name, xl, yl)

        for part in func['lines']:
            self.axes.plot(part[0], part[1], color)
        self.axes.plot(func['dotsx'], func['dotsy'], color + 'o')
        self.axes.plot(func['dotsx'], func['dotsy'], 'w.')

        lx = func['lines'][0][0][0]
        rx = func['lines'][-1][0][1]

        self.axes.set_xbound(lx, rx)
        self.axes.set_ybound(0, 1.1)

        self.draw()


class ContinuousFunction(BasicGraph):
    def __init__(self, parent=None, name=None, w=4, h=3, dpi=100):
        BasicGraph.__init__(self, parent, name, w, h, dpi)

    def display(self, func, xl='x', yl='y', color='b', name=None):
        self.redo(self.axes, 0, name, xl, yl)

        self.axes.plot(func[0], func[1], color=color)

        #self.axes.set_xbound(lx, rx)
        #self.axes.set_ybound(0, 1.1)

        self.draw()


class Histogram(BasicGraph):
    def __init__(self, parent=None, name=None, w=5, h=4, dpi=100):
        BasicGraph.__init__(self, parent, name, w, h, dpi)
        self._gap_x = None
        
    def set_x_gap(self, x):
        self._gap_x = x

    def display(self, bounds, h, mids, weights, xl='x', yl='y', color='b', name=None):
        self.redo(self.axes, 0, name, xl, yl)
        intlen = bounds[-1] - bounds[0]
        ws = []
        for i, weight in enumerate(weights):
            if hasattr(h, "__iter__"):
                ws.append(weight / h[i])
            else:
                ws.append(weight / h)
        self.axes.hist(mids, bins=bounds, weights=ws, color=color)

        xticks = list(map(lambda x: round(x, 3), self.axes.get_xticks()))
        xtickslabels = list(map(str, xticks))

        if self._gap_x:
            xticks.insert(0, self._gap_x)
            xtickslabels.insert(0, "≈")
            if '0.0' not in xtickslabels and '0' not in xtickslabels:
                xticks.insert(0, self._gap_x - (self._gap_x / 5))
                xtickslabels.insert(0, "0")
            
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xtickslabels)

        self.draw()


class PolygonHistogramContinuous(BasicGraph):
    def __init__(self, parent=None, name=None, w=5, h=4, dpi=100):
        BasicGraph.__init__(self, parent, name, w, h, dpi)
        self._gap_x = None

    def set_x_gap(self, x):
        self._gap_x = x

    def display(self, func, bounds, h, mids, weights, xl='x', yl='y', color='b', name=None):
        self.redo(self.axes, 0, name, xl, yl)
        intlen = bounds[-1] - bounds[0]
        ws = []
        for i, weight in enumerate(weights):
            if hasattr(h, "__iter__"):
                ws.append(weight / h[i])
            else:
                ws.append(weight / h)
        self.axes.hist(mids, bins=bounds, weights=ws, color=color)

        self.axes.plot(mids, ws, "r")
        self.axes.scatter(mids, ws, color="r")
        self.axes.plot(func[0], func[1], color="black")

        xticks = list(map(lambda x: round(x, 3), self.axes.get_xticks()))
        xtickslabels = list(map(str, xticks))

        if self._gap_x:
            xticks.insert(0, self._gap_x)
            xtickslabels.insert(0, "≈")
            if '0.0' not in xtickslabels and '0' not in xtickslabels:
                xticks.insert(0, self._gap_x - (self._gap_x / 5))
                xtickslabels.insert(0, "0")
            
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xtickslabels)

        self.draw()



class Polygon(BasicGraph):
    def __init__(self, parent=None, name=None, w=5, h=4, dpi=100):
        BasicGraph.__init__(self, parent, name, w, h, dpi)
        self._gap_x = None

    def set_x_gap(self, x):
        self._gap_x = x

    def display(self, x, y, xl='x', yl='y', color='b', name=None):
        self.redo(self.axes, 0, name, xl, yl)

        self.axes.plot(x, y, color)

        xticks = list(map(lambda x: round(x, 3), self.axes.get_xticks()))
        xtickslabels = list(map(str, xticks))

        if self._gap_x:
            xticks = list(filter(lambda xi: xi >= x[0], xticks))
            xtickslabels = list(map(str, xticks))
            
            xticks.insert(0, self._gap_x)
            xtickslabels.insert(0, "≈")
            
            xticks.insert(0, self._gap_x * 0.9)
            xtickslabels.insert(0, "0")
            
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xtickslabels)

        self.draw()


class Density(BasicGraph):
    def __init__(self, parent=None, names=None, w=5, h=4, dpi=100):
        name = names[0] if names else None
        BasicGraph.__init__(parent, name, w, h, dpi, 211)

        self.name.append(name[1] if names else None)
        self.axes2.set_title(self.name[1])

        self.axes2 = self.figure.add_subplot(212)
        self.axes2.grid(True)

    def display_poly(self, x, y, xl='x', yl='y', color='b', name=None):
        self.redo(self.axes, 0, name, xl, yl)

        self.axes.plot(x, y, color)

        self.draw()

    def display_density(self, left, right, den_func, xl='x', yl='y', name=None, color='r', perc=.1):
        self.redo(self.axes2, 1, name, xl, yl)

        nums = arange(int(left), int(right), perc)
        dens = [den_func(i) for i in nums]

        self.axes2.plot(nums, dens, color)
        self.draw()
