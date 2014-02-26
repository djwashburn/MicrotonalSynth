import wx, pyo, time

# Set up pyo
s = pyo.Server().boot()
s.start()

class LiveAdsr(pyo.SigTo):
	"""An adsr class for live use. HitNote() plays attack through sustain portions, RelNote() plays the release portion."""
	def __init__(self, att=0, dec=0, sus=0, rel=0, mul=1):
		pyo.SigTo.__init__(self, 0)
		self.att=att
		self.dec=dec
		self.sus=sus*mul
		self.rel=rel
		self.mul=mul
	
	def StartNote(self):
		self.setTime(self.att)
		self.setValue(self.mul)
		self.setTime(self.dec)
		self.setValue(self.sus)
	
	def RelNote(self):
		self.setTime(self.rel)
		self.setValue(0)

# Classes ending in Inst define instruments
class Instrument():  # Instrument class skeleton. Instrument classes should inherit from here.
	def __init__(self, freq):
		pass
	
	def HitNote(self):
		pass
	
	def RelNote(self):
		pass

class SineInst(Instrument):
	"""Most basic instrument class. Plays a sine wave at specified frequency with attack and release ramps."""
	def __init__(self, freq):
		self.volmod = LiveAdsr(att=.1, dec=.2, sus=.6, rel=.5, mul=.25)
		self.sine = pyo.Sine(freq=freq, mul=self.volmod).out()
	
	def HitNote(self):
		self.volmod.StartNote()
	
	def RelNote(self):
		self.volmod.RelNote()
		
class HarmInst(SineInst):
	"""Harmonic instrument"""
	def __init__(self, freq):
		SineInst.__init__(self, freq)
		self.sine = pyo.Sine(freq=[freq*(x+1) for x in range(10)], mul=self.volmod).out()
		
class TritInst(SineInst):
	"""Inharmonic instrument based around the tritone."""
	def __init__(self, freq):
		SineInst.__init__(self, freq)
		self.sine = pyo.Sine(freq=[freq, freq*(2**(1/2))], mul=self.volmod).out()

class NotePlayer():
	"""This class will handle mapping keys to notes and playing them when requested"""
	def __init__(self):
		self.bfreq = 110.0
		self.scaletype = "eqdiv"  # "eqdiv" = Equal division of an interval, "eqcents" = equal cents scale
		self.steps = 12.0
		self.unison = 2.0
		self.cents = 88.0
		self.inst = TritInst
		# Maps the keycodes of the keyboard to a list of numbers, each representing a key.
		self.keymap = {96:0, 49:1, 50:2, 51:3, 52:4, 53:5, 54:6, 55:7, 56:8, 57:9, 48:10, 45:11, 61:12, 81:13, 87:14, 69:15, 82:16, 84:17, 89:18, 85:19, 73:20, 79:21, 80:22, 91:23, 93:24, 92:25, 311:26, 65:27, 83:28, 68:29, 70:30, 71:31, 72:32, 74:33, 75:34, 76:35, 59:36, 39:37, 13:38, 90:39, 88:40, 67:41, 86:42, 66:43, 78:44, 77:45, 44:46, 46:47, 47:48}
		self.keydown = [0 for i in range(55)]  # Keeps track of which keys are being held down and which are up
		for each in range(0, 54):
			self.keydown[each] = False  # All start down, obviously
		self.scale = [0 for i in range(55)]  # Define the scale the keys are mapped to
		for num in range(0, 55):
			self.scale[num] = self.bfreq*(2**(num/12.0))  # Automatically start with 12edo. We'll add on option to choose a scale later
		self.keyinstrs = [0 for i in range(55)]
	
	def keyexists(self, keycode):
		return keycode in self.keymap
	
	def is_keydown(self, keycode):
		key = self.keymap[keycode]
		return self.keydown[key] == True
		
	def HitNote(self, notenum, inst=SineInst):  # inst argument is an instrument class
		#self.f = pyo.Adsr(attack=.01, decay=.2, sustain=.75, mul=2)
		#self.g = pyo.Adsr(sustain=.75, release=.5, dur=.5, mul=2)
		#self.a = pyo.Sine(freq = self.scale[notenum], mul=self.f).out()
		#self.f.play()
		freq = self.scale[notenum]
		print inst
		if self.keyinstrs[notenum] == 0:
			self.keyinstrs[notenum] = inst(freq)
		print self.keyinstrs[notenum]
		self.keyinstrs[notenum].HitNote()
		
	def RelNote(self, notenum, inst):
		#self.a.mul = self.g
		#self.g.play()
		print self.keyinstrs[notenum]
		self.keyinstrs[notenum].RelNote()
		
	def SetEqDivScale(self, steps, unison):
		for num in range(0, 55):
			self.scale[num] = self.bfreq*(unison**(num/steps))
	
	def SetEqCentsScale(self, cents):
		for num in range(0, 55):
			self.scale[num] = self.bfreq*(2**(num*cents/1200.0))
	
	def ResetScale(self):
		print self.bfreq
		if self.scaletype == "eqdiv":
			print "here"
			self.SetEqDivScale(self.steps, self.unison)
		elif self.scaletype == "eqcents":
			self.SetEqCentsScale(self.cents)
		else:
			print "Defaulting to 12edo."
			self.SetEqDivScale(12.0, 2.0)
		for i in range(0,55):
			freq = self.scale[i]
			if self.keyinstrs[i] != 0:
				self.keyinstrs[i] = self.inst(freq)

