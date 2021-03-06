#!/usr/bin/python
'''
Study Common Emitter Characteristics of NPN transistors.
Saturation currents, and their dependence on base current 
can be easily visualized.

'''

from __future__ import print_function
import time,sys,os

from PSL_Apps.utilitiesClass import utilitiesClass
from .templates import ui_NFET as NFET
from PyQt4 import QtCore, QtGui
import pyqtgraph as pg

import numpy as np

params = {
'image' : 'transistorCE.png',
'name':'N-FET Transfer\nCharacteristics',
'hint':''
}

class AppWindow(QtGui.QMainWindow, NFET.Ui_MainWindow,utilitiesClass):
	def __init__(self, parent=None,**kwargs):
		super(AppWindow, self).__init__(parent)
		self.setupUi(self)
		self.I=kwargs.get('I',None)
		self.I.set_gain('CH1',2)

		self.setWindowTitle(self.I.H.version_string+' : '+params.get('name','').replace('\n',' ') )

		self.plot=self.add2DPlot(self.plot_area,enableMenu=False)
		self.sig = self.rightClickToZoomOut(self.plot)
		labelStyle = {'color': 'rgb(255,255,255)', 'font-size': '11pt'}
		self.plot.setLabel('left','Drain Current', units='A',**labelStyle)
		self.plot.setLabel('bottom','Gate-Source Voltage', units='V',**labelStyle)

		self.startV.setMinimum(-3.3); self.startV.setMaximum(0); self.startV.setValue(-3.3)
		self.stopV.setMinimum(-3.3); self.stopV.setMaximum(0)
		self.biasV.setMinimum(-5); self.biasV.setMaximum(5); self.biasV.setValue(5)

		self.sweepLabel.setText('Gate Voltage Range(PV2)')
		self.biasLabel.setText('Drain Voltage(PV1)')

		self.totalpoints=2000
		self.X=[]
		self.Y=[]
		self.RESISTANCE = 560
		self.traceName =''
		self.curves=[]
		self.curveLabels=[]
		self.looptimer = self.newTimer()
		self.looptimer.timeout.connect(self.acquire)
		self.running = True


	def savePlots(self):
		self.saveDataWindow(self.curves,self.plot)


	def run(self):
		self.looptimer.stop()
		self.X=[];self.Y=[]
		self.VCC = self.I.set_pv1(self.biasV.value()) 
		self.traceName = 'Vcc = %s'%(self.applySIPrefix(self.VCC,'V'))
		self.curves.append( self.addCurve(self.plot ,self.traceName) )


		self.START = self.startV.value()
		self.STOP = self.stopV.value()
		self.STEP = (self.STOP-self.START)/self.totalPoints.value()
		
		self.V = self.START
		self.I.set_pv2(self.V) 
		time.sleep(0.2)

		P=self.plot.getPlotItem()
		self.plot.setXRange(self.V,self.stopV.value()*1.2)
		self.plot.setYRange(0,20e-3)
		if len(self.curves)>1:P.enableAutoRange(True,True)

		if self.running:self.looptimer.start(20)

	def acquire(self):
		VG=self.I.set_pv2(self.V)
		self.X.append(VG)

		VC =  self.I.get_voltage('CH1',samples=10)
		self.Y.append((self.VCC-VC)/self.RESISTANCE) # list( ( np.linspace(V,V+self.stepV.value(),1000)-VC)/1.e3)

		self.curves[-1].setData(self.X,self.Y)

		self.V+=self.STEP
		if self.V>self.stopV.value():
			self.looptimer.stop()
			txt='<div style="text-align: center"><span style="color: #FFF;font-size:8pt;">%s</span></div>'%(self.traceName)
			text = pg.TextItem(html=txt, anchor=(0,0), border='w', fill=(0, 0, 255, 100))
			self.plot.addItem(text)
			text.setPos(self.X[-1],self.Y[-1])
			self.curveLabels.append(text)
			self.tracesBox.addItem(self.traceName)

	def delete_curve(self):
		c = self.tracesBox.currentIndex()
		if c>-1:
			self.tracesBox.removeItem(c)
			self.removeCurve(self.plot,self.curves[c]);
			self.plot.removeItem(self.curveLabels[c]);
			self.curves.pop(c);self.curveLabels.pop(c);
			if len(self.curves)==0: # reset counter for plot numbers
				self.plotnum=0


	def __del__(self):
		self.looptimer.stop()
		print ('bye')

	def closeEvent(self, event):
		self.looptimer.stop()
		self.finished=True


if __name__ == "__main__":
    from PSL import sciencelab
    app = QtGui.QApplication(sys.argv)
    myapp = AppWindow(I=sciencelab.connect())
    myapp.show()
    sys.exit(app.exec_())

