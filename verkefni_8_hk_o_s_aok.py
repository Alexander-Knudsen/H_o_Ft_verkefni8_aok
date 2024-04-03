import wx
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import fftpack as sc


#Skilgreina gluggaramman
class Gluggarammi(wx.Frame):
    def __init__(self, parent, title):
        super(Gluggarammi, self).__init__(parent, title=title, size=(600, 400))
        self.panel = Maeliforrit(self)

#Skilgreina mæliforritið
class Maeliforrit(wx.Panel):
    def __init__(self, parent):
        super(Maeliforrit, self).__init__(parent)
        self.Bind(wx.EVT_BUTTON, self.Button)
       
#       Titill
        self.label = wx.StaticText(self, label="Sveiflugreiningarkerfi", pos=(140, 30))
        font = wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.label.SetFont(font)

#       Aðgerðarhnappar
        self.btn = wx.Button(self, label='Innlestur', pos=(200, 70))
        self.btn = wx.Button(self, label='Mæling', pos=(200, 175))
        self.btn = wx.Button(self, label='Vista', pos=(200, 240))
        self.btn = wx.Button(self, label='Tímaháð merki', pos=(200, 280))
        self.btn = wx.Button(self, label='FFT greining', pos=(200, 310))

#       Skýringartextar
        self.label = wx.StaticText(self, label="Söfnunartíðni", pos=(60, 120))
        self.label = wx.StaticText(self, label="Fjöldi mæligilda", pos=(60, 150))
        self.label = wx.StaticText(self, label="Skrá", pos=(60, 215))

#       Innlestrarreitir
        self.text_ctrl1 = wx.TextCtrl(self, pos=(200, 120), size=(150, 20))
        self.text_ctrl2 = wx.TextCtrl(self, pos=(200, 150), size=(150, 20))
        self.text_ctrl3 = wx.TextCtrl(self, pos=(200, 215), size=(150, 20))

#       Tengja aðgerðarhnappa við aðgerðir def
        self.Bind(wx.EVT_BUTTON, self.Button)
        self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButtons)

#       Hnappar til að velja Hanning eða flattop
        self.rb1 = wx.RadioButton(self, label="Flat Top", pos=(100, 300), style=wx.RB_GROUP)
        self.rb2 = wx.RadioButton(self, label="Hanning", pos=(100, 320))



# Aðgerð sem les valhnappana
    def onRadioButtons(self, e):
        global radiobutt
        rb = e.GetEventObject()
        self.label.SetLabelText("You Have Selected " + rb.GetLabel())
        print("Radiobutton: ", rb.GetLabel())
        if rb.GetLabel() == "Flat Top": radiobutt = 1
        if rb.GetLabel() == "Hanning": radiobutt = 2

# Aðgerðir til að vinna úr valmyndinni
    def Button(self, e):
        global yA
        bu = e.GetEventObject()
        self.label.SetLabelText("You Have Selected " + bu.GetLabel())
        print("Button: ", bu.GetLabel())
# Opna mæliskrá
        if bu.GetLabel() == "Innlestur":
            frame = wx.Frame(None, -1, 'win.py')
            frame.SetSize(0, 0, 200, 50)
    
            # Opna samskiptaglugga fyrir innlestrarskrá
            openFileDialog = wx.FileDialog(frame, "Opna mæliskrá", "", "",
                                   "CSV skrá (*.csv)|*.csv",
                                   wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            openFileDialog.ShowModal()
            print(openFileDialog.GetPath())
            # defDir, defFile = '', ''
            yA = np.genfromtxt(openFileDialog.GetPath(), delimiter=';')
            fs = yA[0][0]
            Nm = yA[0][2]
            yA = np.delete(yA, 0, 0)
            print(fs, Nm, type(fs))
            self.text_ctrl1.SetValue(str(int(fs)))
            self.text_ctrl2.SetValue(str(int(Nm)))
            openFileDialog.Destroy()


# Mæliaðgerð (mælingin er tilbúin enn nemi)
        if bu.GetLabel() == "Mæling":
            # Sækja söfnunartíðni og fjölda mæligilda
            fs = int(self.text_ctrl1.GetValue())
            Nm = int(self.text_ctrl2.GetValue())
            yIn = np.array([[fs, Nm]]) .T
            np.savetxt("ADread.inp", yIn)
            os.system('cmd /c "ADread"')
            yA = np.loadtxt("ADread.out")
            print(self.text_ctrl1.GetValue())
            print(self.text_ctrl2.GetValue())
            T = 1 / fs
            ts = np.linspace(0.0, Nm*T, Nm, endpoint=False)
            print(yA.shape)
            for isen in range(4):
                ypl = yA.T[isen][:]
                plt.plot(ts, ypl)
                plt.grid()
                plt.xlabel("Tími [s]")
                plt.ylabel("Hröðun [m/s^2]")
                plt.show()








# FFT greining með Flat Top eða Hanning glugga
        if bu.GetLabel() == "FFT greining":
            fs = int(self.text_ctrl1.GetValue())
            Nm = int(self.text_ctrl2.GetValue())
            T = 1 / fs
            wt = 2 * np.pi * np.linspace(0.0, 1.0, Nm)
        if radiobutt == 1:
            win = 1 - 1.93*np.cos(wt) + 1.29*np.cos(2*wt) - 0.388*np.cos(3*wt) + 0.0322*np.cos(4*wt)
        if radiobutt == 2:
            win = 1 - np.cos(wt)
        for isen in range(4):
            yfi = yA.T[isen][:]
            yf = sc.fft(yfi*win)
            yFA = 2.0/Nm * np.abs(yf[0:Nm//2])
            xf = sc.fftfreq(Nm, T)[:Nm//2]
            plt.plot(xf[0:200], yFA[0:200])
            plt.grid()
            plt.xlabel("Tíðni [Hz]")
            plt.ylabel("Hröðun [m/s^2]")
            plt.show()

# Teikna tímaðhað merkið
            if bu.GetLabel() == "Tímaháð merki":
                fs = int(self.text_ctrl1.GetValue())
                Nm = int(self.text_ctrl2.GetValue())
                T = 1 / fs
                ts = np.linspace(0.0, Nm*T, Nm, endpoint=False)
                plt.plot(ts, yA)
                plt.grid()
                plt.xlabel("Tími [s]")
                plt.ylabel("Hröðun [m/s^2]")
                plt.show()


# Vista mælinguna (athugið að það á einnig að vista fs og N)
            if bu.GetLabel() == "Vista":
                fs = int(self.text_ctrl1.GetValue())
                Nm = int(self.text_ctrl2.GetValue())
                filename = self.text_ctrl3.GetValue()
                print(filename)
                ySave = np.reshape(yA, (Nm, -1))
                yIn = np.array([[fs, fs, Nm, Nm]])
                ySa = np.row_stack((yIn, yA))
                print(ySa.shape)
                np.savetxt(filename, ySa, delimiter=";")

# Aðaðalforritið
class MyApp(wx.App):
    def OnInit(self):
        self.frame = Gluggarammi(parent=None, title="Sveiflumælingar")
        self.frame.Show()
        return True

radiobutt = 1
app = MyApp()
app.MainLoop()