keyboard = NotePlayer()

class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(-1,-1))
		self.CreateStatusBar() # A Statusbar in the bottom of the window
		
		# Setting up the menu.
		filemenu = wx.Menu()
		
		#wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets
		menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
		menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")
		
		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
		self.SetMenuBar(menuBar) # Adding the MenuBar to the Frame content.
		
		# Set events
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		
		# Accelerator table, to bind keys to actions globally. Not useful for
		# typable characters as far as I can tell, because it swallows their events
		
		randomId = wx.NewId()
		self.Bind(wx.EVT_MENU, self.onKey, id=randomId)
		accTable = wx.AcceleratorTable([(wx.ACCEL_NORMAL, 340, randomId)]) # 340 is the keycode for F1
		self.SetAcceleratorTable(accTable)
		
		self.Show(True)
	
	def onKey(self, arg):
		print "You F1F1!"
		arg.Skip()
	
	def OnAbout(self, e):
		# A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
		dlg = wx.MessageDialog(self, "A basic synth GUI", "About Basic Synth", wx.OK)
		dlg.ShowModal() # Show it
		dlg.Destroy() # finally destroy it when finished.
	
	def OnExit(self, e):
		self.Close(True) # Close the frame.

class keysink(wx.Window):
	"""This class creates a colored window that catches KeyEvents.
	
	The window area should start out blue. When it has the focus, it will turn green
	and say it is ready. When it loses focus, it will turn red and say it is not ready.
	It has several event handlers to define this behaviour, and as many as necessary to
	process the KeyEvents as desired."""
	def __init__(self, parent):
		wx.Window.__init__(self, parent, style=wx.WANTS_CHARS, name="sink", size=(200,100))
		
		self.SetBackgroundColour(wx.BLUE)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
		self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
		self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
		self.haveFocus = False
		
		# Info for playing notes, will be set by controls in parent panel
		self.freq = 440
		self.wave = 'Sine'
	
	def OnPaint(self, evt):
		"""This runs when the window is painted to the screen, such as when it is loaded and refreshed"""
		dc = wx.PaintDC(self)
		rect = self.GetClientRect()
		if self.haveFocus:
			self.SetBackgroundColour(wx.RED)
			dc.SetTextForeground(wx.BLACK)
			dc.DrawLabel("Ready", rect, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)
		else:
			self.SetBackgroundColour(wx.GREEN)
			dc.SetTextForeground(wx.BLACK)
			dc.DrawLabel("Not ready!", rect, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)
	
	def OnMouse(self, event):
		self.SetFocus()
	
	def OnSetFocus(self, event):
		self.haveFocus = True
		self.Refresh()
	
	def OnKillFocus(self, event):
		self.haveFocus = False
		self.Refresh()
	
	def OnKeyDown(self, event): 	# Detects the 1 key. Just for testing so far.
		keycode = event.KeyCode
		if keyboard.keyexists(keycode) == False:
			event.Skip()
			return
		key = keyboard.keymap[keycode]
		if keyboard.is_keydown(keycode) == True:
			pass
		elif keyboard.is_keydown(keycode) == False:
			keyboard.keydown[key] = True
			print "You pressed key ", key, "!"
			keyboard.HitNote(key, keyboard.inst)
		event.Skip()

	def OnKeyUp(self, event):
		keycode = event.KeyCode
		if keyboard.keyexists(keycode) == False:
			event.Skip()
			return
		key = keyboard.keymap[keycode]
		keyboard.keydown[key] = False
		print "You released key ", key, "!"
		keyboard.RelNote(key, keyboard.inst)
		event.Skip()
	
class ctrlpanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.values = dict([('bfreq', 110.0),('steps', 12.0),('unison', 2.0)])
		
		grid = wx.GridBagSizer(hgap=7, vgap=7)	# Sizer to organize the controls in a grid
		
		# Controls
		
		self.lblfreq = wx.StaticText(self, label="Base Frequency (hz): ")
		grid.Add(self.lblfreq, pos=(0,0))
		self.freq = wx.TextCtrl(self, value="110", size=(100, 20))
		grid.Add(self.freq, pos=(0,1))
		self.lblsteps = wx.StaticText(self, label="Number of Steps per Unison: ")
		grid.Add(self.lblsteps, pos=(1,0))
		self.steps = wx.TextCtrl(self, value="12", size=(100, 20))
		grid.Add(self.steps, pos=(1,1))
		self.lblunison = wx.StaticText(self, label="Ratio of Unison: ")
		grid.Add(self.lblunison, pos=(1,2))
		self.unison = wx.TextCtrl(self, value="2", size=(50, 20))
		grid.Add(self.unison, pos=(1,3))
		self.apply = wx.Button(self, id=wx.ID_APPLY)
		grid.Add(self.apply, pos=(2,0))
		
		self.waveList = ['Sine', 'Semicircle', 'Saw', 'Square']
		self.lblwave = wx.StaticText(self, label="Wave Shape: ")
		grid.Add(self.lblwave, pos=(3,0))
		self.wave = wx.Choice(self, choices=self.waveList)
		self.wave.SetStringSelection('Sine')
		grid.Add(self.wave, pos=(3,1))
		
		# Bind methods
		
		self.Bind(wx.EVT_TEXT, self.onSteps, self.steps)
		self.Bind(wx.EVT_TEXT, self.onUnison, self.unison)
		self.Bind(wx.EVT_TEXT, self.onFreq, self.freq)
		self.Bind(wx.EVT_KILL_FOCUS, self.ApplyChanges, self.freq)
		self.Bind(wx.EVT_BUTTON, self.ApplyChanges, self.apply)
		
		# The keysink
		
		self.lblsink = wx.StaticText(self, label="Click here to play notes with your keyboard: ")
		grid.Add(self.lblsink, pos=(4,0))
		self.sink = keysink(self)
		grid.Add(self.sink, pos=(5,0))
		
		# Put everything into place
		self.SetSizerAndFit(grid)
	
	def onFreq(self,event):
		raw_input = event.GetString()
		try :
			freq = float(raw_input)
			self.values['bfreq'] = freq
		except ValueError:
			self.freq.SetValue("0")
	
	def onSteps(self, event):
		raw_input = event.GetString()
		try :
			steps = float(raw_input)
			self.values['steps'] = steps
		except ValueError:
			self.steps.SetValue("0")
	
	def onUnison(self, event):
		raw_input = event.GetString()
		try :
			unison = float(raw_input)
			self.values['unison'] = unison
		except ValueError:
			self.steps.SetValue("0")
	
	def ApplyChanges(self, event):
		keyboard.bfreq = self.values['bfreq']
		keyboard.steps = self.values['steps']
		keyboard.unison = self.values['unison']
		keyboard.ResetScale()
		

app = wx.App(False)
frame = MainWindow(None, 'Sample editor')
panel = ctrlpanel(frame)
frame.Show()
app.MainLoop()