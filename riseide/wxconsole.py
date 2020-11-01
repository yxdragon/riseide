import wx.stc as stc
import wx
import keyword
from .pconsole import ProcessConsole
import threading, time

faces = {'times': 'Times New Roman',
             'mono': 'Courier New',
             'helv': 'Consolas',
             'other': 'Consolas',
             'size': 10,
             'size2': 8,
             }


class WxConsole(stc.StyledTextCtrl):
    
    def __init__(self, parent, ID=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0):
        stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

        self.CmdKeyAssign(ord('B'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.SetLexer(stc.STC_LEX_PYTHON)
        self.SetKeyWords(0, " ".join(keyword.kwlist))

        self.SetProperty("fold", "1")
        self.SetProperty("tab.timmy.whinge.level", "1")
        # self.SetMargins(0, 0)
        # run_script('C:/Users/54631/Desktop/test/abc/test.py')
        # no tabs
        self.SetUseTabs(False)
        self.SetTabWidth(4)

        # self.SetViewWhiteSpace(True)
        # self.SetWhitespaceSize(4)
        # self.SetBufferedDraw(False)
        # self.SetViewEOL(True)
        # self.SetEOLMode(stc.STC_EOL_CRLF)
        # self.SetUseAntiAliasing(True)

        self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        self.SetEdgeColumn(100)

        # set line number
        # self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        # self.SetMarginWidth(1, 35)

        # self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)

        # bind keyboard
        # self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)
        # self.Bind(wx.stc.EVT_STC_CHARADDED, self.on_text_changed)
        # self.Bind(stc.EVT_STC_AUTOCOMP_COMPLETED, self.on_autocomp_finish)

        # Make some styles,  The lexer defines what each style is used for, we
        # just have to define what each style looks like.  This set is adapted from
        # Scintilla sample property files.

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                          "face:%(helv)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                          "face:%(helv)s,size:%(size)d" % faces)

        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,
                          "fore:#FFFFFF,back:#0000FF")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,
                          "fore:#000000,back:#FF0000")

        # line number margin color
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,
                          'fore:#00FF00,back:#222222,size:13')

        # Python styles
        # Default
        self.StyleSetSpec(stc.STC_P_DEFAULT,
                          "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # Comments
        self.StyleSetSpec(stc.STC_P_COMMENTLINE,
                          "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
        # Number
        self.StyleSetSpec(stc.STC_P_NUMBER,
                          "fore:#007F7F,size:%(size)d" % faces)
        # String
        self.StyleSetSpec(stc.STC_P_STRING,
                          "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # Single quoted string
        self.StyleSetSpec(stc.STC_P_CHARACTER,
                          "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # Keyword
        self.StyleSetSpec(
            stc.STC_P_WORD, "fore:#00007F,size:%(size)d" % faces)
        # Triple quotes
        self.StyleSetSpec(stc.STC_P_TRIPLE,
                          "fore:#7F0000,size:%(size)d" % faces)
        # Triple double quotes
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE,
                          "fore:#7F0000,size:%(size)d" % faces)
        # Class name definition
        self.StyleSetSpec(stc.STC_P_CLASSNAME,
                          "fore:#0000FF,underline,size:%(size)d" % faces)
        # Function or method name definition
        self.StyleSetSpec(stc.STC_P_DEFNAME,
                          "fore:#007F7F,size:%(size)d" % faces)
        # Operators
        self.StyleSetSpec(stc.STC_P_OPERATOR, "size:%(size)d" % faces)
        # Identifiers
        self.StyleSetSpec(stc.STC_P_IDENTIFIER,
                          "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # Comment-blocks
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK,
                          "fore:#7F7F7F,size:%(size)d" % faces)
        # End of line where string is not closed
        self.StyleSetSpec(
            stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)

        # caret
        self.SetCaretForeground("RED")
        self.SetCaretWidth(2)

        self.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.Bind(stc.EVT_STC_CHARADDED, self.on_text_changed)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)
        self.restart()

        class OpenDrop(wx.FileDropTarget):
            def __init__(self, app): 
                wx.FileDropTarget.__init__(self)
                self.app = app

            def OnDropFiles(self, x, y, path):
                path = path[0].replace('\\','/')
                if path[-3:]=='.py':
                    self.app.write("run_script('%s')"%path)
                else: self.app.write(path)

        self.SetDropTarget(OpenDrop(self))

        

    def restart(self):
        self.history = []
        self.history_index = 0
        if hasattr(self, 'pc'):
            self.pc.terminate()
            self.AppendText('\n\n')
        self.pc = ProcessConsole()

        self.pc.start(self.write, self.ready, self.goon, self.wait)
        self.getobj = self.pc.getobj
        self.debug = self.pc.debug
        # print(self.pc.getobj('plt', 'list'), 'getobj')
        
    def terminate(self): self.pc.terminate()

    def on_key(self, event):
        if self.AutoCompActive():
            event.Skip()
            return 
        
        obj = event.GetEventObject()
        keycode = event.GetKeyCode()
        
        pos = self.GetCurrentPos()
        col = self.GetColumn(pos)
        
        # print(col)
        # # keycode: 315 up, 317 down.
        # print('press:', keycode)
        
        # press backspace
        if keycode == 8:
            # >>> , bakcspace is disabled
            if col == 4:
                return
        
        # press up
        if keycode == 315:
            hist_len = len(self.history)
            if hist_len>0:
                self.AutoCompShow(0, "".join(self.history[::-1])[1:])
            return 
            
        if keycode == 317:
            return  
        
        # press enter
        if event.GetKeyCode() == 13:
            self.LineEnd()
            newline = self.GetLineText(self.GetCurrentLine())
            newline_code = newline[4:]
            self.pc.write(newline_code)
            self.history.append(';'+newline_code)
         
        # esc   
        if event.GetKeyCode() == 27:
            self.restart()

        event.Skip()

    def on_text_changed(self, event):
        key = event.GetKey()
        
        # press .
        if key == 46:
            self.LineEnd()
            newline = self.GetLineText(self.GetCurrentLine())
            newline = newline[4:-1].split(' ')[-1]
            cont, status = self.pc.getobj('dir', newline)
            if status and len(cont)>0:
                self.AutoCompShow(0, ' '.join(cont))
         
        # press (       
        if key == 40:
            self.LineEnd()
            newline = self.GetLineText(self.GetCurrentLine())
            newline = newline[4:-1].split(' ')[-1]
            cont, status = self.pc.getobj('doc', newline)
            if status and len(cont)>0:
                self.CallTipSetBackground("yellow")
                self.CallTipShow(self.GetCurrentPos(), cont)
        
    def on_mouse(self, event):
        return event.Skip()
    
    def write(self, cont):
        print('write:', cont)
        # self.SetEditable(True)
        wx.CallAfter(self.WriteText, cont)
        # self.SetEditable(False) 
        
    def ready(self):
        # self.SetEditable(True)
        print('ok')
        self.last = self.GetInsertionPoint()

    def goon(self):
        # self.SetEditable(True)
        self.last = self.index('insert')

    def wait(self):
        # self.SetEditable(False)
        print('wait')

    def __del__(self):
        print('i am deleted!')

if __name__ =='__main__':
    app = wx.App()
    frame = wx.Frame(None)
    console = WxConsole(frame)
    frame.Show()
    app.MainLoop()
