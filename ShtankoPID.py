from tkinter import *
from random import *

class pidController:
	def __init__(self,K_p,K_i,K_d,setPoint,dt,measuredVar,integrator=0.0,derivator=0.0,error=0.0):
		self.K_p = K_p
		self.K_i = K_i
		self.K_d = K_d

		self.setPoint = setPoint
		self.measuredVar = measuredVar
		self.dt = dt

		self.derivator = derivator
		self.integrator = integrator
		self.error = error
		
		self.controlling = False
		self.iterations = 0

	def cycle(self):
		if (self.controlling == True):

			self.error = self.setPoint - self.measuredVar
			P = self.K_p * self.error
		
			self.integrator= self.integrator + self.error * self.dt
			I = self.integrator * self.K_i
		
			D = self.K_d * (self.error - self.derivator) / self.dt
			self.derivator = self.error
		
			self.PID = P + I + D
			self.measuredVar = ioGen.model(self.PID) # grabs measuredVar from random number generator. Replace this with DAQ readings for a real PID.
			
			self.iterations += 1
			pidControl.after(self.dt*1000,self.cycle) # after command in tkinter calls this method after a certain amount of time. This was originally a while loop, but there is no easy way to multithread tkinter so it had to go.
			
#PRINT OUTPUT TO CONSOLE:
			print('ITERATION: ', self.iterations)
			print('SET POINT: ', self.setPoint)
			print('PID: ', self.PID)
			print('MEASURED VARIABLE: ', self.measuredVar)
			print('-----')

	def setVariables(self,K_p,K_i,K_d,setPoint,dt):
		self.K_p = K_p
		self.K_i = K_i
		self.K_d = K_d

		self.setPoint = setPoint
		self.dt = dt

		self.derivator = 0.0
		self.integrator = 0.0
		self.error = 0.0
	
		self.controlling = True
		self.cycle()

	def resetIterations(self):
		self.iterations = 0

	def getError(self):
		return self.error
	def getSetPoint(self):
		return self.setPoint
	def getPID(self):
		return self.PID
	
	def stopCycle(self):
		self.controlling = False
		print("STOPPED CONTROLLING")

# this class will generate random noise and hold the process model. For a real application replace with some arduino library calls.
class IOgenerator:
	def __init__(self,measuredVar,manipulatedVar):
		self.measuredVar = measuredVar
		self.manipulatedVar = manipulatedVar
		
	def model(self,manipulatedVar):
		# tank level simulation with the valve located on the bottom and one in stream above. Let's pretend the efflux rate is independent of the level of an arbitrarily large tank
		# we need a non-inverse controller for this purpose
		# disturbance: inlet pipe from process w/ lots of noise
		# measured var: tank level
		# manipulated var: efflux rate from tank
		# final control element: valve on drain pipe. This is what the PID controls.
		
		self.manipulatedVar = -1*manipulatedVar
		# disturbance simulation below with the disturbance variable being equal to .5+rand(0,1)*.2:
		self.measuredVar += .5 + random()*.1 # constantly increase the tank level by a noisy amount
		# valve simulation below: the pipe is only so big and the efflux rate can only range from 0 to 2.
		if self.manipulatedVar > 2:
			self.measuredVar = self.measuredVar - 2
		elif self.manipulatedVar < 0:
			self.measuredVar = self.measuredVar # this exists for ease of reading
		else:
			self.measuredVar = self.measuredVar + self.manipulatedVar # relationship between measured and manipulated var
		print("VALVE POSITION: ", self.measuredVar)
		return self.measuredVar


# Let's instantiate the PIDController (as pCtrl) and the IOGenerator (as ioGen) above with some default vars
pCtrl = pidController(1,1,1,0,.1,0)
ioGen = IOgenerator(0,0)
		
# TK Interface code, didn't put it in a class because it's a bit finnicky and I'm just learning to use the library
pidControl = Tk()
pidControl.title('Shtanko PID Controller')

# create entry field labels in tkinter
Label(pidControl, text="Set Gains Here", fg="red", padx = 10, pady=10, font=("Cambria",14)).grid(row=0, column=0, sticky=E)
Label(pidControl, text="K_p").grid(row=1, sticky=E)
Label(pidControl, text="K_i").grid(row=2, sticky=E)
Label(pidControl, text="K_d").grid(row=3, sticky=E)
Label(pidControl, text="Set Time Interval & Set Point Here", fg="red", padx = 10, pady=10, font=("Cambria",14)).grid(row=4, column=0, sticky=E)
Label(pidControl, text="Set Point").grid(row=5, sticky=E)
Label(pidControl, text="Interval Between Updates in Seconds (Integer)").grid(row=6, sticky=E)

# create & place entry field widgets on grid in tkinter
K_pEntry = Entry(pidControl)
K_iEntry = Entry(pidControl)
K_dEntry = Entry(pidControl)
setPointEntry = Entry(pidControl)
dtEntry = Entry(pidControl)

K_pEntry.grid(row=1, column=1)
K_iEntry.grid(row=2, column=1)
K_dEntry.grid(row=3, column=1)
setPointEntry.grid(row=5, column=1)
dtEntry.grid(row=6, column=1)

# this is the take everything and run function which gets called when the Update buttom is pressed below
def getEverything():
	K_pInput = float(K_pEntry.get())
	K_iInput = float(K_iEntry.get())
	K_dInput = float(K_dEntry.get())
	setPointInput = float(setPointEntry.get())
	dtInput = int(dtEntry.get())
	
	pCtrl.resetIterations()
	pCtrl.setVariables(K_pInput,K_iInput,K_dInput,setPointInput,dtInput)

# Passing pCtrl.setVariables(vars) to button below executes it at start. Lambda prevents that.
updateValues = Button(pidControl, text="Update", pady=10, command=getEverything)
updateValues.grid(row=7,column=0)
stopProcess = Button(pidControl, text="Stop", pady=10, command=lambda: pCtrl.stopCycle()) # the stop button!
stopProcess.grid(row=7,column=1)

pidControl.mainloop() # tkinter method that builds the entire interface
