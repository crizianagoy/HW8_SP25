#region imports
import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from Rankine_GUI import Ui_Form
from Rankine_Classes_MVC import rankineController
from UnitConversions import UnitConverter as UC
# These imports are necessary for drawing a matplotlib graph in the GUI
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
#endregion

#region class definitions
class MainWindow(qtw.QWidget, Ui_Form):
    """
    Main window class for the Rankine Cycle GUI application.
    Inherits from QWidget and the auto-generated Ui_Form class.
    Initializes and connects the controller, handles all UI setup.
    """
    def __init__(self):
        """
        Constructor for MainWindow. Initializes the UI, connects signals,
        creates the plotting area, and sets up the MVC controller.
        """
        super().__init__()  # Run the parent class constructor first
        self.setupUi(self)  # Initialize widgets from Qt Designer file
        self.AssignSlots()  # Connect signal-slot events
        self.MakeCanvas()   # Create the plotting canvas

        # Create lists of input and display widgets to pass to the controller
        self.input_widgets = [self.rb_SI, self.le_PHigh, self.le_PLow, self.le_TurbineInletCondition,
                              self.rdo_Quality, self.le_TurbineEff, self.cmb_XAxis, self.cmb_YAxis,
                              self.chk_logX, self.chk_logY]

        self.display_widgets = [self.lbl_PHigh, self.lbl_PLow, self.lbl_SatPropLow, self.lbl_SatPropHigh,
                                self.lbl_TurbineInletCondition, self.lbl_H1, self.lbl_H1Units, self.lbl_H2,
                                self.lbl_H2Units, self.lbl_H3, self.lbl_H3Units, self.lbl_H4, self.lbl_H4Units,
                                self.lbl_TurbineWork, self.lbl_TurbineWorkUnits, self.lbl_PumpWork,
                                self.lbl_PumpWorkUnits, self.lbl_HeatAdded, self.lbl_HeatAddedUnits,
                                self.lbl_ThermalEfficiency, self.canvas, self.figure, self.ax]

        # Instantiate controller with input/output widgets
        self.RC = rankineController(self.input_widgets, self.display_widgets)

        # Initial update of saturation properties and calculation
        self.setNewPHigh()
        self.setNewPLow()
        self.Calculate()

        # Store mouse coordinates for plot hover tracking
        self.oldXData = 0.0
        self.oldYData = 0.0

        self.show()  # Show main window

    def AssignSlots(self):
        """
        Connects all GUI components (buttons, radio buttons, etc.)
        to their corresponding slot methods.
        """
        self.btn_Calculate.clicked.connect(self.Calculate)
        self.rdo_Quality.clicked.connect(self.SelectQualityOrTHigh)
        self.rdo_THigh.clicked.connect(self.SelectQualityOrTHigh)
        self.le_PHigh.editingFinished.connect(self.setNewPHigh)
        self.le_PLow.editingFinished.connect(self.setNewPLow)
        self.rb_SI.clicked.connect(self.SetUnits)
        self.rb_English.clicked.connect(self.SetUnits)
        self.cmb_XAxis.currentIndexChanged.connect(self.SetPlotVariables)
        self.cmb_YAxis.currentIndexChanged.connect(self.SetPlotVariables)
        self.chk_logX.toggled.connect(self.SetPlotVariables)
        self.chk_logY.toggled.connect(self.SetPlotVariables)

    def MakeCanvas(self):
        """
        Creates the matplotlib canvas where the Rankine cycle plot is drawn.
        Adds it to the Qt layout.
        """
        self.figure = Figure(figsize=(1, 1), tight_layout=True, frameon=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot()
        self.Layout_Plot.addWidget(NavigationToolbar2QT(self.canvas, self))
        self.Layout_Plot.addWidget(self.canvas)
        self.canvas.mpl_connect("motion_notify_event", self.mouseMoveEvent_Canvas)

    def mouseMoveEvent_Canvas(self, event):
        """
        Event handler that updates the window title based on the mouse position over the plot.
        :param event: mouse move event on the matplotlib canvas
        """
        self.oldXData = event.xdata if event.xdata is not None else self.oldXData
        self.oldYData = event.ydata if event.ydata is not None else self.oldYData
        sUnit = 'kJ/(kg*K)' if self.rb_SI.isChecked() else 'BTU/(lb*R)'
        TUnit = 'C' if self.rb_SI.isChecked() else 'F'
        self.setWindowTitle('s: {:.2f} {}, T: {:.2f} {}'.format(self.oldXData, sUnit, self.oldYData, TUnit))

    def Calculate(self):
        """
        Triggers the controller to read user inputs, update the model,
        and refresh the GUI.
        """
        self.RC.updateModel()

    def SelectQualityOrTHigh(self):
        """
        Toggles between specifying turbine inlet using quality or temperature.
        Updates GUI and controller accordingly.
        """
        self.RC.selectQualityOrTHigh()

    def SetPlotVariables(self):
        """
        Called when the plot axis variables or log scale checkboxes change.
        Updates the Rankine cycle plot.
        """
        self.RC.updatePlot()

    def SetUnits(self):
        """
        Called when the user changes between SI and English units.
        Triggers a full GUI refresh in the new unit system.
        """
        self.RC.updateUnits()

    def setNewPHigh(self):
        """
        Called when the user finishes editing P High input.
        Updates saturation properties at high pressure.
        """
        self.RC.setNewPHigh()

    def setNewPLow(self):
        """
        Called when the user finishes editing P Low input.
        Updates saturation properties at low pressure.
        """
        self.RC.setNewPLow()
#endregion

#region main execution
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    mw.setWindowTitle('Rankine calculator')
    sys.exit(app.exec())
#endregion